"""Telegram lead-capture bot: aiogram 3, SQLite, no paid services."""
import asyncio
import logging
import os
import re
from html import escape

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv

load_dotenv()
import database  # noqa: E402  # .env must load before database path

router = Router()
logger = logging.getLogger(__name__)
SERVICES = ("Interior detailing", "Exterior detailing", "Full detailing", "Other service")


class LeadForm(StatesGroup):
    consent = State()
    service = State()
    name = State()
    phone = State()
    comment = State()


def choice_keyboard(options: tuple[str, ...]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=x)] for x in options], resize_keyboard=True)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🚗 Welcome to AutoDetail Demo!\n\n"
        "I can help you request a detailing quote. "
        "This is a portfolio demonstration, not a real auto shop.\n\n"
        "To process your request, we will store the details you provide "
        "and send them to the demo administrator. "
        "Send /delete to remove your saved requests.\n\n"
        "Do you agree to this data processing?",
        reply_markup=choice_keyboard(("I agree", "No thanks")),
    )
    await state.set_state(LeadForm.consent)


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Request cancelled. Send /start to begin again.", reply_markup=ReplyKeyboardRemove())


@router.message(Command("delete"))
async def delete(message: Message, state: FSMContext):
    await state.clear()
    count = database.delete_user_leads(message.from_user.id)
    await message.answer(f"Deleted {count} saved request(s). Administrator notifications cannot be recalled.",
                         reply_markup=ReplyKeyboardRemove())


@router.message(LeadForm.consent)
async def consent(message: Message, state: FSMContext):
    if message.text == "No thanks":
        await cancel(message, state)
        return
    if message.text != "I agree":
        await message.answer("Choose 'I agree' or 'No thanks'.")
        return
    await state.set_state(LeadForm.service)
    await message.answer("Which service do you need?", reply_markup=choice_keyboard(SERVICES))


@router.message(LeadForm.service)
async def service(message: Message, state: FSMContext):
    if not message.text or message.text not in SERVICES:
        await message.answer("Please select a service using the buttons.")
        return
    await state.update_data(service=message.text)
    await state.set_state(LeadForm.name)
    await message.answer("What's your name?", reply_markup=ReplyKeyboardRemove())


@router.message(LeadForm.name)
async def name(message: Message, state: FSMContext):
    val = (message.text or "").strip()
    if not 2 <= len(val) <= 80:
        await message.answer("Please enter a name between 2 and 80 characters.")
        return
    await state.update_data(name=val)
    await state.set_state(LeadForm.phone)
    await message.answer("Your contact phone (e.g. +1 555 123 4567)?")


@router.message(LeadForm.phone)
async def phone(message: Message, state: FSMContext):
    val = (message.text or "").strip()
    if not re.fullmatch(r"\+?[0-9 ()-]{7,22}", val) or len(re.sub(r"\D", "", val)) < 7:
        await message.answer("Please enter a valid phone number (at least 7 digits).")
        return
    await state.update_data(phone=val)
    await state.set_state(LeadForm.comment)
    await message.answer("Vehicle details or extra notes? Send '-' to skip.")


@router.message(LeadForm.comment)
async def comment(message: Message, state: FSMContext, bot: Bot):
    val = (message.text or "").strip()
    if not val or len(val) > 500:
        await message.answer("Please send a note up to 500 characters, or '-' to skip.")
        return
    data = await state.get_data()
    comment_text = "Not provided" if val == "-" else val
    lead_id = database.save_lead(message.from_user.id, message.from_user.username,
                                 data["name"], data["phone"], data["service"], comment_text)
    admin_id = int(os.environ["ADMIN_CHAT_ID"])
    handle = f"@{escape(message.from_user.username)}" if message.from_user.username else "—"
    notice = (
        f"📩 <b>New demo lead #{lead_id}</b>\n"
        f"Name: {escape(data['name'])}\n"
        f"Phone: {escape(data['phone'])}\n"
        f"Service: {escape(data['service'])}\n"
        f"Details: {escape(comment_text)}\n"
        f"Telegram: {handle}\n"
        f"User ID: <code>{message.from_user.id}</code>"
    )
    try:
        await bot.send_message(admin_id, notice)
        await message.answer("✅ Your demo request is saved and sent to the administrator.\n"
                             "Send /start to create another request or /delete to erase stored data.")
    except Exception:
        logger.exception("Could not notify administrator about lead %s", lead_id)
        await message.answer("✅ Your demo request is saved, but the administrator notification failed. "
                             "Please contact the demo owner directly.")
    await state.clear()


@router.message()
async def fallback(message: Message):
    await message.answer("Send /start to request a quote, /cancel to cancel, or /delete to erase saved requests.")


async def main():
    token = os.getenv("BOT_TOKEN", "")
    admin_id = os.getenv("ADMIN_CHAT_ID", "")
    if not token or token == "replace_with_your_bot_token" or not admin_id.isdecimal():
        raise SystemExit("Set BOT_TOKEN and numeric ADMIN_CHAT_ID in .env first.")
    logging.basicConfig(level=logging.INFO)
    database.initialize()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
