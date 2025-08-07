import time
import json
from datasketch import HyperLogLog

LOG_FILE = "lms-stage-access.log"

def extract_ips(filepath):
    with open(filepath, "r") as file:
        for line in file:
            try:
                data = json.loads(line)
                ip = data.get("remote_addr")
                if ip:
                    yield ip
            except json.JSONDecodeError:
                continue

def exact_count(filepath):
    start = time.time()
    unique_ips = set(extract_ips(filepath))
    duration = time.time() - start
    return len(unique_ips), duration

def approximate_count(filepath):
    start = time.time()
    hll = HyperLogLog(p=14)
    for ip in extract_ips(filepath):
        hll.update(ip.encode("utf-8"))
    duration = time.time() - start
    return int(hll.count()), duration

if __name__ == "__main__":
    print("Обробка лог-файлу:", LOG_FILE)

    exact, time_exact = exact_count(LOG_FILE)
    print(f"Точна кількість унікальних IP: {exact}")
    print(f"Час виконання (set): {time_exact:.4f} секунд")

    approx, time_approx = approximate_count(LOG_FILE)
    print(f"Наближена кількість унікальних IP (HyperLogLog): {approx}")
    print(f"Час виконання (HyperLogLog): {time_approx:.4f} секунд")

    error = abs(exact - approx) / exact * 100 if exact else 0
    print(f"Похибка: {error:.2f}%")