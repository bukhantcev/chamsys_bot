import os
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, MessageReactionUpdated, ReactionTypeEmoji
from aiogram.utils.markdown import hbold
import ai
# === Настройки ===
TOKEN = os.getenv('TOKEN')
GROUP_ID = -4720635713  # ID вашей группы
EMOJI_FUNC2 = "😘"
EMOJI_FUNC3 = '🔥'

# === Инициализация бота ===
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher()


# === Инициализация БД ===
def init_db():
    DB_PATH = "database.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dialog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vopros TEXT,
            otvet TEXT
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


# === Определение состояний ===
class DialogFSM(StatesGroup):
    waiting_for_answer = State()
    threads = State()


# === Обработчик команды /start ===
@dp.message(Command("start"))
async def start_handler(message: Message):
    print(message)
    await message.answer("Бот запущен!")


# === Обработчик сообщений с ?!? в группе ===
@dp.message(F.chat.id == GROUP_ID, F.text.startswith("?!?"))
async def func1(message: Message, state: FSMContext):
    prompt = message.text[len('?!?'):]
    if prompt != '':
        messages = [{"role": "user", "content": prompt}]
        thread_id = ai.create_threads(messages)
        ai.create_run(thread_id, ai.assistant)
        answer = ai.message_list(thread_id)
        await message.reply(answer)
        await state.update_data(thread_id=thread_id)
        await state.set_state(DialogFSM.threads)
        await asyncio.sleep(60)
        ai.delete_threads(thread_id)
        print('final')
        await state.clear()

    else:
        await message.reply("Задайте вопрос")
@dp.message(DialogFSM.threads)
async def dialog(message: Message, state: FSMContext):
    data = await state.get_data()
    thread_id = data.get('thread_id')
    ai.create_message(thread_id, message.text)
    ai.create_run(thread_id, ai.assistant)
    answer = ai.message_list(thread_id)
    await message.reply(answer)



# === Обработчик реакций ===
@dp.message_reaction()
async def check_reaction(event: MessageReactionUpdated, state: FSMContext):


    chat_id = event.chat.id
    message_id = event.message_id

    # Получаем сообщение по message_id
    message = await bot.forward_message(
        chat_id=chat_id,
        from_chat_id=chat_id,
        message_id=message_id
    )


    reaction = event.new_reaction
    if isinstance(reaction[0], ReactionTypeEmoji):
        if reaction[0].emoji == EMOJI_FUNC2:
            await func2(message, state)
        elif reaction[0].emoji == EMOJI_FUNC3:
            await func3(message, state)



# === func2: сохраняет вопрос и ждет ответ ===
async def func2(message: Message, state: FSMContext):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dialog (vopros) VALUES (?)", (message.text[len('?!?'):],))
    dialog_id = cursor.lastrowid
    conn.commit()
    conn.close()
    await state.update_data(dialog_id=dialog_id)
    await state.set_state(DialogFSM.waiting_for_answer)
    await message.answer("Вопрос сохранен. Теперь отправьте ответ (реакция ✅).")


# === func3: сохраняет ответ ===
async def func3(message: Message, state: FSMContext):
    user_data = await state.get_data()
    dialog_id = user_data.get("dialog_id")

    if dialog_id:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE dialog SET otvet = ? WHERE id = ?", (message.text[len('?!?'):], dialog_id))
        conn.commit()
        conn.close()

        await state.clear()
        await message.answer("Ответ сохранен в базе данных.")
    else:
        await message.answer("Сначала отправьте вопрос (реакция ❤️).")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
