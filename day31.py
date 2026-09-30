from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi import Header
from fastapi import UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
import sqlite3
import datetime
import secrets
import os
import json

# ===== 数据库：记录每次调用 =====
conn = sqlite3.connect("records.db", check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS 记录 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    时间 TEXT,
    客户 TEXT,
    接口 TEXT,
    内容 TEXT,
    回答 TEXT
)""")
# 老数据库没有"客户"列时，补上
try:
    conn.execute("ALTER TABLE 记录 ADD COLUMN 客户 TEXT")
    conn.commit()
except:
    pass

# 客户表：存每个客户的密钥和用量
conn.execute("""CREATE TABLE IF NOT EXISTS 客户 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE,
    客户名 TEXT,
    次数 INTEGER DEFAULT 0
)""")
conn.commit()

def 保存记录(客户, 接口, 内容, 回答):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO 记录 (时间, 客户, 接口, 内容, 回答) VALUES (?, ?, ?, ?, ?)",
        (now, 客户, 接口, 内容, 回答[:200])  # 回答只存前200字，够看就行
    )
    conn.commit()

# ===== 客户密钥功能 =====
def 生成key():
    return secrets.token_hex(8)  # 生成16位随机密钥

def 验证密钥(请求头):
    """请求头里带了X-Key就返回(客户名, 次数)，没带/无效返回(None, None)"""
    if not 请求头:  # 没带密钥
        return None, None
    row = conn.execute("SELECT 客户名, 次数 FROM 客户 WHERE key=?", (请求头,)).fetchone()
    if not row:  # 密钥不存在
        return None, None
    新次数 = row[1] + 1
    conn.execute("UPDATE 客户 SET 次数=? WHERE key=?", (新次数, 请求头))
    conn.commit()
    return row[0], 新次数

# ===== 创建应用 =====
app = FastAPI()

# 允许网页调用接口（CORS）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 图片上传目录（客户上传的售后照片/商品图都存这里）
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 配置AI
client = OpenAI(
    api_key="sk-在这里填你的API密钥",  # 部署前填真实密钥
    base_url="https://api.deepseek.com"
)

# 请求格式
class 请求(BaseModel):
    内容: str

# ============================================================
# 让AI"动手干活"（Function Calling）：
# 给客服配一个"算价的手"，客户问价时AI自己调用真实算价函数
# ============================================================

# 真实算价函数：整果卖价/斤数/出肉率 → 各规格纯肉价格表
def 算榴莲肉价(price, weight, yield_rate):
    每箱肉 = weight * yield_rate / 100
    肉单价 = price / 每箱肉
    结果 = f"每箱肉{每箱肉:.2f}斤，纯肉单价{肉单价:.2f}元/斤\n"
    for 规格 in [1, 1.5, 2, 2.5, 3, 3.5, 4]:
        成本 = 肉单价 * 规格
        卖价 = 成本 * 1.05          # 提点5%
        结果 += f"{规格}斤装：成本{成本:.2f}元，加5%提点卖{卖价:.2f}元\n"
    return 结果

# 工具说明书（给AI看的）：注意工具名只能用英文/数字/下划线
工具清单 = [
    {
        "type": "function",
        "function": {
            "name": "calc_durian_price",
            "description": "根据整果卖价、斤数、出肉率，算出各规格榴莲纯肉价格。客户问价格时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {"type": "number", "description": "整箱榴莲卖价，单位元"},
                    "weight": {"type": "number", "description": "整箱多少斤"},
                    "yield_rate": {"type": "number", "description": "出肉率百分比，A果填40，B果填30"}
                },
                "required": ["price", "weight", "yield_rate"]
            }
        }
    }
]

# 调AI并处理"AI想用工具"的情况：最多3轮，防止死循环
def 调用AI(messages):
    for _ in range(3):
        r = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=工具清单,
            tool_choice="auto",
        )
        msg = r.choices[0].message
        if not msg.tool_calls:          # AI没想用工具 → 直接给回复
            return msg.content
        # AI想用工具 → 我们替它真正执行！
        messages.append(msg)            # 记下AI的决定
        for 调用 in msg.tool_calls:
            if 调用.function.name == "calc_durian_price":
                参数 = json.loads(调用.function.arguments)
                结果 = 算榴莲肉价(price=参数["price"], weight=参数["weight"], yield_rate=参数["yield_rate"])
                messages.append({"role": "tool", "tool_call_id": 调用.id, "content": 结果})
    return "抱歉，我有点绕晕了，麻烦您再说一次？"

# 流式版AI（打字机效果）：
# 和调用AI一样会判断"AI想不想用工具"（最多3轮），但最后回复是边生成边吐出
def 流式AI(messages):
    """生成器：AI要算价 → 偷偷算完 → 最后回复一个字一个字吐出来"""
    for _ in range(3):
        r = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=工具清单,
            tool_choice="auto",
        )
        msg = r.choices[0].message
        if msg.tool_calls:          # AI想用工具 → 我们替它真正执行！
            messages.append(msg)
            for 调用 in msg.tool_calls:
                if 调用.function.name == "calc_durian_price":
                    参数 = json.loads(调用.function.arguments)
                    结果 = 算榴莲肉价(price=参数["price"], weight=参数["weight"], yield_rate=参数["yield_rate"])
                    messages.append({"role": "tool", "tool_call_id": 调用.id, "content": 结果})
            continue
        # AI直接回复 → 流式吐出来（打字机）
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True,            # 【关键】开启流式
        )
        for 片段 in stream:
            if 片段.choices and 片段.choices[0].delta and 片段.choices[0].delta.content:
                yield 片段.choices[0].delta.content
        return
    yield "抱歉，我有点绕晕了，麻烦您再说一次？"

# ---------- 1. AI客服（售后谈判专家，打字机流式版） ----------
@app.post("/客服")
def 客服(请求: 请求, 请求头: str = Header(None, alias="X-Key")):
    客户名, 次数 = 验证密钥(请求头)
    知识库 = """
