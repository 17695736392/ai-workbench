# -*- coding: utf-8 -*-
# Day45 教学：监控 + 告警
# 学什么：让电脑定时"体检"你的产品——接口活着吗？服务器磁盘够吗？进程在跑吗？
#        异常时自动告诉你。这是"AI工具人"里最实用的一环：不用你天天手动去看。
# 怎么用：直接双击 运行Day45教学.bat，或者 python 这个文件

import urllib.request
import urllib.parse
import json
import datetime
import paramiko
import os

# ============ 配置 ============
服务器 = "http://82.156.144.247"
SSH地址 = "82.156.144.247"
SSH用户 = "ubuntu"
SSH密码 = "Xiatian000"

# 【进阶】想异常时推送到手机？去申请一个Server酱/钉钉群机器人，把网址填这里：
告警网址 = ""   # 例："https://sctapi.ftqq.com/你的KEY.send"

# ============ 检查工具箱 ============
def 探首页():
    """不带密钥也能探：只要首页200且有'接口'字样，就说明服务活着"""
    with urllib.request.urlopen(服务器 + "/", timeout=10) as resp:
        文本 = resp.read().decode("utf-8")
    assert "接口" in 文本, "首页没有接口清单"
    return "200 正常：" + 文本[:40]

def 探客服():
    """【探针技巧】不带密钥发请求 → 返回'无权限'=接口活着，而且不烧AI的token！
    千万别直接带密钥测，那会真调用AI烧钱"""
    地址 = 服务器 + "/" + urllib.parse.quote("客服")
    req = urllib.request.Request(地址, data='{"内容":"hi"}'.encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        文本 = resp.read().decode("utf-8")
    assert "无权限" in 文本, "客服探针异常"
    return "路由活着（无密钥探针，不烧钱）"

def 探军团():
    """同上：军团接口只探'有没有',不真跑AI"""
    地址 = 服务器 + "/" + urllib.parse.quote("军团")
    req = urllib.request.Request(地址, data='{"内容":"hi"}'.encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        数据 = json.loads(resp.read().decode("utf-8"))
    assert "无权限" in 数据.get("回答", ""), "军团探针异常"
    return "路由活着（不烧钱）"

def 探服务器():
    """SSH连服务器：看进程在不在、磁盘够不够、日志有没有报错"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH地址, username=SSH用户, password=SSH密码, timeout=10)

    # 1. 进程：uvicorn 应该有一个在跑
    _, out, _ = ssh.exec_command("ps aux | grep uvicorn | grep -v grep | wc -l")
    进程数 = int(out.read().decode().strip())
    # 2. 磁盘：根分区使用率
    _, out, _ = ssh.exec_command("df -h / | tail -1 | awk '{print $5}'")
    磁盘 = out.read().decode().strip()
    # 3. 日志：最近有没有 ERROR/Traceback
    _, out, _ = ssh.exec_command("grep -cE 'ERROR|Traceback' /home/ubuntu/app/server.log | tail -1")
    报错数 = out.read().decode().strip()
    ssh.close()

    assert 进程数 >= 1, f"uvicorn进程没了（当前{进程数}个）"
    return f"进程{进程数}个 / 磁盘{磁盘} / 日志报错{报错数}行"

# ============ 执行体检 ============
def 主程序():
    print("=" * 40)
    print("🩺 工具箱体检报告", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 40)

    结果们 = [
        ("工具箱首页", 探首页),
        ("客服接口", 探客服),
        ("军团接口", 探军团),
        ("云服务器", 探服务器),
    ]

    问题们 = []
    for 名称, 检查 in 结果们:
        try:
            详情 = 检查()
            print(f"✅ {名称}：{详情}")
        except Exception as e:
            print(f"❌ {名称}：异常！{e}")
            问题们.append(f"{名称}：{e}")

    # 把报告存下来，方便回看
    日志路径 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "监控日志.txt")
    with open(日志路径, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
        for 名称, 检查 in 结果们:
            try:
                f.write(f"✅ {名称}\n")
            except Exception:
                pass
        if 问题们:
            f.write("❌ " + " | ".join(问题们) + "\n")

    # 告警：有问题时，醒目提示 + （可选）推送到手机
    if 问题们:
        print()
        print("🚨🚨🚨 发现问题了！")
        for 问题 in 问题们:
            print("  -", 问题)
        print()
        print("【检查建议】")
        print("  1. 首页/接口挂了 → SSH上服务器看：tail -30 /home/ubuntu/app/server.log")
        print("  2. 进程没了 → 重启：cd /home/ubuntu/app && sudo killall uvicorn; setsid nohup ./aienv/bin/uvicorn day31:app --host 0.0.0.0 --port 80 > server.log 2>&1 &")
        print("  3. 磁盘快满 → 清理：du -sh /home/ubuntu/app/* 找出大文件")
        if 告警网址:
            try:
                import urllib.parse
                消息 = urllib.parse.quote("工具箱出问题：" + " | ".join(问题们))
                urllib.request.urlopen(告警网址 + "?title=工具箱异常&desp=" + 消息, timeout=10)
                print("  📱 已推送告警到手机")
            except Exception as e:
                print("  推送失败：", e)
    else:
        print()
        print("🎉 一切正常！可以放心干活。")

if __name__ == "__main__":
    主程序()
