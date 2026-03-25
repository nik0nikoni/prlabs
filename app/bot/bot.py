import httpx
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.api_client import TodoApiClient
from app.bot.utils.states import TaskCreate, TaskEdit, TaskGet, DeleteTask, EmailSend
from app.bot.utils.kb import main_menu_keyboard, task_actions_keyboard



api = None
BOT_TOKEN = '8600999895:AAE45Ihp0CuBkmrLeZTWIOnJnbp9uqg2MtM'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


def format_task(task: dict) -> str:
    task_id = task.get("id")
    title = task.get("title") or "-"
    desc = task.get("description") or "-"
    done = task.get("is_done", False)

    status = "✅ DONE" if done else "🕒 TODO"
    return (
        f"🧩 <b>Task #{task_id}</b>\n"
        f"<b>{title}</b>\n"
        f"{status}\n"
        f"📝 {desc}"
    )




@dp.callback_query(F.data == "email:send")
async def email_send_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(EmailSend.to)
    await callback.message.answer("✉️ Введите email получателя (to):")
    await callback.answer()


@dp.message(EmailSend.to)
async def email_send_to(message: Message, state: FSMContext):
    await state.update_data(to=message.text.strip())
    await state.set_state(EmailSend.subject)
    await message.answer("🧾 Введите тему письма (subject):")


@dp.message(EmailSend.subject)
async def email_send_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text.strip())
    await state.set_state(EmailSend.body)
    await message.answer("📝 Введите текст письма (body):")


@dp.message(EmailSend.body)
async def email_send_body(message: Message, state: FSMContext):
    data = await state.get_data()
    to = data["to"]
    subject = data["subject"]
    body = message.text

    try:
        res = await api.send_mail(to=to, subject=subject, body=body)
        # ожидаем что сервер вернёт {"status":"ok"} или {"status":"sent"...}
        await message.answer(f"✅ Письмо отправлено.\nОтвет сервера: {res}")

    except httpx.HTTPStatusError as e:
        # сервер вернул 4xx/5xx
        detail = None
        try:
            detail = e.response.json().get("detail")
        except Exception:
            detail = e.response.text

        await message.answer(f"❌ Ошибка сервера при отправке письма:\n{detail}")

    except Exception as e:
        await message.answer(f"❌ Ошибка клиента/сети:\n{e}")

    finally:
        await state.clear()
        await message.answer("Выбери действие:", reply_markup=main_menu_keyboard())


@dp.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer("Привет 👋\n\n""Я ToDo-бот. Выбери действие:", reply_markup=main_menu_keyboard())



@dp.callback_query(F.data == 'tasks:list')
async def get_tasks(callback: CallbackQuery):
    '''
    Вывод всех задач
    '''
    await callback.answer()
    if api is None:
        await callback.message.answer("API client is not initialized.")
        return

    tasks = await api.get_tasks()
    if not tasks:
        await callback.message.answer("📭 Список задач пуст.")
        return

    text = "\n\n".join(format_task(t) for t in tasks)
    await callback.message.answer(text, parse_mode='HTML')


# ----- Получение по айди ------------
@dp.callback_query(F.data == 'tasks:get')
async def get_task_id_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('🔍 Введи ID задачи (число):')
    await state.set_state(TaskGet.waiting_id)


@dp.message(TaskGet.waiting_id)
async def get_task_by_id(message: Message, state: FSMContext):
    text = (message.text or '').strip()

    if not text.isdigit():
        await message.answer('❗️ID должен быть числом. Введи ещё раз:')
        return
    
    task_id = int(text)
    task = await api.get_task(task_id=task_id)
    is_done = task.get('id_done', False)

    if not task:
        await message.answer('❌ Task not found.')
        await state.clear()
        return
    
    await message.answer(format_task(task), parse_mode='HTML', reply_markup=task_actions_keyboard(task_id=task_id, is_done=is_done))
    await state.clear()
    

# -----------------КОНЕЦ------------------------------------



# ---------------- УДАЛЕНИЕ ПО АЙДИ -------------------------------
@dp.callback_query(F.data == 'tasks:delete')
async def delete_task_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('🔍 Введи ID задачи (число):')
    await state.set_state(DeleteTask.waiting_id)