你是"夏天榴莲店"的金牌AI客服，同时也是资深售后谈判专家，既护住店铺利润，又让客户觉得被重视。

【店铺信息】
- 价格：金枕榴莲 75元/斤，猫山王 150元/斤
- 发货：下单后48小时内发货，全国包邮

【售后处理（最高优先级，先判断再行动）】
第一步·判断问题真伪：
- 真问题（客户有照片/视频证据、物流异常、果肉明显变质发黑、重量缺斤少两）：按平台流程正常处理——道歉→问清情况→指导客户在平台内申请售后/退款，该补发补发、该全额退全额退。
- 薅羊毛（没有证据、反复纠缠、张嘴就要全额退款、夸张说辞）：启动"阶梯让步话术"，把损失压到最低。

第二步·阶梯让步话术（只用于薅羊毛客户）：
- 第1轮：先共情不硬顶，主动提出"我们承担20%的心意补偿"，语气诚恳，像真心想解决。
- 客户不接受：第2轮加码到30%，并强调"这已经是店里的最高权限了，我特地去申请的"。
- 客户继续闹着要全额：第3轮加到50%，并说明"这是极限了，再高只能请平台介入处理"，把球抛给平台。
- 每轮都让客户感觉"再争取一下还有空间"，一轮只让一步，绝不一次给到底。

【红线（绝对禁止，违反=严重违规）】
1. 绝口不提"微信退款"，不给微信号、不引导加微信，不引导任何线下转账/私下打款。
2. 所有退款补偿一律引导客户"在平台内申请售后"，统一说"平台会按规则处理，您的钱有保障"。
3. 不承诺超出平台规则的口头赔偿。

