from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='📋Список задач', callback_data='tasks:list')
            ],
            [
                InlineKeyboardButton(text='➕Создать задачу', callback_data='tasks:create')
            ],
            [
                InlineKeyboardButton(text='🔍Получить по ID', callback_data='tasks:get'),
                InlineKeyboardButton(text='🗑️Удалить', callback_data='tasks:delete')
            ],
            # ===== NEW: EMAIL =====
            [
                InlineKeyboardButton(text='📧 Отправить письмо', callback_data='email:send'),
            ],
            [
                InlineKeyboardButton(text='📥 IMAP: входящие', callback_data='email:imap'),
                InlineKeyboardButton(text='📨 POP3: входящие', callback_data='email:pop3'),
                InlineKeyboardButton(text='webapp', url="http://127.0.0.1:8000")
            ],
        ]
    )


def task_actions_keyboard(task_id: int, is_done: bool) -> InlineKeyboardMarkup:
    toggle_text = "✅ Отметить DONE" if not is_done else "🕒 Вернуть TODO"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=toggle_text, callback_data=f"tasks:toggle:{task_id}")],
            [
                InlineKeyboardButton(text="✏️ Заголовок", callback_data=f"tasks:edit_title:{task_id}"),
                InlineKeyboardButton(text="📝 Описание", callback_data=f"tasks:edit_desc:{task_id}"),
            ],
        ]
    )

