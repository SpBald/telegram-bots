from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Поддержка", callback_data="support")],
        [InlineKeyboardButton("Профиль", callback_data="profile")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("Ответить на тикет", callback_data="answer_ticket")],
        [InlineKeyboardButton("Начислить баланс", callback_data="add_balance")]
    ]
    return InlineKeyboardMarkup(keyboard)
