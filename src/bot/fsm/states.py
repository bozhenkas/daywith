from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    waiting_for_time = State()
    adding_first_habit = State()
    choosing_habit_type = State()


class HabitStates(StatesGroup):
    waiting_for_name = State()
    choosing_type = State()
    setting_goal = State()
    waiting_for_rename = State()


class HistoryStates(StatesGroup):
    waiting_for_date = State()


class SettingsStates(StatesGroup):
    waiting_for_tz = State()
    waiting_for_tz_manual = State()
