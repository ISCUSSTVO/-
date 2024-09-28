from aiogram.types import InputMediaPhoto
#from sqlalchemy import select
from db.orm_query import orm_check_catalogs, orm_get_banner ,orm_check_catalog
#from db.models import Accounts
from inlinekeyboars.inline_kbcreate import get_services_btns, get_user_main_btns

from sqlalchemy.ext.asyncio import AsyncSession

from utils.paginator import Paginator



def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def main(session, menu_name, level):
    banner = await orm_get_banner(session, menu_name)

    if banner is None:
        # Обработка случая, когда баннер не найден
        return "Баннер не найден", get_user_main_btns(level=level)

    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_main_btns(level=level)

    return image, kbds


async def catalog(session):
    # Получаем баннер (если он нужен)
    banner = await orm_get_banner(session, 'catalog')

    # Получаем все аккаунты
    accounts = await orm_check_catalog(session)

    # Формируем сообщение с аккаунтами
    accounts_list = "\n".join([f"{account.gamesonaacaunt}" for account in accounts])  # Замените на актуальные поля

    if banner:
        image = InputMediaPhoto(
            media=banner.image,
            caption=(
                f"Игры:\n{accounts_list}"
            ),
        )
    else:
        image = None

    # Создаем кнопки с названиями игр
    game_buttons = []
    for account in accounts:
        button = {
            "text": account.gamesonaacaunt,  # Название игры
            "callback_data": f"game_{account.gamesonaacaunt}"  # Передаем название игры
        }
        game_buttons.append(button)
    
    kbds = {
        "inline_keyboard": [game_buttons]  
    }

    return image, kbds


async def gamecatalog(session: AsyncSession, game_name: str, page: int):
    # Получаем баннер (если он нужен)
    banner = await orm_get_banner(session, 'catalog')

    # Получаем все аккаунты для конкретной игры
    accounts = await orm_check_catalogs(session, game_name)

    print(f"Аккаунты на входе для игры '{game_name}': {accounts}")  # Отладочный вывод

    # Создаем экземпляр Paginator
    try:
        paginator = Paginator(accounts, page=page)  # Используем page как количество элементов на странице
    except ValueError as e:
        print(f"Ошибка пагинации: {e}")
        return None, None

    current_accounts = paginator.get_page()

    print(f"Текущие аккаунты на странице {page}: {current_accounts}")  # Отладочный вывод

    if not current_accounts:
        return None, None

    account = current_accounts[0]
    account_info = f"Аккаунт: {account.gamesonaacaunt}\n"

    if banner:
        image = InputMediaPhoto(
            media=banner.image,
            caption=account_info
        )
    else:
        image = None

    pagination_btns = pages(paginator)

    kbds = get_services_btns(
        pagination_btns=pagination_btns,
        level=page,  # Здесь передаем номер страницы
        page=page,
        service_id=123
    )

    return image, kbds



async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    page: int | None = None

):
    if level == 0:
        return await main(session=session, level=level, menu_name=menu_name)
    elif level == 1:
        return await catalog(session)
    elif level == 2:
        return await gamecatalog(session,level,page)



