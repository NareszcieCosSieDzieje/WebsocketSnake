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

from logic import initialize_game_state, get_new_food


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

session_iter_synch: dict[int, dict[int, int]] = {}

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
    global sessions
    global waiting_sessions
    global clients_in_sessions
    global connected_clients
    global session_iter_synch

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
                available_session = random.choice(list(waiting_sessions.keys()))
                active_sessions.add(available_session)
                waiting_client = waiting_sessions.pop(available_session)
                clients_in_sessions[client_id] = available_session
                sessions[available_session] = (client_id, waiting_client)

                session_iter_synch[available_session] = {client_id: 1, waiting_client: 1}

                # clients_in_sessions[waiting_client] = available_session
                # FIXME SEND MESSAGE THAT GAME CAN START
                game_state = initialize_game_state()
                
                # TIXME JAK PRZESLAC TEMU TYPOWI CO CZEKAL WIADOMOSC!
                for i, client in enumerate([waiting_client, client_id], 1):
                    if client == client_id:
                        ws = websocket
                    else:
                        ws = connected_clients[client]
                    print(f"czy to zadziala = ws klientow: {ws}") # FIXME WYWAL
                    if i == 1:
                        ei = 2
                    else:
                        ei = 1
                    response = {
                        'type': 'game_init',
                        'data': {'my_snake': f'snake_{i}', 'enemy_snake': f'snake_{ei}', **game_state}
                    }
                    print(response)
                    await ws.send(json.dumps(response))
        
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

async def process_game_iter(websocket, client_id, received_data, *args, **kwargs):
    global active_sessions
    global max_sessions
    global waiting_sessions
    global clients_in_sessions
    global connected_clients
    global sessions
    global session_iter_synch

    current_session = clients_in_sessions.get(client_id, None)
    is_session_active = True if current_session in active_sessions else False

    if client_id in clients_in_sessions and is_session_active:
        # player in an active session

        max_iter = session_iter_synch[current_session][client_id]
        if received_data['iteration'] <= max_iter:
            print(f"Stara wiadomosc {session_iter_synch[current_session]} <= {max_iter}")
            return # DISCARD OLD DATA?
        else:
            session_iter_synch[current_session][client_id] = received_data['iteration']
            print(f"Updated the session {session_iter_synch[current_session]}")

        other_player_id = None
        for player_id in sessions[current_session]:
            if client_id != player_id:
                other_player_id = player_id
                break
        
        other_player_websocket = connected_clients[other_player_id]

        print(f"received data: {received_data}") # FIXME WYWAL

        message = {
            'type': 'game_iter',
            'client_id': client_id,
            'data': {
                'iteration': received_data['iteration'],
                'enemy_snake_direction': received_data['my_snake_direction'],
                'enemy_snake_coordinates': received_data['my_snake'],
            }
        }

        print(f"sending message {message}")

        await other_player_websocket.send(json.dumps(message))

        if received_data['food_eaten']:
            # W TYM PRZYPADKU MUSZE KAZDEMU WYSLAC INFO O NEW FOOD DODATKOWE! I OBSLUZYC 2 WIADOMOSCI OD NICH!
            taken_coordinates = received_data['taken_coordinates']
            # Generate new food
            new_food = get_new_food(taken_coordinates)
            food_message = {
                'type': 'new_food',
                'client_id': client_id,
                'data': {
                    'iteration': received_data['iteration'],
                    'new_food': new_food['coordinates']
                }
            }
            print(f"sending new food message {food_message}")
            await other_player_websocket.send(json.dumps(food_message))
            await websocket.send(json.dumps(food_message))
        
        if session_iter_synch[current_session][other_player_id] == session_iter_synch[current_session][client_id]:
            await asyncio.sleep(0.2)
            
            print(f"Sessions synchronized.")

            if session_iter_synch[current_session][other_player_id] == 100: # FIXME
                print(f"Final interation in session.")
                end_message = {'type': 'end_session', 'client_id': client_id, 'data': {}}
                await other_player_websocket.send(json.dumps(end_message))
                await websocket.send(json.dumps(end_message))
            
            print(f"-----------> Sending synch messages -------->{session_iter_synch[current_session]}")
            synch_message = {'type': 'synchronize', 'client_id': client_id, 'data': {}}
            await other_player_websocket.send(json.dumps(synch_message))
            await websocket.send(json.dumps(synch_message))

    else:
        print(f"Client: ({client_id}) is not in an active session.")


async def send_change_direction(websocket, client_id, data, *args, **kwargs):
    global active_sessions
    global clients_in_sessions
    global connected_clients
    global sessions

    current_session = clients_in_sessions.get(client_id, None)
    is_session_active = True if current_session in active_sessions else False

    if client_id in clients_in_sessions and is_session_active:
        # player in an active session

        other_player_id = None
        for player_id in sessions[current_session]:
            if client_id != player_id:
                other_player_id = player_id
                break
        message = {
            'type': 'change_direction',
            'client_id': client_id,
            'data': data
        }
        other_player_websocket = connected_clients[other_player_id]
        other_player_websocket.send(json.dumps(message))
    else:
        print(f"Client: ({client_id}) is not in an active session.")

async def ack_change_direction(websocket, client_id, *args, **kwargs):
    
    global active_sessions
    global clients_in_sessions
    global connected_clients
    global sessions

    current_session = clients_in_sessions.get(client_id, None)
    is_session_active = True if current_session in active_sessions else False

    if client_id in clients_in_sessions and is_session_active:
        # player in an active session

        other_player_id = None
        for player_id in sessions[current_session]:
            if client_id != player_id:
                other_player_id = player_id
                break
        message = {
            'type': 'ack_change_direction',
            'client_id': client_id,
        }
        other_player_websocket = connected_clients[other_player_id]
        other_player_websocket.send(json.dumps(message))
    else:
        print(f"Client: ({client_id}) is not in an active session.")


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
                elif message_type == 'game_iter':
                    await process_game_iter(websocket, client_id, data)
                elif message_type == 'change_direction':
                    await send_change_direction(websocket, client_id, data)

                elif message_type == 'ack_change_direction':
                    await ack_change_direction(websocket, client_id)

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

