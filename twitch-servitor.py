from yaml import load
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

with open('creds.yml', 'r') as credsfile:
    creds = load(credsfile)
    twitch_token = creds['twitch_irc_token']

def on_message(ws, message):
    if "PING" in message:
        ws.send("PONG :tmi.twitch.tv")
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        pass_string = "PASS {}".format(twitch_token)
        print pass_string
        time.sleep(5)
        ws.send(pass_string)
        time.sleep(5)
        ws.send("NICK twitch-servitor")
        time.sleep(5)
        ws.send("JOIN #karmik")
        time.sleep(1)
        ws.send("PRIVMSG #karmik :Hello word")
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://irc-ws.chat.twitch.tv:80/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              )
    ws.on_open = on_open
    ws.run_forever()
