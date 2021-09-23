# import asyncio
# from websockets import connect

# async def hello(uri):
#     async with connect(uri) as websocket:
#         await websocket.send("Hello world!")
#         await websocket.recv()

# asyncio.run(hello("ws://localhost:8765"))

import asyncio
import datetime
import random
import json
import websockets


class SnakeServer():

    def __init_(self, host='127.0.0.1', port='6666'):
        self.host_ip = host
        self.port = port
        self.connected_clients = {}
        self.sessions = {}
        self.max_clients = 100

    async def on_connect(self, websocket, *args, **kwargs) -> tuple:
        """
        """
        client_id = 0       
        if len(self.connected_clients) < self.max_clients:
            while(client_id := random.randint(1, self.max_clients)):
                if client_id not in self.connected_clients.keys():
                    break
        else:
            response = {'error': f'The maximum number of connections ({self.max_clients}) has been reached.'}
            websocket.send(json.dumps(response))
            await websocket.close(code=1000, reason=response)

        if client_id != 0:
            self.clients[client_id] = ... # FIXME CO TUTAJ ? ? czy raczej zbior a nie slownik

        return client_id
    
    async def on_disconnect(self, websocket, client_id):
        """
        """
        try:
            self.connected_clients.pop(client_id)
            await websocket.close(code=1000, reason='')
        except KeyError:
            # logger.warning(f"'{client_id}' is not connected")
            await websocket.send(json.dumps({"result":False}))
            return

    async def server_handler(self, websocket, *args, **kwargs):

        try:
            async for message in websocket:
                
                client_id, request, data = self.parse_message(message)

                if request == "connect":
                    client_id = await self.on_connect(websocket) # FIXME REMOVE RET VAL
                elif request == "disconnect":
                    await self.on_disconnect(websocket, client_id)
                elif request == 'start':
                    pass
                elif request == 'game':
                    pass

                elif request == "echo":
                    await websocket.send(json.dumps({"result":message}))

                else:
                    # send response and disconnect
                    await self.respond(websocket, client_id, request, data)
        except websockets.exceptions.ConnectionClosedError as cce:
            pass
        finally:
            await websocket.close(code=1000, reason='')

    
    @staticmethod
    def parse_message(message):
        message = json.loads(message)
        request = message['request']
        client_id = 0
        data = {}

        if request != 'connect':
            client_id = message['client_id']
            data = message['data']

        return client_id, request, data

    
    def mainloop(self):
        self.loop.run_until_complete(websockets.serve(self.server_handler, self.host_ip, self.port))
        self.loop.run_forever()


# await asyncio.sleep(10)
   


def main():
    game_server = SnakeServer()
    game_server.mainloop()


if __name__ == "__main__":
    main()
