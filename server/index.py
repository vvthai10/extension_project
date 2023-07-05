'''
Author: vvthai
Description: Run websocket by python: python index.py
'''
import asyncio
import websockets

async def handle_connection(websocket, path):
    print("New client connected!")
    await websocket.send("Hello from server!")

    try:
        while True:
            message = await websocket.recv()
            print("Received message from client:", message)

            # Xử lý dữ liệu nhận được từ client

            # Gửi dữ liệu từ server tới client
            response = "Hello from server!"
            await websocket.send(response)
            
    except websockets.exceptions.ConnectionClosedOK:
        print("Client has disconnected")

start_server = websockets.serve(handle_connection, "localhost", 8082)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
