import logging as logger
import rel
import websocket
import json
from time import sleep
from .logger import setup_logger
from .manageStream import deployStream, removeStream, downStream


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
                    # Deploy stream
                    logger.info("Attempting to deploy Stream '{}'".format(
                        stream["name"]))
                    deployStream(ws, stream)
                elif stream["status"] == "pendingDelete":
                    # Remove stream
                    logger.info("Attempting to remove Stream '{}'".format(
                        stream["name"]))
                    removeStream(ws, stream)
                elif stream["status"] == "pendingDown":
                    # Down stream
                    logger.info("Attempting to down Stream '{}'".format(
                        stream["name"]))
                    downStream(ws, stream)
                else:
                    logger.debug("No changes to Stream '{}'".format(
                        stream["name"]))
            except Exception as error:
                logger.critical("Failed to change Stream")
                logger.debug("Error: \n{}".format(error))
                # raise error
    elif message[0] == "confirm":
        logger.debug("Confirming with API")
        ws.send(json.dumps({"cmd": "confirm"}))
    else:
        logger.warning("Unknown command: {}".format(message[0]))


def on_error(ws, error):
    logger.error("Error1: {}".format(error))


def on_close(ws, close_status_code, close_msg):
    logger.warning("Websocket closed")
    sleep(5)
    ws.run_forever(dispatcher=rel, reconnect=5)


def on_open(ws):
    pass
    # logger.info("Websocket connected")


def start(api_key, api_url):
    # ws_addr = "wss://api.singer.systems/websocket"
    ws_addr = "wss://"+api_url+"/websocket"
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
