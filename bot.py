import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = os.environ.get('TOKEN')

user_data_store = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


def calculate_price(brawler_name: str, current_trophies: int, desired_trophies: int) -> float:
    if desired_trophies <= current_trophies:
        return -1
    trophy_difference = desired_trophies - current_trophies
    name = brawler_name.lower().strip()
    multiplier = 0.3
    hard_brawlers = [
        "мортис", "сэнди", "пайпер", "мэг", "бонни", "динамайк", "кольт",
        "гром", "базз", "корделиус", "роза", "8-бит", "белль", "финкс", "нани", "R-T"
    ]

    very_hard_brawlers = [
        "спайк", "амбер", "честер",
        "меллоди", "сэнди", "тик"
    ]

    if name in hard_brawlers:
        multiplier = 0.5
    elif name in very_hard_brawlers:
        multiplier = 0.6
    price = trophy_difference * multiplier
    return round(price, 2)


async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data_store[user_id] = {}
    await update.message.reply_text(
        'Привет! Я помогу рассчитать стоимость буста кубков в Brawl Stars.\n'
        'Введи имя бойца (например, "Спайк" или "Мико"):'
    )


async def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_data_store:
        user_data_store[user_id] = {}

    if 'brawler' not in user_data_store[user_id]:
        user_data_store[user_id]['brawler'] = text
        await update.message.reply_text(f'Боец: {text}. Теперь введи ТЕКУЩИЕ кубки (только число):')

    elif 'current_trophies' not in user_data_store[user_id]:
        try:
            current = int(text)
            if current < 0:
                raise ValueError("Число не может быть отрицательным")
            user_data_store[user_id]['current_trophies'] = current
            await update.message.reply_text(f'Текущие кубки: {current}. Теперь введи ЖЕЛАЕМЫЕ кубки (только число):')
        except ValueError:
            await update.message.reply_text('Пожалуйста, введи корректное положительное число (например, 300).')

    elif 'desired_trophies' not in user_data_store[user_id]:
        try:
            desired = int(text)
            if desired < 0:
                raise ValueError("Число не может быть отрицательным")

            brawler = user_data_store[user_id]['brawler']
            current = user_data_store[user_id]['current_trophies']
            price = calculate_price(brawler, current, desired)

            if price == -1:
                await update.message.reply_text(
                    'Ошибка: Желаемые кубки должны быть больше текущих. Напиши /start для нового расчета.')
            else:
                await update.message.reply_text(
                    f'✅ Расчет для бойца *{brawler}*:\n'
                    f'📊 {current} ⚔️ {desired} кубков.\n'
                    f'💰 Стоимость услуги: *{price} руб.*\n\n'
                    f'Для нового расчета напиши /start.',
                    parse_mode='Markdown'
                )
            del user_data_store[user_id]
        except ValueError:
            await update.message.reply_text('Пожалуйста, введи корректное положительное число (например, 500).')
    else:
        await update.message.reply_text('Напиши /start для нового расчета.')


def main():
    print("Запуск бота...")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот успешно запущен и готов к работе!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
