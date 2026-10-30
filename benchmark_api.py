
import requests
import time
import statistics

URL = "http://127.0.0.1:8000/mcqs/evaluate"

payload = {
    "skill": "Python",
    "answers": [
        "def",
        "Dictionary"
    ]
}

total_requests = 30
response_times = []
successful_requests = 0

for i in range(total_requests):

    start_time = time.perf_counter()

    try:
        response = requests.post(
            URL,
            json=payload,
            timeout=10
        )

        end_time = time.perf_counter()

        elapsed_time = (end_time - start_time) * 1000

        if response.status_code == 200:
            successful_requests += 1
            response_times.append(elapsed_time)

        print(
            f"Request {i + 1}: "
            f"{response.status_code} - {elapsed_time:.2f} ms"
        )

    except requests.RequestException as error:
        print(f"Request {i + 1} failed: {error}")


if response_times:
    print("\n--- Benchmark Results ---")
    print("Successful requests:", successful_requests)
    print("Total requests:", total_requests)

    print(
        "Success rate:",
        f"{successful_requests / total_requests * 100:.2f}%"
    )

    print(
        "Average response time:",
        f"{statistics.mean(response_times):.2f} ms"
    )

    print(
        "Minimum response time:",
        f"{min(response_times):.2f} ms"
    )

    print(
        "Maximum response time:",
        f"{max(response_times):.2f} ms"
    )
else:
    print("No successful requests. Check your API server.")
