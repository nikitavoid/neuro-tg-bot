# 🤖 NeuroBot

A Telegram AI assistant powered by an LLM, with chat memory and switchable personas.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3-2CA5E0?style=flat-square&logo=telegram&logoColor=white)
![AI](https://img.shields.io/badge/AI-LLM-7f5af0?style=flat-square)

## Features

- 💬 Remembers the last 20 messages of every chat
- 🎭 Three modes: `/assistant`, `/translator` (RU ⇄ EN), `/coder`
- 🧹 `/reset` wipes the conversation
- ✂️ Splits long answers to fit Telegram's message limit

## Quick start

```bash
git clone https://github.com/nikitavoid/neuro-tg-bot
cd neuro-tg-bot
pip install -r requirements.txt
cp .env.example .env   # put your tokens here
python bot.py
```

Get a bot token from [@BotFather](https://t.me/BotFather) and an Anthropic API key.

## How it works

Every incoming message is added to the chat's history and sent to the LLM together with a system prompt for the current mode. The reply goes back to Telegram and is stored in the history too.

## License

MIT
