

import schedule
import rel
import time
import _thread
import websocket
import asyncio
from time import sleep
api_key = "3867cb4d-48c1-4a5d-a395-fec3ac24a588"


def on_message(ws, message):
    print("Recieved --> ", message)


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    print(close_status_code)
    print("### closed ###")
    sleep(5)
    ws.run_forever(dispatcher=rel, reconnect=5)


def on_open(ws):
    print("Opened connection")


def theSchedule(ws):
    schedule.every(2).seconds.do(ws.send, "ping")
    schedule.every(30).seconds.do(ws.send, "getFlow")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8000/websocket",
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
