from aiogram.fsm.state import State, StatesGroup

class UserSteps(StatesGroup):
    WAITING_FOR_FILE = State()
    FILE_LOADED = State()
    WAITING_FOR_NAME = State()
    MESSAGES_EXTRACTED = State()
    WAITING_FOR_HYPOTHESIS = State()
    ANALYSIS_DONE = State()