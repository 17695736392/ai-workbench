# ============================================
# Day 35 教学：定时任务（闹钟）
# 用 schedule 库：让代码"到点自动干活"
# 生意版：以后可以做"每天早上8点自动出报表"
# ============================================
import schedule
import time
import datetime

def 心跳():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] 心跳正常：服务器活着，工具箱在线")

def 干活():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] ⏰ 到点了！自动干活：生成今日销量报告")

# 设定闹钟（这是核心，就3行）
schedule.every(2).seconds.do(心跳)    # 每2秒心跳一次
schedule.every(10).seconds.do(干活)   # 每10秒干一次活
# 以后想"每天早8点"，就改成：schedule.every().day.at("08:00").do(干活)

print("定时任务启动！观察下面两种输出：")
print("  - 每2秒：心跳")
print("  - 每10秒：自动干活")
print("（演示跑30秒自动结束，想提前停就按 Ctrl+C）")
print("=" * 40)

结束时间 = time.time() + 30          # 演示30秒
while time.time() < 结束时间:
    schedule.run_pending()            # 关键：检查有没有到点的任务，到点就执行
    time.sleep(1)                     # 每1秒检查一次

print()
print("演示结束！")
print("核心就2句：schedule.every(X).seconds.do(要干的活)  +  schedule.run_pending()")
