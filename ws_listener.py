import json
import re
import websocket

import servitor_utils

try:
    import thread
except ImportError:
    import _thread as thread
import time

def check_message(ws, message):
    try:
        parsed_message = json.loads(message)
        print json.dumps(parsed_message['message'], ensure_ascii=False)
    except:
        print "failed parsing"
        print message
    return True

def check_error(ws, message):
    print message
    return True

def on_message(ws, message):
    if check_message(ws, message):
        return
    elif check_error(ws, message):
        return

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws, settings):
    def run(*args):
        time.sleep(1)
        ws.send(json.dumps("bleep"))
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    settings = servitor_utils.make_settings("settings.yml")
    auth_creds = servitor_utils.make_auth("creds.yml")
    websocket_server = "ws://localhost:8000"
    ws = websocket.WebSocketApp(websocket_server,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close,
                               )
    ws.on_open = on_open(ws, settings)
    ws.run_forever()
