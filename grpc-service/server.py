import asyncio
from datetime import datetime

import grpc
from grpc import aio

import echo_pb2
import echo_pb2_grpc


class EchoService(echo_pb2_grpc.EchoServiceServicer):
    async def Echo(self, request, context):
        data = request.data
        size_bytes = len(data)
        ts = datetime.utcnow().isoformat() + "Z"

        return echo_pb2.EchoResponse( # type: ignore
            data=data,
            size_bytes=size_bytes,
            timestamp=ts,
        )


async def serve():
    server = aio.server()
    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoService(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("gRPC server listening on port 50051")
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())