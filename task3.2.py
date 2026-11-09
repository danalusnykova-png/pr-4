import threading
import queue
import time
import random


class Task:
    def __init__(self, task_id, data, priority=0):
        self.task_id = task_id
        self.data = data
        self.priority = priority
        self.created_at = time.time()

    def __repr__(self):
        return f"Task(id={self.task_id}, data='{self.data}')"


def producer(task_queue, num_tasks, producer_id):
    for i in range(num_tasks):
        task = Task(
            task_id=producer_id * 100 + i,
            data=f"Дані від виробника {producer_id}, пакет {i}",
            priority=random.randint(1, 5)
        )

        task_queue.put(task)

        print(
            f"[Виробник-{producer_id}] Створено {task}"
        )

        time.sleep(random.uniform(0.1, 0.3))


def consumer(task_queue, consumer_id, results, results_lock):
    while True:
        try:
            task = task_queue.get(timeout=2)

        except queue.Empty:
            print(
                f"[Споживач-{consumer_id}] "
                f"Черга порожня, завершення"
            )
            break

        if task is None:
            task_queue.task_done()
            print(f"[Споживач-{consumer_id}] Завершив роботу")
            break

        try:
            start = time.perf_counter()

            print(
                f"[Споживач-{consumer_id}] "
                f"Обробляє завдання {task.task_id}"
            )

            time.sleep(random.uniform(0.2, 0.5))

            elapsed = time.perf_counter() - start

            with results_lock:
                results.append({
                    "task_id": task.task_id,
                    "consumer": consumer_id,
                    "time": elapsed
                })

            print(
                f"[Споживач-{consumer_id}] "
                f"Завдання {task.task_id} виконано"
            )

        finally:
            task_queue.task_done()


def producer_consumer_demo():
    task_queue = queue.Queue(maxsize=5)
    results = []
    results_lock = threading.Lock()

    num_producers = 2
    num_consumers = 3
    tasks_per_producer = 5

    producers = []
    consumers = []

    for i in range(num_consumers):
        thread = threading.Thread(
            target=consumer,
            args=(task_queue, i + 1, results, results_lock)
        )

        consumers.append(thread)
        thread.start()

    for i in range(num_producers):
        thread = threading.Thread(
            target=producer,
            args=(task_queue, tasks_per_producer, i + 1)
        )

        producers.append(thread)
        thread.start()

    for thread in producers:
        thread.join()

    task_queue.join()

    for i in range(num_consumers):
        task_queue.put(None)

    for thread in consumers:
        thread.join()

    total_tasks = num_producers * tasks_per_producer

    if results:
        average_time = sum(
            item["time"] for item in results
        ) / len(results)
    else:
        average_time = 0

    print("\n=== Результати Producer-Consumer ===")
    print("Створено завдань:", total_tasks)
    print("Оброблено завдань:", len(results))
    print(f"Середній час обробки: {average_time:.3f} сек")
    print("Максимальний розмір черги:", task_queue.maxsize)
    print("Залишилось у черзі:", task_queue.qsize())


def deadlock_demo():
    lock_a = threading.Lock()
    lock_b = threading.Lock()
    deadlock_detected = threading.Event()

    def worker_1():
        lock_a.acquire()
        print("[Worker-1] Захопив Lock A")

        time.sleep(0.1)

        acquired = lock_b.acquire(timeout=1)

        if not acquired:
            print(
                "[Worker-1] ДЕДЛОК: "
                "не вдалося захопити Lock B!"
            )
            deadlock_detected.set()
            lock_a.release()
            return

        print("[Worker-1] Захопив Lock B")

        lock_b.release()
        lock_a.release()

    def worker_2():
        lock_b.acquire()
        print("[Worker-2] Захопив Lock B")

        time.sleep(0.1)

        acquired = lock_a.acquire(timeout=1)

        if not acquired:
            print(
                "[Worker-2] ДЕДЛОК: "
                "не вдалося захопити Lock A!"
            )
            deadlock_detected.set()
            lock_b.release()
            return

        print("[Worker-2] Захопив Lock A")

        lock_a.release()
        lock_b.release()

    def safe_worker_1():
        with lock_a:
            print("[Safe-1] Захопив Lock A")

            time.sleep(0.1)

            with lock_b:
                print("[Safe-1] Захопив Lock B")
                print("[Safe-1] Роботу виконано")

    def safe_worker_2():
        with lock_a:
            print("[Safe-2] Захопив Lock A")

            time.sleep(0.1)

            with lock_b:
                print("[Safe-2] Захопив Lock B")
                print("[Safe-2] Роботу виконано")

    print("=== Спроба з потенційним дедлоком ===")

    t1 = threading.Thread(target=worker_1)
    t2 = threading.Thread(target=worker_2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    if deadlock_detected.is_set():
        print(
            ">>> Виявлено взаємне очікування замків!"
        )
        print(
            ">>> Timeout запобіг зависанню програми."
        )
    else:
        print(">>> Дедлок цього разу не виник.")

    print("\n=== Безпечна версія ===")

    t3 = threading.Thread(target=safe_worker_1)
    t4 = threading.Thread(target=safe_worker_2)

    t3.start()
    t4.start()

    t3.join()
    t4.join()

    print(">>> Обидва потоки завершили роботу без дедлоку.")


def main():
    print("=" * 60)
    print("=== Паттерн Producer-Consumer ===")
    print("=" * 60)

    producer_consumer_demo()

    print("\n" + "=" * 60)
    print("=== Демонстрація дедлоку ===")
    print("=" * 60)

    deadlock_demo()


if __name__ == "__main__":
    main()

