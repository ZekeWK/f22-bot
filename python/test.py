from asyncio import run
import websockets.client
from secret import TOKEN
import json


to_send = json.dumps({ "seq": 1, "action": "authentication_challenge", "data": { "token": TOKEN}})

async def main():
    uri = "wss://mattermost.fysiksektionen.se:443/api/v4/websocket"
    async with websockets.client.connect(uri) as websocket:
        await websocket.send(to_send)
        while True:
            print(await websocket.recv())

if __name__ == "__main__":
    run(main())
