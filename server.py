#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
from definitions import WEBSOCKET_IP, WEBSOCKET_PORT

logging.basicConfig()

STATE = {"task": None, 
         "parameters": None}

USERS = set()

def parameters_event():
    if STATE['parameters'] is None:
        p = json.dumps({"type": "parameters", "has_data": False, "parameters": ""})
    else:
        p = json.dumps({"type": "parameters", "has_data": True, "parameters": json.dumps(STATE['parameters'])})
    return p

def specific_parameter_event(name):
    if STATE['parameters'] is None:
        p = json.dumps({"type": "iparam", "has_data": False, "value": ""})
    else:
        p = json.dumps({"type": "iparam", "has_data": True, "value": json.dumps(STATE['parameters'][name])})
    return p

def task_event():
    if STATE['task'] is None:
        p = json.dumps({"type": "task", "has_data": False, "task": ""})
    else:
        p = json.dumps({"type": "task", "has_data": True, "task": STATE['task']})
    return p

def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})

async def notify_parameters():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = parameters_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_specific_parameter(name):
    if USERS:
        message = specific_parameter_event(name)
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_task():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = task_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()


async def serve_parameters(websocket, path):
    # register(websocket) sends user_event() to websocket
    try:
        await register(websocket)
        async for message in websocket:
            data = json.loads(message)
            print(data)
            if data["type"] == "set_parameters":
                STATE["parameters"] = json.loads(data["parameters"])
                await notify_parameters()
            elif data["type"] == "set_task":
                STATE["task"] = data["task"]
                await notify_task()
                await notify_parameters()
            elif data["type"] == "get_parameter":
                await notify_specific_parameter(data["name"])
    except Exception:
        print("Websocket connection closed.")
    finally:
        await unregister(websocket)


start_server = websockets.serve(serve_parameters, WEBSOCKET_IP, WEBSOCKET_PORT)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()