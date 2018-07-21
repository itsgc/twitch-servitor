import json
import pika
import re
import time
import websocket
from os import environ

import servitor_utils

try:
    import thread
except ImportError:
    import _thread as thread
import time

settings = servitor_utils.make_settings(environ.get('SETTINGS_FILE'))
auth_data = servitor_utils.make_auth(environ.get('SECRETS_FILE'))

def check_message(ws, message):
    if message[0] == "@":
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
            args['type'] = "PRIVMSG"
            print args['type'] + " <" + args['username'] + "> " + args['message']
            return True
    elif message[0] == ":":
        regex = (r':([^!]*)![^!]*@[^.]*.tmi.twitch.tv'  # username
                 r' [#]?PRIVMSG ([^ ]*)'  # channel
                 r' :(.*)') # message
        regex = re.compile(regex, re.UNICODE)
        match = re.search(regex, message)
        args = dict()
        if match:
            args['username'] = match.group(1)
            args['channel'] = match.group(2)
            args['message'] = match.group(3).rstrip()
            if args['username'] == "jtv":
                args['type'] = "SYSNOTICE"
                if is_hosting(args['message']):
                    args['sub-type'] = "HOST"
                    args['sub-type-username'] = args['message'].split(" ")[0]
                    print args['type'] + " " + args['sub-type'] + " " + args['sub-type-username']
                    servitor_utils.send_amqp_notice(host=settings['amqp_server'],
                                                    exchange=settings['amqp_exchange'],
                                                    topic=settings['topics']['irc'],
                                                    message=args)
                    print "sent something"
                else:
                    print args['type'] + " " + args['username'] + " " + args['message']
            else:
                args['type'] = "OTHERMSG"
                print args['type'] + " " + args['username'] + " " + args['message']
        else:
            print message

def is_subscription(usernotice):
    if "subscribed" in usernotice:
        return True
    else:
        return False

def is_hosting(message):
    if "hosting" in message:
        return True
    else:
        return  False

def check_usernotice(ws, message):
    if message[0] == "@":
        arg_regx = r"([^=;]*)=([^ ;]*)"
        arg_regx = re.compile(arg_regx, re.UNICODE)
        args = dict(re.findall(arg_regx, message[1:]))
        regex = (
            r'^@[^ ]* :tmi.twitch.tv'
            r' USERNOTICE #(?P<channel>[^ ]*)'  # channel
            r'((?: :)?(?P<message>.*))?')  # message
        regex = re.compile(regex, re.UNICODE)
        match = re.search(regex, message)
        if match:
            args['channel'] = match.group(1)
            args['message'] = match.group(2)
            args['type'] = "USERNOTICE"
            system_message = args['system-msg'].split("\s")
            args['user'] = system_message[0]
            if is_subscription(system_message):
                args['sub-type'] = "SUBSCRIPTION"
            else:
                args['sub-type'] = "OTHER"
            print args['type'] + " " + args['user'] + " " + args['sub-type'] + " full message:" + re.sub(r'\\s', ' ', args['system-msg'])
            return True

def check_ping(ws, message):
    if re.search(r"PING :tmi\.twitch\.tv", message):
        ws.send("PONG :tmi.twitch.tv")
        return True

def check_error(ws, message):
    if re.search(r":tmi.twitch.tv NOTICE \* :Error logging i.*", message):
        ws.close()
        print("closing session due to logging error")

def on_message(ws, message):
    if check_message(ws, message):
        return
    elif check_ping(ws, message):
        return
    elif check_usernotice(ws, message):
        return
    elif check_error(ws, message):
        return

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws, settings, auth_token):
    def run(*args):
        nickname_command = "NICK {}".format(settings['nickname'])
        irc_channel_command = "JOIN {}".format(settings['irc_channel'])
        pass_command = "PASS oauth:{}".format(auth_token)
        time.sleep(5)
        ws.send(pass_command)
        time.sleep(5)
        ws.send(nickname_command)
        time.sleep(1)
        ws.send(irc_channel_command)
        time.sleep(1)
        ws.send("CAP REQ :twitch.tv/membership")
        time.sleep(1)
        ws.send("CAP REQ :twitch.tv/tags")
        time.sleep(1)
        ws.send("CAP REQ :twitch.tv/commands")
        message = dict()
        message['message'] = "signon to Twitch IRC succeeded"
        message['sub-type'] = "NOTICE"
        message['sub-type-username'] = "vigil"
        servitor_utils.send_amqp_notice(host=settings['amqp_server'],
                                        exchange=settings['amqp_exchange'],
                                        topic=settings['topics']['irc'],
                                        message=message)
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    twitch_token = auth_data['twitch_irc_token']
    websocket.enableTrace(True)
    websocket_server = settings['websocket_irc_server']
    ws = websocket.WebSocketApp(websocket_server,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              )
    ws.on_open = on_open(ws, settings, twitch_token)
    ws.run_forever()
