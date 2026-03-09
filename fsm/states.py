from aiogram.fsm.state import State, StatesGroup

class OnboardingStates(StatesGroup):
    waiting_for_time = State()
    adding_first_habit = State()
    choosing_habit_type = State()

class HabitStates(StatesGroup):
    waiting_for_name = State()
    choosing_type = State()
    setting_goal = State()

class HistoryStates(StatesGroup):
    browsing_date = State()
    editing_day = State()
