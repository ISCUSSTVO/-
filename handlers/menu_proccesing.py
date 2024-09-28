from aiogram.types import InputMediaPhoto
from db.orm_query import orm_check_catalogs, orm_get_banner ,orm_check_catalog
#from db.models import Accounts
from inlinekeyboars.inline_kbcreate import get_services_btns, get_user_main_btns


from sqlalchemy.ext.asyncio import AsyncSession

from utils.paginator import Paginator



def pages(paginator: Paginator):
    btns = []

    if paginator.has_previous():
        btns.append(("◀ Пред.", "previous"))

    if paginator.has_next():
        btns.append(("След. ▶", "next"))

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
            "callback_data": f"game_{game_name}"  # Передаем название игры
        })

    kbds = {
        "inline_keyboard": [game_buttons]  
    }

    return image, kbds

async def gamecatalog(session: AsyncSession, game_name: str, page: int, level: int):
    # Получаем все аккаунты для конкретной игры
    accounts = await orm_check_catalogs(session, game_name)

    # Группируем аккаунты по игре
    grouped_accounts = {}
    for account in accounts:
        game = account.gamesonaacaunt
        if game not in grouped_accounts:
            grouped_accounts[game] = []
        grouped_accounts[game].append(account)

    # Создаем экземпляр Paginator
    try:
        paginator = Paginator(grouped_accounts.get(game_name, []), page=page)
    except ValueError as e:
        print(f"Ошибка пагинации: {e}")
        return None, None

    current_account = paginator.get_page()

    if not current_account:
        return None, None

    account = current_account[0]  # Берем текущий аккаунт для отображения
    account_info = f"Аккаунт: {account.name}\n{account.description}\nЦена: {account.price}"

    # Предполагаем, что у аккаунта есть поле image для картинки
    image = InputMediaPhoto(
        media=account.image,
        caption=account_info
    )
    kbds = get_services_btns(
        pagination_btns=pages(paginator),
        level=level,
        page=page,
        service_id=123
    )

    return image, kbds



async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    game_name: str,
    page: int | None = None,
    

):
    if level == 0:
        return await main(session=session, level=level, menu_name=menu_name)
    elif level == 1:
        return await catalog(session)
    elif level == 2:
        return await gamecatalog(session, page=page, level=level,game_name=game_name)



