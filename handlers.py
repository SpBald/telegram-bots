from telegram import Update
from telegram.ext import ContextTypes
from db import Session, User, SupportTicket
from utils import get_main_keyboard, get_admin_keyboard
from config import ADMIN_IDS

current_admin_action = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    user_id = update.effective_user.id
    username = update.effective_user.username
    referrer = None

    if context.args:
        try:
            referrer = int(context.args[0])
        except ValueError:
            pass

    user = session.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        user = User(telegram_id=user_id, username=username, referrer_id=referrer)
        session.add(user)
        session.commit()

    await update.message.reply_text("Добро пожаловать!", reply_markup=get_main_keyboard())
    session.close()

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "support":
        current_admin_action[user_id] = "support"
        await query.message.reply_text("Напишите сообщение в поддержку.")
    elif query.data == "profile":
        session = Session()
        user = session.query(User).filter_by(telegram_id=user_id).first()
        referrals = session.query(User).filter_by(referrer_id=user.telegram_id).count()
        text = (f"Ваш ID: {user.telegram_id}'
"
                f"Баланс: {user.balance}
"
                f"Рефералов: {referrals}
"
                f"Ваша ссылка: /start {user.telegram_id}")
        await query.message.reply_text(text)
        session.close()
    elif query.data == "answer_ticket":
        current_admin_action[user_id] = "answer_ticket"
        await query.message.reply_text("Введите ID тикета.")
    elif query.data == "add_balance":
        current_admin_action[user_id] = "add_balance"
        await query.message.reply_text("Введите ID пользователя для начисления баланса.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in ADMIN_IDS:
        action = current_admin_action.get(user_id)
        if action == "answer_ticket":
            context.user_data["ticket_id"] = text
            current_admin_action[user_id] = "reply_ticket"
            await update.message.reply_text("Введите ответ для тикета.")
        elif action == "reply_ticket":
            ticket_id = context.user_data.get("ticket_id")
            ticket = session.query(SupportTicket).filter_by(id=int(ticket_id)).first()
            if ticket:
                await context.bot.send_message(ticket.user_id, f"Ответ от поддержки:
{text}")
                ticket.status = "closed"
                session.commit()
                await update.message.reply_text("Ответ отправлен.")
            current_admin_action.pop(user_id, None)
        elif action == "add_balance":
            context.user_data["target_user_id"] = text
            current_admin_action[user_id] = "input_amount"
            await update.message.reply_text("Введите сумму.")
        elif action == "input_amount":
            target_id = context.user_data.get("target_user_id")
            user = session.query(User).filter_by(telegram_id=int(target_id)).first()
            if user:
                user.balance += int(text)
                session.commit()
                await update.message.reply_text(f"Начислено {text} пользователю {target_id}.")
            current_admin_action.pop(user_id, None)
    else:
        action = current_admin_action.get(user_id)
        if action == "support":
            ticket = SupportTicket(user_id=user_id, message=text)
            session.add(ticket)
            session.commit()
            await update.message.reply_text("Ваше сообщение отправлено в поддержку.")
            for admin in ADMIN_IDS:
                await context.bot.send_message(admin, f"Новый тикет #{ticket.id} от {user_id}: {text}")
            current_admin_action.pop(user_id, None)

    session.close()
