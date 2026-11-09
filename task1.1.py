import threading
import time


def download_simulation(file_name, size_mb):
    thread_name = threading.current_thread().name

    print(
        f"[{thread_name}] Початок завантаження "
        f"'{file_name}' ({size_mb} MB)"
    )

    time.sleep(size_mb * 0.3)

    print(f"[{thread_name}] Завантажено '{file_name}'")

    return {
        "file": file_name,
        "size": size_mb,
        "thread": thread_name
    }


class MonitorThread(threading.Thread):
    def __init__(self, interval=0.5):
        super().__init__(name="Monitor", daemon=True)
        self.interval = interval
        self.active_downloads = 0
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            self.active_downloads = max(
                0, threading.active_count() - 2
            )

            print(
                f"[Monitor] Активних потоків: "
                f"{threading.active_count()}, "
                f"завантажень: {self.active_downloads}"
            )

            self._stop_event.wait(self.interval)

    def stop(self):
        self._stop_event.set()


def main():
    files = [
        ("data.csv", 2.5),
        ("report.pdf", 1.0),
        ("image.png", 0.5),
        ("archive.zip", 4.0),
        ("log.txt", 0.3)
    ]

    print("1. Паралельне завантаження файлів:\n")

    monitor = MonitorThread()
    monitor.start()

    threads = []

    for file_name, size_mb in files:
        thread = threading.Thread(
            target=download_simulation,
            args=(file_name, size_mb),
            name=f"Download-{file_name}"
        )

        threads.append(thread)

    start = time.perf_counter()

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    parallel_time = time.perf_counter() - start

    monitor.stop()
    monitor.join()

    print(
        f"\nУсі файли завантажено за "
        f"{parallel_time:.2f} сек"
    )

    print("\n2. Послідовне завантаження файлів:\n")

    start = time.perf_counter()

    for file_name, size_mb in files:
        download_simulation(file_name, size_mb)

    sequential_time = time.perf_counter() - start

    print(
        f"\nПослідовне виконання: "
        f"{sequential_time:.2f} сек"
    )

    print("\n3. Порівняння результатів:")
    print(f"Паралельно: {parallel_time:.2f} сек")
    print(f"Послідовно: {sequential_time:.2f} сек")

    speedup = sequential_time / parallel_time

    print(f"Прискорення: {speedup:.2f} рази")


if __name__ == "__main__":
    main()

