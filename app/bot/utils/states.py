from aiogram.fsm.state import StatesGroup, State


class TaskGet(StatesGroup):
    waiting_id = State()


class DeleteTask(StatesGroup):
    waiting_id = State()


class TaskCreate(StatesGroup):
    waiting_title = State()
    waiting_desc = State()



class TaskEdit(StatesGroup):
    waiting_title = State()
    waiting_desc = State()



class EmailSend(StatesGroup):
    to = State()
    subject = State()
    body = State()