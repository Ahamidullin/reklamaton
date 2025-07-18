from aiogram.fsm.state import State, StatesGroup

class CharacterCreation(StatesGroup):
    choosing_creation_method = State()
    prompt_based_description = State()
    prompt_based_name = State()
    prompt_based_avatar = State()
    constructor_based_archetype_group = State()
    constructor_based_archetype_type = State()
    constructor_based_communication_style = State()
    constructor_based_traits = State()
    constructor_based_name = State()
    constructor_based_avatar = State()
    preview = State()
    editing = State()
    editing_field = State() 