# twitch-servitor
A pet project to experiment with RabbitMQ, Websocket and the Twitch API.

## What
This is my personal attempt at recreating the functionality of services such as
StreamLabs streamer event alerts.


## Why
I wanted to understand what happens behind
the curtains when twitch events such as Follows, Hosts and Subscriptions trigger
an alert on a streamer broadcast, typically followed by a graphical effect live
on stream.

For an idea of the workflow involved check this video:
https://www.youtube.com/watch?v=dqIt3xOYzv4

## What's not
It is by no means intended to be a working product. It is a tech demo i built to
better understand the technologies Twitch and partners use to achieve those
effects.

It is also not made by a professional programmer. This is spaghetti code i wrote
in my spare time exclusively for my own benefit. Documentation will suck and the
whole structure is probably way more complicated than it needs to be.

## Details

The Twitch API is.. frazzled. You need completely different communication
channels open depending on which event notification you want to receive.

**Hosts**: IRC over WebSocket \
**Follows**: Webhook \
**Subscriptions**: [PubSub](https://dev.twitch.tv/docs/pubsub/) protocol over WebSocket

I built 3 different listeners to support all event types.
* **[vigil](vigil.py)**: basic IRC/WebSocket client that will connect to Twitch IRC, log
 onto a given streamer channel and parse incoming messages searching for Host
 notification events. Sadly, it relies on screen-scraping as the messages are not
 structured.
* **[pubsub](pubsub.py)**: websocket client that "subscribes"
to a topic on Twitch API's PubSub server to obtain events when someone subscribes
to your stream. This component has been only tested with the sample payloads published in Twitch's
API reference so i expect this to be very buggy.
* **[cogitator](cogitator.py)**: at its core this is my webhook listener. you will need a publicly
reachable webserver that Twitch can hit with the webhook payload.

### Support components
Since the 3 events are delivered in such different ways, i wanted a single endpoint
my client-side code will connect to when generating stream overlays. Each listener
generates a RabbitMQ message and **[rabbitmq-receiver](rabbitmq-receiver.py)** collects them and delivers
them over WebSocket to the client-side code.

**[ws_listener](ws_listener.py)** is a small standalone websocket client used for testing.

## Authentication
A lot of details for the authentication side can be read in depth here: 
https://dev.twitch.tv/docs/authentication/

* **vigil** can work with a simple, unprivileged access token such as one from
https://twitchapps.com/tmi/

* **cogitator** will request a token from twitch with the correct scope. By visiting
https://{cogitator_ip}/auth you will be redirected to Twitch for granting authorization
to the app. Once twitch sends you back to the application instance, a valid token
will get stored in the database and used to subscribe to Twitch's Webhook service
for follow events.

* **pubsub** auth is messy right now. Hit https://{cogitator_ip}/auth?type=pubsub
to have the app request a token with the *channel_subscription* scope to Twitch.
Once that is done, pubsub will have the needed credentials to connect to Twitch
PubSub service and subscribe to the correct topic to receive Subscriptions events.

## TODO
* store the permanent code returned by Twitch after a user has granted permission
to the app (instead of the ephemeral ones)
* request multiple scopes at once
* move the Database code into a class
* implement HTTP error codes
* improve error handling and custom exceptions
* logging (lol)
* create example creds.yml and settings.yml with empty values
* find some JS code to ripoff for the client-side overlay generator.
* cleanup all the print statements.
* link to the "ops" repo and document better standing up the whole system.
* provide nginx examples

## Code ripoffs
I shamelessly ripped code off from
* https://github.com/websocket-client
* https://www.rabbitmq.com/tutorials/tutorial-one-python.html
* countless ServerFault posts