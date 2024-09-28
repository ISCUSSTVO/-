from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



class Menucallback(CallbackData, prefix ="menu"):
    level: int
    menu_name: str
    page: int = 0



##################Создание инлайн клавиатуры  ################################################################
def inkbcreate(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,)):

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
            
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_user_main_btns(*, level:int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Аккаунты": "catalog",
        "О нас ": "about",
        "Оплата": "payment",
        }
    for text, menu_name  in btns.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text, callback_data=Menucallback(level=1, menu_name=menu_name).pack()))   
        elif menu_name == 'cart':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data =Menucallback(level=3, menu_name=menu_name).pack())) 
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data =Menucallback(level=level, menu_name=menu_name).pack()))   
            
    return keyboard.adjust(*sizes).as_markup()

def get_services_btns(
    *,
    level: int,
    page: int,
    pagination_btns: list,
    service_id: int,
    sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()

    # Уменьшаем уровень на 1 для кнопки "Назад"
    back_level = level - 1

    keyboard.add(InlineKeyboardButton(
        text='Назад',
        callback_data=Menucallback(level=back_level, menu_name='back').pack()
    ))

    keyboard.add(InlineKeyboardButton(
        text='Купить 💵',
        callback_data=Menucallback(
            level=level,
            menu_name='add_to_cart',
            service_id=service_id
        ).pack()
    ))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns:
        if menu_name == "next":
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=Menucallback(
                    level=level,  # Оставляем уровень неизменным
                    menu_name=menu_name,
                    page=page + 1
                ).pack()
            ))
        elif menu_name == "previous":
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=Menucallback(
                    level=level,  # Оставляем уровень неизменным
                    menu_name=menu_name,
                    page=page - 1
                ).pack()
            ))

    return keyboard.row(*row).as_markup()
