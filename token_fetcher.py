import servitor_utils

settings = servitor_utils.make_settings("settings.yml")
auth_data = servitor_utils.make_auth("creds.yml")
auth_data['auth_endpoint'] = "https://apple.didgt.info/twitch/authlistener"
pubsub_auth_data = servitor_utils.make_auth("pubsub_creds.yml")

toolkit = servitor_utils.TwitchTools(auth_data)

print toolkit.get_pubsub_token(secret=pubsub_auth_data['pubsub_secret'], dispenser_url="https://apple.didgt.info/twitch/tokendispenser")