【回答要求】
1. 先共情再处理，语气真诚、不油腻、不卑微。
2. 每轮回答100字以内，短句，像真实店员说话。
3. 正常咨询（价格/发货/规格）直接给数字，别绕弯。
4. 拿不准的就说"我帮您问问老板"，绝不编造。
"""
    messages = [
        {"role": "system", "content": 知识库},
        {"role": "user", "content": 请求.内容}
    ]
    def 生成():
        if not 客户名:
            yield "❌ 无权限：请先找店主开通密钥"
            return
        全文 = ""
        for 字 in 流式AI(messages):   # 会算价+打字机：客户问价自动算，回复边出字边显示
            全文 += 字
            yield 字
        保存记录(客户名, "客服", 请求.内容, 全文)
    return StreamingResponse(生成(), media_type="text/plain; charset=utf-8")

# ---------- 2. 小红书文案 ----------
@app.post("/文案")
def 文案(请求: 请求, 请求头: str = Header(None, alias="X-Key")):
    客户名, 次数 = 验证密钥(请求头)
    if not 客户名:
        return {"回答": "❌ 无权限：请先找店主开通密钥"}
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": """你是小红书爆款文案专家，写过100篇10万赞笔记，特别擅长把普通商品写出"非买不可"的理由。
【写作公式】
1. 钩子（第1句）：制造好奇或共鸣，让人忍不住停下（如"吃过这家的榴莲，别的都是将就"）
2. 三层理由（正文核心，必须具体有细节，不许空喊"好吃"）：
   - 感官层：口感/香气/入口的具体描写（如"果肉像冰淇淋化在嘴里，核小得可怜"）
   - 品质层：能证明品质的细节（产地、品种、重量、发货新鲜度、坏果承诺）
   - 价值层：为什么比别家/别的水果值（性价比对比、复购场景、送礼体面）
