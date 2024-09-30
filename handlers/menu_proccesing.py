from aiogram.types import InputMediaPhoto
#from sqlalchemy import select
from db.orm_query import orm_get_accounts_by_game, orm_get_banner ,orm_check_catalog
#from db.models import Account
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
    image = InputMediaPhoto(media = banner.image, caption=banner.description)

    kbds = get_user_main_btns(level=level)

    return image, kbds



async def catalog(session):
    # Получаем баннер (если он нужен)
    banner = await orm_get_banner(session, 'catalog')

    # Получаем все аккаунты
    accounts = await orm_check_catalog(session)

    # Формируем сообщение с аккаунтами
    accounts_list = "\n".join([f"{account.gamesonaacaunt}" for account in accounts])

    if banner:
        image = InputMediaPhoto(
            media=banner.image,
            caption=f"Игры:\n{accounts_list}",
        )
    else:
        image = None

    # Создаем кнопки с названиями игр
    game_buttons = []
    game_count = {}

    for account in accounts:
        game_name = account.gamesonaacaunt
        if game_name in game_count:
            game_count[game_name] += 1
        else:
            game_count[game_name] = 1

    # Создаем кнопки с учетом количества
    for game_name, count in game_count.items():
        game_buttons.append({
            "text": f"{game_name} ({count})",  # Название игры с количеством
            "callback_data": f"show_game_{game_name}"  # Передаем название игры
        })

    kbds = {
        "inline_keyboard": [game_buttons]
    }


    return image, kbds



async def gamecatalog(session, level, page, game_name):
    services = await orm_get_accounts_by_game(session, game_name)
    paginator = Paginator(services, page=page)

    current_services = paginator.get_page()

    if current_services:
        service = current_services[0]
        if service.image:
            image = InputMediaPhoto(
                media=service.image,
                caption=f"{service.name}\nОписание: {service.description}\nСтоимость: {round(service.price, 2)}\n"
                        f"Аккаунт {paginator.page} из {paginator.pages}",
            )
        else:
            image = None
    else:
        image = None

    pagination_btns = pages(paginator)

    kbds = get_services_btns(
        level=level,
        page=paginator.page,
        pagination_btns=pagination_btns,
        service_id=current_services[0].id if current_services else None,
    )
    
    return image, kbds





async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    game_name: str = None,
    page: int | None = None,
):
    if level == 0:
        return await main(session=session, level=level, menu_name=menu_name)
    
    if level == 1:
        return await catalog(session)

    elif level == 2:
        if game_name:
            return await gamecatalog(session, level, page, game_name)

    # Возвращаем значения по умолчанию
    return None


