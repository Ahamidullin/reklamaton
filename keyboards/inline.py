from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    buttons = [
        [InlineKeyboardButton(text="🎭 Выбрать персонажа", callback_data="select_character")],
        [InlineKeyboardButton(text="✨ Создать нового", callback_data="create_character")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def character_list_keyboard(characters):
    buttons = []
    for char in characters:
        button = [InlineKeyboardButton(text=char.name, callback_data=f"character_{char.id}")]
        buttons.append(button)
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def character_card_keyboard(character_id):
    buttons = [
        [InlineKeyboardButton(text="✅ Начать диалог", callback_data=f"start_dialogue_{character_id}")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_character_{character_id}")],
        [InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="select_character")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard 

def creation_method_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📝 Задать промптом", callback_data="creation_prompt")],
        [InlineKeyboardButton(text="🛠️ Использовать конструктор", callback_data="creation_constructor")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard 

def skip_keyboard(callback_data: str):
    buttons = [
        [InlineKeyboardButton(text="Пропустить", callback_data=callback_data)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard 

def preview_keyboard():
    buttons = [
        [InlineKeyboardButton(text="✅ Сохранить и начать чат", callback_data="save_character")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_character")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard 

def archetype_group_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Аналитики (INTJ, INTP, ENTJ, ENTP)", callback_data="archetype_group_analysts")],
        [InlineKeyboardButton(text="Дипломаты (INFJ, INFP, ENFJ, ENFP)", callback_data="archetype_group_diplomats")],
        [InlineKeyboardButton(text="Стражи (ISTJ, ISFJ, ESTJ, ESFJ)", callback_data="archetype_group_sentinels")],
        [InlineKeyboardButton(text="Искатели (ISTP, ISFP, ESTP, ESFP)", callback_data="archetype_group_explorers")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="create_character")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard 

def archetype_type_keyboard(types):
    buttons = []
    row = []
    for mbti_type in types:
        row.append(InlineKeyboardButton(text=mbti_type, callback_data=f"archetype_type_{mbti_type}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="creation_constructor")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard 

def communication_style_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Формальный", callback_data="comm_style_formal"),
            InlineKeyboardButton(text="Литературный", callback_data="comm_style_literary")
        ],
        [
            InlineKeyboardButton(text="Неформальный", callback_data="comm_style_informal"),
            InlineKeyboardButton(text="Сленг (Gen Z)", callback_data="comm_style_gen_z")
        ],
        [
            InlineKeyboardButton(text="Сквернословие", callback_data="comm_style_profanity"),
            InlineKeyboardButton(text="Детский лепет", callback_data="comm_style_baby_talk")
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="creation_constructor")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard 

def traits_keyboard(sarcasm=1, humor=1, flirt=1, unpredictability=1, black_humor=False):
    buttons = [
        [
            InlineKeyboardButton(text="Сарказм:", callback_data="noop"),
            InlineKeyboardButton(text="-", callback_data="trait_decr_sarcasm"),
            InlineKeyboardButton(text=str(sarcasm), callback_data="noop"),
            InlineKeyboardButton(text="+", callback_data="trait_incr_sarcasm")
        ],
        [
            InlineKeyboardButton(text="Юмор:", callback_data="noop"),
            InlineKeyboardButton(text="-", callback_data="trait_decr_humor"),
            InlineKeyboardButton(text=str(humor), callback_data="noop"),
            InlineKeyboardButton(text="+", callback_data="trait_incr_humor")
        ],
        [
            InlineKeyboardButton(text="Флирт:", callback_data="noop"),
            InlineKeyboardButton(text="-", callback_data="trait_decr_flirt"),
            InlineKeyboardButton(text=str(flirt), callback_data="noop"),
            InlineKeyboardButton(text="+", callback_data="trait_incr_flirt")
        ],
        [
            InlineKeyboardButton(text="Непредсказуемость:", callback_data="noop"),
            InlineKeyboardButton(text="-", callback_data="trait_decr_unpredictability"),
            InlineKeyboardButton(text=str(unpredictability), callback_data="noop"),
            InlineKeyboardButton(text="+", callback_data="trait_incr_unpredictability")
        ],
        [
            InlineKeyboardButton(text="Черный юмор:", callback_data="noop"),
            InlineKeyboardButton(text="✅ Да" if black_humor else "❌ Нет", callback_data="trait_toggle_black_humor")
        ],
        [InlineKeyboardButton(text="Продолжить", callback_data="trait_continue")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard 

def edit_options_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Изменить имя", callback_data="edit_option_name")],
        [InlineKeyboardButton(text="Изменить описание/черты", callback_data="edit_option_description")],
        [InlineKeyboardButton(text="Изменить/добавить изображение", callback_data="edit_option_avatar")],
        [InlineKeyboardButton(text="✅ Сохранить изменения", callback_data="edit_save")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard 