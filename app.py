import rel
import time
import _thread
import websocket
import asyncio
import json
from time import sleep
import numpy as np
import subprocess
api_key = "3867cb4d-48c1-4a5d-a395-fec3ac24a588"


def wireguardControl(status, stream):
    result = subprocess.run(
        ["wg-quick", status, "/etc/wireguard/{}.conf".format(stream)], stdout=subprocess.PIPE).stdout.decode('utf-8')
    return result
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
    # print("DEBUG: Recieved -->", message)
    try:
        message = json.loads(message)
        if message[0] == "info":
            print(message[1])
        elif message[0] == "streams":
            for stream in message[1]:
                # print("Stream: {} with details {}".format(
                # stream["name"], stream))
                if stream["initiated"] == False:
                    wireguardControl("down", stream["stream_id"])
                    with open("/etc/wireguard/{}.conf".format(stream["stream_id"]), "w") as wgconf:
                        wgconf.write(stream["config"])
                    result = wireguardControl("up", stream["stream_id"])
                    print(result)
                    ws.send(json.dumps(
                        {"cmd": "patch", "id": stream["stream_id"], "info": True}))
                else:
                    print("Stream {} already initiated".format(
                        stream["stream_id"]))

        else:
            print("Unknown command: {}".format(message[0]))
    except Exception as e:
        print("Error:", e)


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    print(close_status_code)
    print("### closed ###")
    sleep(5)
    ws.run_forever(dispatcher=rel, reconnect=5)


def on_open(ws):
    print("Opened connection")


if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api.singer.systems/websocket",
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
