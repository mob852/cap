import asyncio
import logging
from aiortc import RTCPeerConnection, VideoStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling

logging.basicConfig(level=logging.DEBUG)

async def run(pc, signaling):
    try:
        print("Connecting to signaling server...")
        await signaling.connect()

        print("Creating and sending offer...")
        await pc.setLocalDescription(await pc.createOffer())
        await signaling.send(pc.localDescription)

        print("Waiting for answer...")
        answer = await signaling.receive()
        print("Answer received:", answer)
        await pc.setRemoteDescription(answer)
        print("Connection established!")
    except Exception as e:
        print(f"Error in sender signaling process: {e}")
    finally:
        await signaling.close()

if __name__ == "__main__":
    signaling = TcpSocketSignaling("0.0.0.0", 9000)
    pc = RTCPeerConnection()

    asyncio.run(run(pc, signaling))