@dp.message(DeleteTask.waiting_id)
async def delete_task(message: Message, state: FSMContext):
    text = (message.text or '').strip()

    if not text.isdigit():
        await message.answer('❗️ID должен быть числом. Введи ещё раз:')
        return
    
    task_id = int(text)
    task = await api.delete_task(task_id=task_id)

    if not task:
        await message.answer('❌ Task not found.')
        await state.clear()
        return
    
    if task:
        await message.answer(f'🗑️ Task #{task_id} удалена.')
    else:
        await message.answer('❌ Task not found.')


    await state.clear()
# -------------------- КОНЕЦ -----------------


# ---------------- CREATE ------------------
@dp.callback_query(F.data == "tasks:create")
async def start_create_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("➕ Введи название задачи:")
    await state.set_state(TaskCreate.waiting_title)


@dp.message(TaskCreate.waiting_title)
async def set_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()
    if not title:
        await message.answer("❗️Название не должно быть пустым. Введи ещё раз:")
        return

    await state.update_data(title=title)
    await message.answer("📝 Теперь введи описание задачи (или '-' если без описания):")
    await state.set_state(TaskCreate.waiting_desc)


@dp.message(TaskCreate.waiting_desc)
async def set_desc_and_create(message: Message, state: FSMContext):
    desc = (message.text or "").strip()
    if not desc or desc == "-":
        desc = None

    data = await state.get_data()
    title = data["title"]

    task = await api.create_task(title=title, description=desc)
    await message.answer("✅ Задача создана!\n\n" + format_task(task), parse_mode="HTML")
    await state.clear()
# -----------------------------------------------------------


# ---------- UPDATE ---------------
@dp.callback_query(F.data.startswith("tasks:toggle:"))
async def toggle_task(callback: CallbackQuery):
    await callback.answer()

    task_id = int(callback.data.split(":")[2])

    task = await api.get_task(task_id=task_id)
    if not task:
        await callback.message.answer("❌ Task not found.")
        return

    new_done = not task.get("is_done", False)
    updated = await api.update_task(task_id=task_id, is_done=new_done)

    await callback.message.answer(
        "✅ Статус обновлён!\n\n" + format_task(updated),
        parse_mode="HTML",
        reply_markup=task_actions_keyboard(updated["id"], updated.get("is_done", False)),
    )


@dp.callback_query(F.data.startswith("tasks:edit_title:"))
async def ask_new_title(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    task_id = int(callback.data.split(":")[2])

    await state.update_data(task_id=task_id)
    await state.set_state(TaskEdit.waiting_title)
    await callback.message.answer("✏️ Введи новый заголовок:")


@dp.message(TaskEdit.waiting_title)
async def set_new_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()
    if not title:
        await message.answer("❗️Заголовок не должен быть пустым. Введи ещё раз:")
        return

    data = await state.get_data()
    task_id = data["task_id"]

    updated = await api.update_task(task_id=task_id, title=title)

    await message.answer(
        "✅ Заголовок обновлён!\n\n" + format_task(updated),
        parse_mode="HTML",
        reply_markup=task_actions_keyboard(updated["id"], updated.get("is_done", False)),
    )
    await state.clear()


@dp.callback_query(F.data.startswith("tasks:edit_desc:"))
async def ask_new_desc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    task_id = int(callback.data.split(":")[2])

    await state.update_data(task_id=task_id)
    await state.set_state(TaskEdit.waiting_desc)
    await callback.message.answer("📝 Введи новое описание (или '-' чтобы очистить):")


@dp.message(TaskEdit.waiting_desc)
async def set_new_desc(message: Message, state: FSMContext):
    desc = (message.text or "").strip()
    if desc == "-" or desc == "":
        desc = None

    data = await state.get_data()
    task_id = data["task_id"]

    updated = await api.update_task(task_id=task_id, description=desc)

    await message.answer(
        "✅ Описание обновлено!\n\n" + format_task(updated),
        parse_mode="HTML",
        reply_markup=task_actions_keyboard(updated["id"], updated.get("is_done", False)),
    )
    await state.clear()




async def main():
    global api
    api = TodoApiClient(base_url='http://backend:8000')
    
    try:
        await dp.start_polling(bot)
    finally:
        await api.close()

if __name__ == '__main__':
    asyncio.run(main())