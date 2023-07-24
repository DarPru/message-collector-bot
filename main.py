import os
from datetime import datetime
from config import TOKEN

from aiogram import Bot, Dispatcher, executor, types

is_logging = False
logging_path = ''


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_logging(message: types.Message):
    global is_logging
    global logging_path

    user_name = message.from_user.username
    is_logging = True
    dt = datetime.now()
    ts = datetime.timestamp(dt)

    if not os.path.exists('logs'):
        os.makedirs('logs')
    with open(f"logs/{user_name}_{str(ts)}.txt", "w", encoding='UTF8') as file:
        file.write(f"****** {dt} ******\n")
        file.write(f"Пользователь {user_name} начал логирование\n\n\n")
    logging_path = f'logs/{user_name}_{str(ts)}.txt'
    await message.answer("Логирование начато")

@dp.message_handler(commands=['get'])
async def get_file(message: types.Message):
    global is_logging
    if is_logging:
        await bot.send_document(chat_id=message.chat.id, document=open(logging_path, 'rb'))
        os.remove(logging_path)
        is_logging = False
    else:
        await message.answer("Запустите логирование")
        await message.answer("/start")
@dp.message_handler()
async def message_processing(message: types.Message):
    if is_logging:
        message_text = message.text
        date = message.forward_date if message.forward_date is not None else message.date
        user = ''
        try:
            name = message.forward_from.first_name
            user = name
        except Exception as ex:
            user = message.forward_sender_name
        try:
            lastname = message.forward_from.last_name
            user = f'{user} {lastname}'
        except Exception as ex:
            pass
        try:
            username = message.forward_from.username
            user = f'{user} {username}'
        except Exception as ex:
            pass
        if user is None: user = f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.username}'

        with open(logging_path, 'a', encoding='utf8') as f:
            f.write(f'{user} [{date}]\n\n')
            f.write(message_text + '\n\n')
            f.write('----------------------------------\n')
    else:
        await message.answer("Запустите логирование")
        await message.answer("/start")
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
