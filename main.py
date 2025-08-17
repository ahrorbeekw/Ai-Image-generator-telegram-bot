import os
import sys
import asyncio
import logging
from urllib.parse import quote_plus

import httpx
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile

dp = Dispatcher()


from openai import AsyncOpenAI

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

async def fetch_image_bytes(url:str)->bytes:
  async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as c:
    r=await c.get(url)
    if r.status_code==200:
      return r.content
    await asyncio.sleep(1)
    r=await c.get(url)
    if r.status_code==200:
      return r.content
    raise RuntimeError("image_fetch_failed")

@dp.message(CommandStart())
async def start(m:Message):
  await m.answer("👋 Salom. Matn yuboring yoki /draw buyrug'idan foydalaning. Masalan:\n<code>/draw cat astronaut on the moon</code>")

async def handle_prompt(m:Message,prompt:str):
  if not prompt:
    await m.reply("Matn kiriting. Masalan: <code>/draw neon cyberpunk city</code>")
    return
  await m.answer("⏳ Rasm yaratilmoqda...")
  u=f"https://image.pollinations.ai/prompt/{quote_plus(prompt)}"
  try:
    b=await fetch_image_bytes(u)
    f=BufferedInputFile(b,"image.jpg")
    await m.answer_photo(f,caption=f"🖼 {prompt}")
  except Exception:
    await m.reply("❌ Xatolik yuz berdi. Keyinroq urinib ko'ring.")

@dp.message(Command("draw"))
async def draw(m:Message):
  p=m.text.split(maxsplit=1)
  t=p[1] if len(p)>1 else ""
  await handle_prompt(m,t)

@dp.message(F.text)
async def any_text(m:Message):
  await handle_prompt(m,m.text.strip())
async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook(drop_pending_updates=True)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())