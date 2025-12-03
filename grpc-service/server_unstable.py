import asyncio
import random
from datetime import datetime

import grpc
from grpc import aio

import echo_pb2
import echo_pb2_grpc


class EchoService(echo_pb2_grpc.EchoServiceServicer):
    async def Echo(self, request, context):
        # 20% simulated failure
        if random.random() < 0.2:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Simulated server failure")
            # return an "empty" reply
            return echo_pb2.EchoReply() # type: ignore

        data = request.data
        size = len(data)
        ts = datetime.utcnow().isoformat() + "Z"

        return echo_pb2.EchoReply( # type: ignore
            payload=data,
            size_bytes=size,
            timestamp=ts,
        )


async def serve() -> None:
    server = aio.server()
    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoService(), server)

    listen_addr = "[::]:50052"
    server.add_insecure_port(listen_addr)
    print(f"Unstable gRPC server listening on {listen_addr}")

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())