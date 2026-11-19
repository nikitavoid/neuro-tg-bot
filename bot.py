"""NeuroBot — a Telegram AI assistant powered by an LLM.

Features:
  * remembers the last messages of every chat (short-term memory)
  * switchable personas: /assistant, /translator, /coder
  * /reset clears the conversation
"""

import asyncio
import logging
import os
from collections import defaultdict, deque

import anthropic
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-5-5"
HISTORY_LIMIT = 20  # messages kept per chat (user + assistant)

PERSONAS = {
    "assistant": "You are a friendly, concise assistant in a Telegram chat. "
    "Answer in the user's language. Keep replies short unless asked for detail.",
    "translator": "You are a translator. Detect the language of each message. "
    "If it is Russian, translate it to English; otherwise translate it to Russian. "
    "Reply with the translation only.",
    "coder": "You are a senior Python developer. Give working code with a one-line "
    "explanation. Use Markdown code blocks.",
}

client = anthropic.AsyncAnthropic()
history: dict[int, deque] = defaultdict(lambda: deque(maxlen=HISTORY_LIMIT))
persona: dict[int, str] = defaultdict(lambda: "assistant")
dp = Dispatcher()


async def ask_llm(chat_id: int) -> str:
    response = await client.beta.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=PERSONAS[persona[chat_id]],
        messages=list(history[chat_id]),
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        return "Sorry, I can't help with that one."
    return "".join(b.text for b in response.content if b.type == "text") or "…"


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Hi! I'm NeuroBot 🤖\n\n"
        "Just write me anything.\n"
        "/assistant — general help\n"
        "/translator — RU ⇄ EN translation\n"
        "/coder — programming help\n"
        "/reset — forget our conversation"
    )


@dp.message(Command("assistant", "translator", "coder"))
async def switch_persona(message: Message) -> None:
    name = message.text.split()[0].lstrip("/").split("@")[0]
    persona[message.chat.id] = name
    history[message.chat.id].clear()
    await message.answer(f"Mode switched to <b>{name}</b> ✅")


@dp.message(Command("reset"))
async def reset(message: Message) -> None:
    history[message.chat.id].clear()
    await message.answer("Memory cleared 🧹")


@dp.message(F.text)
async def chat(message: Message) -> None:
    chat_id = message.chat.id
    history[chat_id].append({"role": "user", "content": message.text})
    await message.bot.send_chat_action(chat_id, ChatAction.TYPING)
    try:
        answer = await ask_llm(chat_id)
    except anthropic.RateLimitError:
        history[chat_id].pop()
        await message.answer("Too many requests, try again in a minute ⏳")
        return
    except anthropic.APIError:
        logging.exception("LLM API error")
        history[chat_id].pop()
        await message.answer("Something went wrong, please try again.")
        return
    history[chat_id].append({"role": "assistant", "content": answer})
    # Telegram limit is 4096 chars per message
    for i in range(0, len(answer), 4000):
        await message.answer(answer[i : i + 4000], parse_mode=None)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(
        os.environ["BOT_TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
