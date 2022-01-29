# Omegle Bot
- What is this
- How does it works?
    - Connection
    - Console
    - Telegram
- Contacts
## What is this?
This is a software that allow you to talk with people on omegle through console or telegram bot.
## How does it works?
### Connection
This basically simulate the connection a browser does to omegle for start chatting.<br>
For starting chatting first we have to obtain a "token" by doing a get request to<br>
https://front{SERVER}.omegle.com/start?caps=recaptcha2,t&firstevents=1&spid=&randid=BKHDLXDX&topics={TOPICS}&lang={LANG}<br>
After getting the token we start doing post requests to<br>
https://front{SERVER}.omegle.com/disconnect<br>
This return what is happening:
- Found a chat
- Received message
- Stranger disconnected

Once we found a chat, we can start receiving messages and sending messages by doing a post request to<br>
https://front{SERVER}.omegle.com/send<br>
And, when we want to disconnect we just send a post requests to<br>
https://front{SERVER}.omegle.com/disconnect<br>
Every post request have these params: token<br>
For sending message also the message we want to send.<br>
### Console
For using the connection with the console and start chatting we just send commands in the console.<br>
- newchat -> start new chat
- stopchat -> stop current chat
- startyping -> send post request for saying to the server we are "typing"
- stoptyping -> send post request for saying that we have stopped typing
- Every other messages -> Send that message to the chat
### Telegram
For telegram i had to create a bot for allowing someone to send messages/commands<br>
The code is a little bit modified since the bot allow multiple chat to be active at the same time.
## Contacts
For contacting me
- Email: alessandro.condello.email@gmail.com
- Discord: TechAle#1195