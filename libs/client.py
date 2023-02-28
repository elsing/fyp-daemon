import logging as logger
import rel
import time
import _thread
import websocket
import asyncio
import json
from time import sleep
from .logger import setup_logger
from .manageStream import deployStream, removeStream
import numpy as np
import subprocess


def updateField(ws, stream_id, field, value):
    try:
        ws.send(json.dumps(
            {"cmd": "patch", "id": stream_id, "field": field, "value": value}))
    except Exception as error:
        raise error

    # return result
    # while True:
    #     time.sleep(5)
    #     print("Checking Wireguard connections")
    #     result = subprocess.run(
    #         ["wg", "show"], stdout=subprocess.PIPE).stdout.decode('utf-8')
    #     print(result)
    #     for line in result.splitlines():
    #         if "interface" in line:
    #             interface = line.split(":")[1].strip()
    #             print("Interface: {}".format(interface))
    #         elif "peer" in line:
    #             peer = line.split(":")[1].strip()
    #             print("Peer: {}".format(peer))
    #         elif "latest handshake" in line:
    #             handshake = line.split(":")[1].strip()
    #             print("Handshake: {}".format(handshake))
    #             if handshake == "never":
    #                 print("Handshake never, restarting Wireguard")
    #                 result = subprocess.run(
    #                     ["wg-quick", "down", interface], stdout=subprocess.PIPE).stdout.decode('utf-8')
    #                 print(result)
    #                 result = subprocess.run(
    #                     ["wg-quick", "up", interface], stdout=subprocess.PIPE).stdout.decode('utf-8')
    #                 print(result)


def on_message(ws, message):
    logger.debug("WS Recieved --> {}".format(message))
    message = json.loads(message)
    if message[0] == "info":
        logger.info(message[1])
    elif message[0] == "streams":
        for stream in message[1]:
            error = ""
            # print("Stream: {} with details {}".format(
            # stream["name"], stream))
            try:
                if stream["status"] == "init" or stream["status"] == "pendingUpdate":
                    # Write WG config to host
                    error, value = deployStream(stream)
                    print("test")
                    updateField(ws, stream["stream_id"], "error", error)
                    updateField(ws, stream["stream_id"], "status", value)

                elif stream["status"] == "pendingDelete":
                    logger.critical(stream)
                    error = removeStream(ws, stream)
                    if error == "":
                        updateField(ws, stream["stream_id"], "error", error)
                        updateField(ws, stream["stream_id"], "status", value)
                    else:
                        print("trigger")
                        print(error)
                        raise error
                else:
                    logger.debug("No changes to Stream '{}'".format(
                        stream["name"]))
            except Exception as error:
                logger.CRITICAL("Failed to iteratite: ", error)
                # raise error
            # Send updates to DB
    else:
        logger.warning("Unknown command: {}".format(message[0]))


def on_error(ws, error):
    logger.error("Error1: {}".format(error))


def on_close(ws, close_status_code, close_msg):
    logger.warning("Websocket closed")
    sleep(5)
    ws.run_forever(dispatcher=rel, reconnect=5)


def on_open(ws):
    logger.info("Websocket connected")


def start(api_key):
    # ws_addr = "wss://api.singer.systems/websocket"
    ws_addr = "wss://api.singer.systems/websocket"
    ws = websocket.WebSocketApp(ws_addr,
                                # Add custom headers here
                                header={
                                    "api_key": api_key},
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    ws.run_forever(dispatcher=rel, reconnect=5)
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