3. 信任背书：一句打消顾虑（如"坏果包赔，放心冲"）
4. 行动号召：结尾给明确动作（"想吃的扣1，我发链接"）
5. 2-3个贴切emoji
【要求】
- 全文120-180字，信息密度高，每个词都有用
- 口语化像朋友安利，但内容扎实：有细节、有理由、有承诺
- 必须围绕用户给的商品/内容写，不许跑题"""},
            {"role": "user", "content": 请求.内容}
        ]
    )
    回答 = response.choices[0].message.content
    保存记录(客户名, "文案", 请求.内容, 回答)
    return {"回答": 回答, "已用次数": 次数}

# ---------- 3. 写周报 ----------
@app.post("/周报")
def 周报(请求: 请求, 请求头: str = Header(None, alias="X-Key")):
    客户名, 次数 = 验证密钥(请求头)
    if not 客户名:
        return {"回答": "❌ 无权限：请先找店主开通密钥"}
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": """你是资深职场人的周报助手。
【输出结构】
1. 本周核心成果：2-3条，每条必须带数字（完成XX件/提升XX%/处理XX单）
2. 关键数据：如果用户给了数字，整理成表格
3. 遇到的问题：1-2条，每条附"已做/待解决"状态
4. 下周计划：3条，按优先级排序
【要求】
- 正式但不官腔，直接能交
- 用户没说数字的地方，用【待补充】标出，不要编数字"""},
            {"role": "user", "content": 请求.内容}
        ]
    )
    回答 = response.choices[0].message.content
    保存记录(客户名, "周报", 请求.内容, 回答)
    return {"回答": 回答, "已用次数": 次数}

# ---------- 4. 数据分析 ----------
@app.post("/数据分析")
def 数据分析(请求: 请求, 请求头: str = Header(None, alias="X-Key")):
    客户名, 次数 = 验证密钥(请求头)
    if not 客户名:
        return {"回答": "❌ 无权限：请先找店主开通密钥"}
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": """你是深耕生鲜零售10年的数据分析师。
请严格按照以下步骤输出分析：
1. 关键数字盘点：列出核心指标（销量结构占比、售后率、潜在客单价），能估算的给估算
2. 深度洞察：结合行业特征（季节波动、损耗、定价带、复购），指出至少3个别人容易忽略的业务问题或机会
3. 可执行建议：每条建议必须写明【怎么做+预期效果+大概成本】
4. 风险提示：指出最可能踩的坑
要求：用大白话，每个结论都要有数字支撑，不要泛泛而谈"""},
            {"role": "user", "content": 请求.内容}
        ]
    )
    回答 = response.choices[0].message.content
    保存记录(客户名, "数据分析", 请求.内容, 回答)
    return {"回答": 回答, "已用次数": 次数}
# ---------- 5. 写标书 ----------
@app.post("/标书")
def 标书(请求: 请求, 请求头: str = Header(None, alias="X-Key")):
    客户名, 次数 = 验证密钥(请求头)
    if not 客户名:
        return {"回答": "❌ 无权限：请先找店主开通密钥"}
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": """你是投标方案撰写专家，写过300+份中标标书。
【输出结构】
1. 项目概述：一句话理解客户需求
2. 需求理解与响应：把客户需求逐条翻译成"我们能做什么"
3. 实施方案：分阶段（准备期/执行期/交付期），每阶段写清做什么、标准是什么
4. 项目团队：3-4个角色（项目经理/执行/质控）
5. 服务承诺：响应时效、质量保障、售后
6. 报价说明：按分项列出（如果用户给了预算就细分，没给就写"待根据实际需求报价"）
【要求】
- 语气专业、可信，用"我方"称呼
- 每部分3-5条，别写废话"""},
            {"role": "user", "content": 请求.内容}
        ]
    )
    回答 = response.choices[0].message.content
    保存记录("标书", 请求.内容, 回答)
    return {"回答": 回答}

# ---------- 6. 榴莲纯肉定价（按店主的成本核算表逻辑） ----------
class 榴莲价请求(BaseModel):
    整果卖价: float   # 每箱整果卖多少钱（元/箱），如450
    斤数: float       # 每箱多少斤，如18
    出肉率: float     # 出肉率（百分比，如43表示43%）
    提点: float = 5  # 提点率%，默认5

@app.post("/榴莲价")
def 榴莲价(请求: 榴莲价请求, 请求头: str = Header(None, alias="X-Key")):
    客户名, 次数 = 验证密钥(请求头)
    if not 客户名:
        return {"回答": "❌ 无权限：请先找店主开通密钥"}
    # 核心计算（和店主Excel表逻辑一致：卖价倒推法）
    整果卖价 = 请求.整果卖价
    斤数 = 请求.斤数
    出肉率 = 请求.出肉率
    提点率 = 请求.提点
    每箱肉 = round(斤数 * 出肉率 / 100, 2)          # 18斤 × 43% = 7.74
    肉单价 = round(整果卖价 / 每箱肉, 2)             # 450 ÷ 7.74 = 58.14
    规格表 = []
    for 规格 in [1, 1.5, 2, 2.5, 3, 3.5, 4]:
        成本价 = round(肉单价 * 规格, 2)
        提点额 = round(成本价 * 提点率 / 100, 2)     # 提点 = 成本价 × 提点率
        卖价 = round(成本价 + 提点额, 2)
        规格表.append((规格, 成本价, 提点额, 卖价))
    # AI给一句定价建议
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": """你是榴莲批发零售的老手。店主按"卖价倒推法"核算果肉定价：
每箱{斤数}斤，整果卖{整果卖价}元/箱，出肉率{出肉率}%，每箱肉{每箱肉}斤，榴莲肉单价{肉单价}元/斤，每单提点{提点率}%（平台+抖音）。
请用大白话给2-3句实在建议：这个定价能不能卖动、要不要调、损耗风险提醒。100字内，别写表格。""".format(斤数=斤数, 整果卖价=整果卖价, 出肉率=出肉率, 每箱肉=每箱肉, 肉单价=肉单价, 提点率=提点率)},
            {"role": "user", "content": "给定价建议"}
        ]
    )
    ai建议 = response.choices[0].message.content
    表 = ["🍈 每箱%d斤 · 整果卖%.0f元 · 出肉率%.0f%% · 每箱肉%.2f斤" % (斤数, 整果卖价, 出肉率, 每箱肉),
          "榴莲肉单价：%.2f 元/斤（提点%.0f%%）" % (肉单价, 提点率),
          "",
          "规格 | 成本价 | 提点%.0f%% | 卖价" % 提点率]
    for 规格, 成本价, 提点额, 卖价 in 规格表:
        表.append("%.1f斤 | %.2f | %.2f | %.2f" % (规格, 成本价, 提点额, 卖价))
    表.append("")
    表.append("【AI建议】" + ai建议)
    回答 = "\n".join(表)
    内容 = "整果卖%.0f元/箱,%d斤,出肉率%.0f%%,提点%.0f%%" % (整果卖价, 斤数, 出肉率, 提点率)
    保存记录(客户名, "榴莲价", 内容, 回答)
    return {"回答": 回答, "已用次数": 次数}

# ---------- 上传图片（客户拍售后照片/商品图，店主在使用记录里查看） ----------
@app.post("/上传图片")
async def 上传图片(file: UploadFile = File(...), 备注: str = Form(""), 请求头: str = Header(None, alias="X-Key")):
    客户名, 次数 = 验证密钥(请求头)
    if not 客户名:
        return {"回答": "❌ 无权限：请先找店主开通密钥"}
    # 1. 校验：必须是图片
    if not file.content_type or not file.content_type.startswith("image/"):
        return {"回答": "❌ 只能上传图片（jpg/png）"}
    扩展名 = os.path.splitext(file.filename or "")[1].lower()
    if 扩展名 not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        return {"回答": "❌ 只支持 jpg / png 图片"}
    # 2. 读取并限制大小（5MB）
    图片数据 = await file.read()
    if len(图片数据) > 5 * 1024 * 1024:
        return {"回答": "❌ 图片超过5MB，压缩后再传"}
    # 3. 存到 uploads 目录（文件名带时间戳+随机，不会重）
    文件名 = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(3) + 扩展名
    with open("uploads/" + 文件名, "wb") as f:
        f.write(图片数据)
    图片链接 = "http://82.156.144.247/uploads/" + 文件名
    内容 = 备注 or "图片"
    保存记录(客户名, "图片", 内容, 图片链接)
    return {"回答": "📷 上传成功！店主会在使用记录里看到", "图片": 图片链接, "已用次数": 次数}

# ---------- 查看使用记录 ----------
@app.get("/记录")
def 记录列表():
    rows = conn.execute("SELECT 时间, 客户, 接口, 内容, 回答 FROM 记录 ORDER BY id DESC LIMIT 20").fetchall()
    记录 = []
    for r in rows:
        图片 = r[4] if r[4] and r[4].startswith("http") else ""
        记录.append({"时间": r[0], "客户": r[1], "接口": r[2], "内容": r[3], "图片": 图片})
    return {"记录": 记录}

# ---------- 7. 开通密钥（店主用） ----------
class 开通请求(BaseModel):
    客户名: str

@app.post("/开通")
def 开通(开通请求: 开通请求):
    key = 生成key()
    conn.execute("INSERT INTO 客户 (key, 客户名, 次数) VALUES (?, ?, 0)", (key, 开通请求.客户名))
    conn.commit()
    return {"客户名": 开通请求.客户名, "key": key, "提示": "把key发给客户，客户在工具箱里填上就能用"}

# ---------- 8. 客户列表（店主看谁在用、用了多少） ----------
@app.get("/客户列表")
def 客户列表():
    rows = conn.execute("SELECT 客户名, key, 次数 FROM 客户").fetchall()
    return {"客户": [{"客户名": r[0], "key": r[1], "次数": r[2]} for r in rows]}

# 首页
@app.get("/")
def 首页():
    return {"消息": "AI接口超市（密钥版）：10个接口：/客服 /文案 /周报 /数据分析 /标书 /榴莲价 /上传图片 /开通 /客户列表 /记录"}

# 网页版工具箱（新增！客户打开这个网址就能用）
@app.get("/工具", response_class=HTMLResponse)
def 工具页面():
    with open("index.html", encoding="utf-8") as f:
        return f.read()

# 启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
