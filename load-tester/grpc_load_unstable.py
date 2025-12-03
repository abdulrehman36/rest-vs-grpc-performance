import argparse
import asyncio
import time
import random
import string
import sys

from grpc import aio

# allow imports from grpc-service
sys.path.append("../grpc-service")
import echo_pb2 # type: ignore
import echo_pb2_grpc # type: ignore


async def worker(stub, payload_bytes, duration, results):
    end_time = time.time() + duration
    count = 0
    total_latency = 0.0
    errors = 0

    while time.time() < end_time:
        try:
            start = time.time()
            resp = await stub.Echo(echo_pb2.EchoRequest(data=payload_bytes))
            latency = time.time() - start

            # simple success check; resp has data, size_bytes, timestamp
            count += 1
            total_latency += latency
        except Exception:
            errors += 1

    results.append((count, total_latency, errors))


async def run_test(concurrency, duration, payload_size):
    # generate same random payload, then encode to bytes
    payload_str = ''.join(
        random.choices(string.ascii_letters + string.digits, k=payload_size)
    )
    payload_bytes = payload_str.encode("utf-8")

    async with aio.insecure_channel("localhost:50052") as channel:
        stub = echo_pb2_grpc.EchoServiceStub(channel)

        results = []
        tasks = [
            worker(stub, payload_bytes, duration, results)
            for _ in range(concurrency)
        ]

        await asyncio.gather(*tasks)

    total_requests = sum(r[0] for r in results)
    total_latency = sum(r[1] for r in results)
    total_errors = sum(r[2] for r in results)

    avg_latency_ms = (total_latency / total_requests * 1000) if total_requests > 0 else 0
    throughput = total_requests / duration if duration > 0 else 0

    print("=== RESULTS (gRPC) ===")
    print(f"Concurrency: {concurrency}")
    print(f"Total Requests: {total_requests}")
    print(f"Throughput: {throughput:.2f} req/s")
    print(f"Average Latency: {avg_latency_ms:.2f} ms")
    print(f"Errors: {total_errors}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, required=True)
    parser.add_argument("--duration", type=int, default=10)
    parser.add_argument("--payload", type=int, default=128)
    args = parser.parse_args()

    asyncio.run(run_test(args.concurrency, args.duration, args.payload))