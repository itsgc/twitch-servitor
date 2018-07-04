from yaml import load
import websocket
import re
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
    elif message[0] == "@":
        arg_regx = r"([^=;]*)=([^ ;]*)"
        arg_regx = re.compile(arg_regx, re.UNICODE)
        args = dict(re.findall(arg_regx, message[1:]))
        regex = (r'^@[^ ]* :([^!]*)![^!]*@[^.]*.tmi.twitch.tv'  # username
                     r' PRIVMSG #([^ ]*)'  # channel
                     r' :(.*)') # message
        regex = re.compile(regex, re.UNICODE)
        match = re.search(regex, message)
        if match:
            args['username'] = match.group(1)
            args['channel'] = match.group(2)
            args['message'] = match.group(3)
            print args
        else:
            print "No match found"
        # message_type = message.split(":")[-2].split(" ")[-2]
        # message_text = message.split("#lobosjr")[-1].split(":")[-1]
    # print args['username'] + " " + args['channel'] + " " + args['message']
    # print message
    # print message.split(":")[-2]
    # print(message_type + " " + message_text)

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
        ws.send("NICK Karmik")
        time.sleep(1)
        ws.send("JOIN #day9tv")
        time.sleep(1)
        ws.send("CAP REQ :twitch.tv/membership")
        time.sleep(1)
        ws.send("CAP REQ :twitch.tv/tags")
        time.sleep(1)
        ws.send("CAP REQ :twitch.tv/commands")
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
