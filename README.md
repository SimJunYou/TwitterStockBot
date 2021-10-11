# WallStweetBot

A tiny little Telegram bot hosted on Heroku that can send you sketchy financial advice every now and then.

The bot is **still active!** Find it at @wallstweetbot on Telegram.

## What it does

Actually, it's just tweets. You get to choose which user's tweets you want to "follow". There's a live feed option, and some other commands which can give you the latest tweet or trawl through their tweets to find their recommendations. You can add it to a group too to let it ~~irritate~~ send tweets to your friends. That being said, there isn't actually any high-level analytics going on.

## Rationale

I got introduced to investing and felt that some people's Twitter feeds might be a good source of information. Except, I didn't use Twitter. Naturally, I made a Twitter account... to hook it into a Telegram bot that can send those tweets to me on Telegram.

I didn't really use it all that much in the end, but it was a fun project.

## Architecture

This bot isn't mainly a Telegram bot, per se. Instead, there's a "central" bot which reads from a job queue and sends jobs to separate threads. There is one thread for the Twitter bot and one for the Telegram bot. User input from the Telegram bot adds to the job queue. Simple as that.

I really just wanted to toy around with combining two bots into one cohesive system, and also toy around with multithreading. I'd say it turned out pretty well.

## Limitations
Since it was a personal project, I didn't really think about adding functions to allow people to change who they wanted to follow. It's still hardcoded in `config.py`. There's also no user-specific config, which kinda made sense at the time since I was the only one using it.

If I were to continue working on this, I would probably try spinning up a Postgres DB on Heroku to store user specific configs. Maybe a bit of an overkill, but I did just learn about databases in school...

## Commands
`/latest` - Get each user's latest tweet.

`/recommend` - Searches for the followed user's portfolios and recommendations.

`/toggle` - Stop the bot's live tweet feed. Other commands will still work.

`/shutdown` - Shut down the bot.

## Built With

* [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot) - Python interface for Telegram's official bot API
* [python-twitter](https://github.com/bear/python-twitter) - Python interface for Twitter's official bot API
