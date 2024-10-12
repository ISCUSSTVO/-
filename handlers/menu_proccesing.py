from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query import orm_get_category, orm_get_banner, orm_check_catalog
from inlinekeyboars.inline_kbcreate import back_kbds, get_user_main_btns





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
    for game_cat in game_count:
        game_buttons.append(
            {
                "text": f"{game_cat}",  # Название игры с количеством
                "callback_data": f"show_cat_{game_cat}",  # Передаем название игры
            }
        )

    kbds = {"inline_keyboard": [game_buttons]}

    return image, kbds


async def game_catalog(session: AsyncSession, game_cat: str, level):
    banner = await orm_get_banner(session, "catalog")
    # Получаем игры по категории из базы данных
    games = await orm_get_category(session, game_cat)
    # Формируем список игр для отображения
    games_list = "\n".join(
        [f"`{game.gamesonaacaunt}`" for game in games]
    )  
    
    if banner:
        image = InputMediaPhoto(
            media=banner.image,
            caption=f"Игры:\n{games_list}",
            parse_mode='MarkdownV2'
        )
    else:
        image = None
    
    kbds = back_kbds(
        level=level,
    )

    return image, kbds



async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    game_cat: str = None,
):
    if level == 0:
        return await main(session=session, level=level, menu_name=menu_name)

    elif level == 1:
        return await categ(session)

    elif level == 2:
        return await game_catalog(session, game_cat, level)