from aiogram import types
from aiogram.types import InputMediaPhoto
from aiogram import Router

# from sqlalchemy import select
from db.orm_query import orm_get_accounts_by_game, orm_get_banner, orm_check_catalog

# from db.models import Account
from inlinekeyboars.inline_kbcreate import get_services_btns3, get_user_main_btns


from sqlalchemy.ext.asyncio import AsyncSession

from utils.paginator import Paginator

menu_router = Router()


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def main(session, menu_name, level):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_user_main_btns(level=level)

    return image, kbds


async def categ(session):
    # Получаем баннер (если он нужен)
    banner = await orm_get_banner(session, "catalog")

    # Получаем все аккаунты
    accounts = await orm_check_catalog(session)

    # Формируем сообщение с аккаунтами
    accounts_list = "\n".join([f"{account.categories}" for account in accounts])

    if banner:
        image = InputMediaPhoto(
            media=banner.image,
            caption=f"Категории:\n{accounts_list}",
        )
    else:
        image = None

    # Создаем кнопки с названиями игр
    game_buttons = []
    game_count = {}

    for account in accounts:
        game_cat = account.categories
        if game_cat in game_count:
            game_count[game_cat] += 1
        else:
            game_count[game_cat] = 1

    # Создаем кнопки с учетом количества
    for game_cat, count in game_count.items():
        game_buttons.append(
            {
                "text": f"{game_cat}",  # Название игры с количеством
                "callback_data": f"show_cat_{game_cat}",  # Передаем название игры
            }
        )

    kbds = {"inline_keyboard": [game_buttons]}

    return image, kbds


async def gamecatalog(session: AsyncSession, game_cat: str, level, page):
    # Получаем игры по категории из базы данных
    games = await orm_get_accounts_by_game(session, game_cat)
    paginator = Paginator(games, page=page)
    service = paginator.get_page()[0]
    # Формируем список игр для отображения
    if games:
        games_list = "\n".join(
            [f"{game.gamesonaacaunt}: {game.description}" for game in games]
        )  # Предполагается, что у игры есть поля name и description

    kbds = get_services_btns3(
        level=level,
        service_id=service.id,
    )

    return games_list, kbds


async def handle_game_selection(
    callback_query: types.CallbackQuery, session, game_name, level, page
):
    image, kbds = await viewgame(session, level, page, game_name)
    print(image, kbds)
    if image is None or kbds is None:
        print(image, kbds)
        await callback_query.answer(
            "Не удалось получить данные об игре.", show_alert=True
        )
        return

    media = InputMediaPhoto(
        media=image.media,
        caption=image.caption,
    )
    await callback_query.message.edit_media(media=media, reply_markup=kbds)


async def viewgame(session, level, page, game_name):
    services = await orm_get_accounts_by_game(session, game_name)
    paginator = Paginator(services, page=page)

    service = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=service.image,
        caption=f"\nОписание: {service.description}\nСтоимость: {round(service.price, 2)} rub\n"
        f"Аккаунт {paginator.page} из {paginator.pages}",
    )

    kbds = get_services_btns3(
        level=level,
        service_id=service.id,
    )

    return image, kbds


async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    game_cat: str = None,
    page: int | None = None,
):
    if level == 0:
        return await main(session=session, level=level, menu_name=menu_name)

    elif level == 1:
        return await categ(session)

    elif level == 2:
        return await gamecatalog(session, game_cat, level, page)

    elif level == 3:
        return await viewgame(session, level, page, game_cat)

    # Возвращаем значения по умолчанию
    return None
