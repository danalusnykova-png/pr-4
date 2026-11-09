import threading
import time
import random


class ConnectionPool:
    def __init__(self, max_connections=3):
        self._semaphore = threading.Semaphore(max_connections)
        self._lock = threading.Lock()
        self.max_connections = max_connections
        self.active_connections = 0
        self.total_served = 0
        self.peak_connections = 0

    def acquire_connection(self, client_name):
        print(f"[{client_name}] Запит на з'єднання...")

        self._semaphore.acquire()

        with self._lock:
            self.active_connections += 1

            if self.active_connections > self.peak_connections:
                self.peak_connections = self.active_connections

            print(
                f"[{client_name}] З'єднання отримано. "
                f"Активних: {self.active_connections}"
            )

    def release_connection(self, client_name):
        with self._lock:
            self.active_connections -= 1
            self.total_served += 1

            print(
                f"[{client_name}] З'єднання звільнено. "
                f"Активних: {self.active_connections}"
            )

        self._semaphore.release()

    def get_stats(self):
        with self._lock:
            return {
                "max": self.max_connections,
                "active": self.active_connections,
                "total_served": self.total_served,
                "peak": self.peak_connections
            }


def client_task(pool, client_name, ready_event):
    print(f"[{client_name}] Очікує готовності сервера")

    ready_event.wait()

    pool.acquire_connection(client_name)

    try:
        work_time = random.uniform(0.5, 2.0)

        print(
            f"[{client_name}] Працює {work_time:.1f} сек"
        )

        time.sleep(work_time)

    finally:
        pool.release_connection(client_name)


def main():
    pool = ConnectionPool(max_connections=3)
    ready_event = threading.Event()
    num_clients = 10

    threads = []

    print("=== Запуск клієнтських потоків ===\n")

    for i in range(num_clients):
        thread = threading.Thread(
            target=client_task,
            args=(pool, f"Client-{i:02d}", ready_event)
        )

        threads.append(thread)
        thread.start()

    time.sleep(0.5)

    print("\n>>> Сервер готовий!")
    print(">>> Усі клієнти починають роботу.\n")

    ready_event.set()

    for thread in threads:
        thread.join()

    stats = pool.get_stats()

    print("\n=== Статистика пулу ===")
    print(f"Макс. з'єднань: {stats['max']}")
    print(f"Активних з'єднань: {stats['active']}")
    print(f"Обслуговано клієнтів: {stats['total_served']}")
    print(f"Пікове навантаження: {stats['peak']}")

    print("\n=== Перевірка обмежень ===")

    if stats["peak"] <= stats["max"]:
        print("Обмеження з'єднань не перевищено")
    else:
        print("Помилка: перевищено кількість з'єднань")

    if stats["total_served"] == num_clients:
        print("Усі клієнти успішно обслуговані")
    else:
        print("Не всі клієнти були обслуговані")


if __name__ == "__main__":
    main()

