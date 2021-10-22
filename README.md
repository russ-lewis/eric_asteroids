Right now, we're just playing with networking technology - educating ourselves about how to send messages back and forth.
The rate of messages is expected to be a few dozen per second, so HTTP is not appropriate (though we might move to
WebSockets at some time).  UDP is also another possibility, maybe.

The goal is to eventually develop a simplistic multiplayer "Asteroids" game - a server tracks the asteroids and sends
regular update messages to the clients; the clients send back their moves to the server.
