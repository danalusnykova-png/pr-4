import threading
import time
import random


class BankAccount:
    def __init__(self, balance=0.0):
        self.balance = balance
        self.transaction_count = 0

    def deposit(self, amount):
        current = self.balance

        time.sleep(random.uniform(0.0001, 0.001))

        self.balance = current + amount
        self.transaction_count += 1

    def withdraw(self, amount):
        current = self.balance

        time.sleep(random.uniform(0.0001, 0.001))

        if current >= amount:
            self.balance = current - amount
            self.transaction_count += 1
            return True

        return False


class SafeBankAccount:
    def __init__(self, balance=0.0):
        self.balance = balance
        self.transaction_count = 0
        self._lock = threading.Lock()

    def deposit(self, amount):
        with self._lock:
            current = self.balance

            time.sleep(random.uniform(0.0001, 0.001))

            self.balance = current + amount
            self.transaction_count += 1

    def withdraw(self, amount):
        with self._lock:
            current = self.balance

            time.sleep(random.uniform(0.0001, 0.001))

            if current >= amount:
                self.balance = current - amount
                self.transaction_count += 1
                return True

            return False


def run_transactions(account, num_deposits, num_withdrawals):
    num_threads = 10
    threads = []

    def worker(index):
        deposits = (
            num_deposits // num_threads
            + (1 if index < num_deposits % num_threads else 0)
        )

        withdrawals = (
            num_withdrawals // num_threads
            + (1 if index < num_withdrawals % num_threads else 0)
        )

        for i in range(max(deposits, withdrawals)):
            if i < deposits:
                account.deposit(50.0)

            if i < withdrawals:
                account.withdraw(50.0)

    for i in range(num_threads):
        thread = threading.Thread(
            target=worker,
            args=(i,),
            name=f"Worker-{i + 1}"
        )
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def main():
    initial_balance = 1000.0
    num_deposits = 100
    deposit_amount = 50.0
    num_withdrawals = 100
    withdraw_amount = 50.0

    expected_balance = (
        initial_balance
        + num_deposits * deposit_amount
        - num_withdrawals * withdraw_amount
    )

    print("=== Тест без синхронізації ===")

    unsafe_account = BankAccount(initial_balance)

    start = time.perf_counter()

    run_transactions(
        unsafe_account,
        num_deposits,
        num_withdrawals
    )

    unsafe_time = time.perf_counter() - start

    print(f"Очікуваний баланс: {expected_balance:.2f}")
    print(f"Фактичний баланс: {unsafe_account.balance:.2f}")
    print(
        f"Кількість транзакцій: "
        f"{unsafe_account.transaction_count}"
    )
    print(
        "Баланс правильний:",
        unsafe_account.balance == expected_balance
    )
    print(f"Час виконання: {unsafe_time:.3f} сек")

    print("\n=== Тест із синхронізацією (Lock) ===")

    safe_account = SafeBankAccount(initial_balance)

    start = time.perf_counter()

    run_transactions(
        safe_account,
        num_deposits,
        num_withdrawals
    )

    safe_time = time.perf_counter() - start

    print(f"Очікуваний баланс: {expected_balance:.2f}")
    print(f"Фактичний баланс: {safe_account.balance:.2f}")
    print(
        f"Кількість транзакцій: "
        f"{safe_account.transaction_count}"
    )
    print(
        "Баланс правильний:",
        safe_account.balance == expected_balance
    )
    print(f"Час виконання: {safe_time:.3f} сек")

    print("\n=== Порівняння результатів ===")

    print(
        f"Без Lock: {unsafe_account.balance:.2f}"
    )
    print(
        f"З Lock: {safe_account.balance:.2f}"
    )
    print(f"Очікуваний баланс: {expected_balance:.2f}")
    print(
        f"Різниця без Lock: "
        f"{unsafe_account.balance - expected_balance:.2f}"
    )
    print(
        f"Різниця з Lock: "
        f"{safe_account.balance - expected_balance:.2f}"
    )


if __name__ == "__main__":
    main()

