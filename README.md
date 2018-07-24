# discord-prom
Discord bot for prometheus node exporter. Lets you interact with a bot that pulls data from your various node exporter clients. 

Works with python v3.6.6 on macos

### Commands so far

` memory use [node] `

` storage use [node] `

` monitor [rx, tx, read, write] [node] `


### Using with your own bot

create a `key.py` file in the same dir:
`client_token = '[your bot token]'`

Don't forget to add your bot to a channel
