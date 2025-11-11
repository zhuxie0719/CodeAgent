import threading

counter = 0


def worker():
    global counter
    for _ in range(1000):
        # 无锁的共享变量写入
        counter += 1  # threading_race_condition: high


def run():
    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()



