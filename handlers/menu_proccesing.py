from aiogram import types
import aiogram
from aiogram.types import InputMediaPhoto
from aiogram import Router

# from sqlalchemy import select
from db.orm_query import orm_get_accounts_by_game, orm_get_banner, orm_check_catalog, orm_get_accounts_by_game1

# from db.models import Account
from inlinekeyboars.inline_kbcreate import get_services_btns, get_services_btns3, get_user_main_btns


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


async def gamecatalog(session: AsyncSession, game_cat: str, level):
    banner = await orm_get_banner(session, "catalog")
    # Получаем игры по категории из базы данных
    games = await orm_get_accounts_by_game(session, game_cat)
    # Формируем список игр для отображения
    games_list = "\n".join(
        [f"`{game.gamesonaacaunt}`" for game in games]  # Используем * для жирного шрифта
    )  
    if banner:
        image = InputMediaPhoto(
            media=banner.image,
            caption=f"Игры:\n{games_list}",
            parse_mode='MarkdownV2')
    else:
        image = None
    kbds = get_services_btns3(
        level=level,
    )

    return image, kbds




async def handle_game_selection(
    message: types.Message, session, game, level, page
):
    image, kbds = await viewgame(session, level, page, game)
    print(image, kbds)
    if image is None or kbds is None:
        print(image, kbds)
        await message.answer(
            "Не удалось получить данные об игре.", show_alert=True
        )
        return

    media = InputMediaPhoto(
        media=image.media,
        caption=image.caption,
    )
    try:
        await message.edit_media(media=media, reply_markup=kbds)
    except aiogram.exceptions.TelegramBadRequest as e:
        print(f"Error editing message: {e}")
        await message.answer(f"Не удалось отредактировать сообщение.{e}")

async def viewgame(session, level, page, game):
    services = await orm_get_accounts_by_game1(session, game)
    paginator = Paginator(services, page=page)

    service_page = paginator.get_page()
    service = service_page[0]

    image = InputMediaPhoto(
        media=service.image,
        caption=f"\nОписание: {service.description}\nСтоимость: {round(service.price, 2)} rub\n"
        f"Аккаунт {paginator.page} из {paginator.pages}",
    )
    pagination_btns = pages(paginator)
    kbds = get_services_btns(
        level=level,
        page=page,
        pagination_btns=pagination_btns,
        service_id = service.id
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
        return await gamecatalog(session, game_cat, level)

    elif level == 3:
        return await viewgame(session, level, page, game_cat)
    # Возвращаем значения по умолчанию
    return None
