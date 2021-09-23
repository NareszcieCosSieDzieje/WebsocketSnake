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
import logging
import websockets

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from logic import initialize_game_state


host_ip = 'localhost'
port = '6789'
connected_clients = {} # client id -> websocket # URL?? FIXME
clients_in_sessions: dict[int, int] = {} # CLIENT -> SESSION
active_sessions: set[int] = set()
waiting_sessions: dict[int, int] = {} # SESSION_ID -> WAITING CLIENT_ID 
sessions: dict[int, tuple[int, int]] = {} # SESSION ID -> CLIENT1, CLIENT2
max_clients = 100
max_sessions = 50
max_game_iters = 200 # FIXME UZYJ TEGO!

print(f"Initialized this snake game")

async def on_connect(websocket, *args, **kwargs):
    """
    """
    global connected_clients
    global max_clients
    global connected_clients

    client_id = None

    if len(connected_clients) < max_clients:
        while(client_id := random.randint(1, max_clients)):
            if client_id not in connected_clients.keys():
                print(f"mam client id {client_id}") # FIXME WYWAL
                break
    else:
        print(f"wiadomosc ze rip ze za duzo polaczen") # FIXME WYWAL
        response = {'error': f'The maximum number of connections ({max_clients}) has been reached.'}
        websocket.send(json.dumps(response))
        await websocket.close(code=1000, reason=response)
        return

    if client_id is not None:
        connected_clients[client_id] = websocket # FIXME CO TUTAJ ? ? slownik na ten websocket czy raczej url i nowy websocket XD!?
        print(f"dodaj polaczenie {connected_clients}") # FIXME WYWAL

    response = {
        'type': 'connect',
        'client_id': client_id,
        'data': {}
    }
    
    await websocket.send(json.dumps(response))
    print(f"wyslal odpowiedz {response}") # FIXME WYWAL
    
    return client_id

async def on_disconnect(websocket, client_id):
    """
    """
    global connected_clients
    global clients_in_sessions

    try:
        connected_clients.pop(client_id)
        clients_in_sessions.pop(client_id) # TODO: ZATRZYMAJ SESJE
        # TODO CLEAR SESION DATA!!
        await websocket.close(code=1000, reason='')
    except KeyError:
        # logger.warning(f"'{client_id}' is not connected")
        await websocket.send(json.dumps({"result":False}))
        return

async def on_start(websocket, client_id):
    """
    """
    global active_sessions
    global max_sessions
    global waiting_sessions
    global clients_in_sessions
    global connected_clients

    if len(active_sessions) < max_sessions:

        print(f"sa wolne sesje {active_sessions}") # FIXME WYWAL

        if client_id not in clients_in_sessions.keys():

            print(f"nie jest w sesji typ") # FIXME WYWAL

            if len(waiting_sessions) == 0:
                print(f"tworzy sesje {client_id}") # FIXME WYWAL
                # CREATE SESSION
                while(session_id := random.randint(1, max_sessions)):
                    if session_id not in active_sessions:
                        break
                waiting_sessions[session_id] = client_id
                clients_in_sessions[client_id] = session_id
                # FIXME CLIENTS IN SESSIONS DODAC?
                # TODO: jakis response send?
                return

            else: # ADD TO SESSION
                print(f"wbija do istniejacej {client_id}") # FIXME WYWAL
                print(f"tu sie wywala {waiting_sessions}")# FIXME WYYWAL
                available_session = random.choice(list(waiting_sessions.keys()))
                active_sessions.add(available_session)
                waiting_client = waiting_sessions.pop(available_session)
                clients_in_sessions[client_id] = available_session
                # clients_in_sessions[waiting_client] = available_session
                # FIXME SEND MESSAGE THAT GAME CAN START
                game_state = initialize_game_state()
                
                # TIXME JAK PRZESLAC TEMU TYPOWI CO CZEKAL WIADOMOSC!
                for i, client in enumerate([waiting_client, client_id], 1):
                    ws = connected_clients[client]
                    print(f"czy to zadziala = ws klientow: {ws}") # FIXME WYWAL
                    if i == 1:
                        ei = 2
                    else:
                        ei = 1
                    # FIXME CLIENT!!!
                    response = {
                        'type': 'game_init',
                        'data': {'my_snake': f'snake_{i}', 'enemy_snake': f'snake_{ei}', **game_state}
                    }
                    print(response)
                    await ws.send(json.dumps(response))
                    return
        
        else:
            response = {'error': 'The client is already in a session.'}
            await websocket.send(json.dumps(response))
            return
    else:
        response = {'error': 'The server has reached a max number of sessions. Try again.'}
        websocket.send(json.dumps(response))

    # FIXME REMOVE THIS
    # self.clients_in_sessions: dict[int, int] = {} # CLIENT -> SESSION
    # self.active_sessions: set[int] = set()
    # self.waiting_sessions: dict[int, int] = {} # SESSION_ID -> WAITING CLIENT_ID

async def keep_alive(self, websocket, *args, **kwargs):
    pass


async def server_handler(websocket, *args, **kwargs):

    try:
        print(f"In server handler")

        async for message in websocket:
            
            print(f"Received msg {message} | {websocket}")

            client_id, message_type, data = parse_message(message)

            if message_type == "connect":
                print(f"Connecting...")
                client_id = await on_connect(websocket) # FIXME REMOVE RET VAL

            if client_id is not None:                    
                
                if message_type == "disconnect":
                    print(f"Disconnecting...")
                    await on_disconnect(websocket, client_id)
                elif message_type == 'start':
                    print(f"Starting...")
                    await on_start(websocket, client_id)
                    
                    # ADD TO THE SESSIONS DICT
                    pass
                elif message_type == 'game':
                    pass

                elif message_type == "echo":
                    await websocket.send(json.dumps({"result":message}))

            else:
                # send response and disconnect
                logger.error(f"lol dziwny message {websocket}")
                # await (websocket, client_id, message_type, data)
    except websockets.exceptions.ConnectionClosedError as cce:
        pass
    finally:
        await websocket.close(code=1000, reason='')

    
def parse_message(message):
    message = json.loads(message)
    type = ''
    client_id = None
    data = {}

    if 'client_id' in message:
        client_id = message['client_id']
    if 'data' in message:
        data = message['data']
    if 'type' in message:
        type = message['type']

    return client_id, type, data

    
async def main():
    global host_ip
    global port

    async with websockets.serve(server_handler, host_ip, port):
        await asyncio.Future()  # run forever

# await asyncio.sleep(10)
   

if __name__ == "__main__":
    asyncio.run(main())

