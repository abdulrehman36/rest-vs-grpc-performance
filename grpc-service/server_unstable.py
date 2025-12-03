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
            return echo_pb2.EchoResponse()  # type: ignore

 
        data = request.data
        size_bytes = len(data)
        ts = datetime.utcnow().isoformat() + "Z"

        return echo_pb2.EchoResponse(  # type: ignore
            data=data,
            size_bytes=size_bytes,
            timestamp=ts,
        )


async def serve():
    server = aio.server()
    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoService(), server)
    server.add_insecure_port("[::]:50052")
    await server.start()
    print("Unstable gRPC server listening on port 50052")
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())