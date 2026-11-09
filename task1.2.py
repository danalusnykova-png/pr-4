import multiprocessing
import time
import os


def is_prime(n):
    if n < 2:
        return False

    if n < 4:
        return True

    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5

    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6

    return True


def sum_primes_in_range(start, end):
    pid = os.getpid()
    total_sum = 0
    count = 0

    for number in range(start, end):
        if is_prime(number):
            total_sum += number
            count += 1

    return total_sum, count, pid


def main():
    total_range = 1_000_000
    num_workers = 4

    chunk_size = total_range // num_workers
    ranges = []

    for i in range(num_workers):
        start = i * chunk_size if i > 0 else 2
        end = (i + 1) * chunk_size

        if i == num_workers - 1:
            end = total_range

        ranges.append((start, end))

    print("1. Діапазони обчислення:")

    for start, end in ranges:
        print(f"Від {start} до {end - 1}")

    print("\n2. Послідовне виконання:")

    start_time = time.perf_counter()

    sequential_results = []

    for start, end in ranges:
        result = sum_primes_in_range(start, end)
        sequential_results.append(result)

    seq_time = time.perf_counter() - start_time

    seq_sum = sum(result[0] for result in sequential_results)
    seq_count = sum(result[1] for result in sequential_results)

    print("Сума простих чисел:", seq_sum)
    print("Кількість простих чисел:", seq_count)
    print("PID основного процесу:", os.getpid())
    print(f"Час: {seq_time:.3f} сек")

    print("\n3. Паралельне виконання:")

    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=num_workers) as pool:
        parallel_results = pool.starmap(
            sum_primes_in_range,
            ranges
        )

    par_time = time.perf_counter() - start_time

    par_sum = sum(result[0] for result in parallel_results)
    par_count = sum(result[1] for result in parallel_results)

    for i, result in enumerate(parallel_results, 1):
        total, count, pid = result

        print(f"Частина {i}:")
        print(f"  PID процесу: {pid}")
        print(f"  Кількість простих: {count}")
        print(f"  Сума: {total}")

    print("\n4. Порівняння результатів:")

    print("Послідовна сума:", seq_sum)
    print("Паралельна сума:", par_sum)
    print("Результати однакові:", seq_sum == par_sum)
    print("Кількість простих чисел:", par_count)

    print(f"\nПослідовно: {seq_time:.3f} сек")
    print(f"Паралельно ({num_workers} процеси): {par_time:.3f} сек")

    if par_time > 0:
        speedup = seq_time / par_time
        print(f"Прискорення: {speedup:.2f}x")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

