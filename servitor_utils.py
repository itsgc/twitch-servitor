import pika
import requests
import urllib
import urlparse
import yaml

def make_auth(credsfile_path):
    with open(credsfile_path, 'r') as credsfile:
        return yaml.load(credsfile)

def make_settings(settingsfile_path):
    with open(settingsfile_path, 'r') as settingsfile:
        return yaml.load(settingsfile)

def send_aqmp_notice(message, topic):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange="topic_twitch_servitor",
                         exchange_type="topic")
    routing_key = topic
    message = { "type": message['sub-type'],
                "username": message['sub-type-username'],
                "message": message['message']}
    channel.basic_publish(exchange='topic_twitch_servitor',
                      routing_key=routing_key,
                      body=json.dumps(message, ensure_ascii=False))
    connection.close()


class TwitchTools():
    """ Class of tools to facilitate authenticating and fetching basic information
        from the Twitch v5 API"""

    def __init__(self, auth_data):
        self.description = 'Consumes Twitch v5 API'
        self.domain = "twitch.tv"
        self.client_id = auth_data['client_id']
        self.client_secret = auth_data['client_secret']
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.twitchtv.v5+json',
            # 'Authorization': 'OAuth ' + auth_token,
            # 'Authorization': 'Bearer ' + auth_token
        }
        self.jar = requests.cookies.RequestsCookieJar()
        self.session = requests.Session()
        self.auth_listener = auth_data['auth_endpoint']
        # self.jar.set('placeholder_cookie', self.auth_token, domain=self.domain,
        # path='placeholder_path')

    def _get(self, url=None, parameters=None):
        if parameters is None:
            r = self.session.get(url=url, headers=self.headers, cookies=self.jar)
        else:
            r = self.session.get(url=url, params=parameters, headers=self.headers,
                                 cookies=self.jar)
        return r.json()

    def _post(self, url=None, parameters=None, payload=None):
        if parameters is None:
            r = self.session.post(url=url, headers=self.headers, cookies=self.jar,
                                  data=payload)
        else:
            r = self.session.post(url=url, headers=self.headers,
                                  cookies=self.jar, params=parameters,
                                  data=payload)
        return r.json()

    def get_auth_url(self):
        payload = { "client_id": self.client_id,
                    "redirect_uri": self.auth_listener,
                    "response_type": "code",
                    "scope": "channel_read" }
        url = urlparse.urlparse("https://id.twitch.tv/oauth2/authorize")
        urllist = [ url.scheme, url.netloc, url.path, None, urllib.urlencode(payload),
                    url.fragment ]
        return urlparse.urlunparse(urllist)

    def get_app_token(self, scope):
        grant_type = "client_credentials"
        payload = { 'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': grant_type}
        url = "https://id.twitch.tv/oauth2/token"
        if scope is not None:
            payload['scope'] = scope
        app_token = self._post(url=url, payload=payload)
        return app_token

    def get_access_tokens(self, intermediate_code):
        grant_type = "authorization_code"
        redirect_uri = self.auth_listener
        payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": intermediate_code,
                "grant_type": grant_type,
                "redirect_uri": redirect_uri
        }
        url = "https://id.twitch.tv/oauth2/token"
        access_token = self._post(url=url, parameters=payload, payload=payload)
        print access_token
        return access_token

    def get_user_info(self, auth_token, type, value):
        url = "https://api.twitch.tv/helix/users"
        self.headers['Authorization'] = 'Bearer ' + auth_token
        print self.headers
        payload = {type: value}
        user_info = self._get(url=url, parameters=payload)
        print user_info
        return user_info

    def get_channel_id(auth_token):
        url = 'https://api.twitch.tv/kraken/channel'
        self.headers['Authorization'] =  'OAuth ' + auth_token
        channel_id = self._get(url=url, headers=headers)
        return channel_id

    def subscribe_followers(user_id, callback_url):
        self.headers['Client-ID'] = self.client_id
        sub_url = "https://api.twitch.tv/helix/webhooks/hub"
        base_topic_url = "https://api.twitch.tv/helix/users/follows"
        payload = { "to_id": user_id }
        url = urlparse.urlparse(base_topic_url)
        urllist = [ url.scheme, url.netloc, url.path, None, urllib.urlencode(payload),
                    url.fragment ]
        topic_url = urlparse.urlunparse(urllist)
        subscribe_payload = {"hub.callback": callback_url,
                             "hub.mode": "subscribe",
                             "hub.topic": topic_url,
                             "hub.lease_seconds": 3600}
        subscribe = self._post(url=sub_url, payload=json.dumps(subscribe_payload))
        return subscribe
