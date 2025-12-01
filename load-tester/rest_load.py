import argparse
import asyncio
import httpx
import time
import random
import string

async def worker(client, url, payload, duration, results):
    end_time = time.time() + duration
    count = 0
    total_latency = 0.0
    errors = 0

    while time.time() < end_time:
        try:
            start = time.time()
            r = await client.post(url, json={"payload": payload})
            latency = time.time() - start

            if r.status_code == 200:
                count += 1
                total_latency += latency
            else:
                errors += 1

        except Exception:
            errors += 1

    results.append((count, total_latency, errors))


async def run_test(concurrency, duration, payload_size):
    url = "http://localhost:5001/echo"

    # generate random payload
    payload = ''.join(random.choices(string.ascii_letters + string.digits, k=payload_size))

    async with httpx.AsyncClient() as client:
        results = []

        tasks = [
            worker(client, url, payload, duration, results)
            for _ in range(concurrency)
        ]

        await asyncio.gather(*tasks)

    total_requests = sum(r[0] for r in results)
    total_latency = sum(r[1] for r in results)
    total_errors = sum(r[2] for r in results)

    avg_latency_ms = (total_latency / total_requests * 1000) if total_requests > 0 else 0
    throughput = total_requests / duration

    print("=== RESULTS ===")
    print(f"Concurrency: {concurrency}")
    print(f"Payload size: {payload_size} bytes")
    print(f"Duration: {duration}s")
    print(f"Total Requests: {total_requests}")
    print(f"Throughput: {throughput:.2f} req/s")
    print(f"Average Latency: {avg_latency_ms:.2f} ms")
    print(f"Errors: {total_errors}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, required=True)
    parser.add_argument("--duration", type=int, default=5)
    parser.add_argument("--payload", type=int, default=128)

    args = parser.parse_args()

    asyncio.run(run_test(args.concurrency, args.duration, args.payload))