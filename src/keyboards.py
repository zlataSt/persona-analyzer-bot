from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📥 Загрузить переписку")]
], resize_keyboard=True)

def get_actions_kb(user_name: str) -> InlineKeyboardMarkup:
    """Клавиатура после извлечения сообщений."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🧠 Типировать '{user_name}'", callback_data="start_typing")],
        [InlineKeyboardButton(text="👤 Выбрать другого пользователя", callback_data="extract_another")],
        [InlineKeyboardButton(text="🔄 Начать заново", callback_data="restart")]
    ])

def get_hypothesis_kb() -> InlineKeyboardMarkup:
    """Клавиатура для вопроса о гипотезе."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, есть версии", callback_data="hypo_yes"),
            InlineKeyboardButton(text="❌ Нет, на ваш суд", callback_data="hypo_no")
        ]
    ])

def get_analysis_kb() -> InlineKeyboardMarkup:
    """Клавиатура после получения анализа."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Показать полностью", callback_data="show_full_analysis")],
        [InlineKeyboardButton(text="💾 Скачать PDF", callback_data="download_pdf")],
        [InlineKeyboardButton(text="👤 Типировать другого", callback_data="extract_another")],
        [InlineKeyboardButton(text="🔄 Начать заново", callback_data="restart")]
    ])

def get_retry_kb(action: str) -> InlineKeyboardMarkup:
    """Клавиатура для повтора действия после ошибки."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Попробовать еще раз", callback_data=f"retry:{action}")],
        [InlineKeyboardButton(text="🔄 Начать заново с новым файлом", callback_data="restart")]
    ])