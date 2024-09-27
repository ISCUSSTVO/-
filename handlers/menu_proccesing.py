from aiogram.types import InputMediaPhoto
#from sqlalchemy import select
from db.orm_query import orm_get_banner ,orm_check_catalog
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
    image = InputMediaPhoto(media = banner.image, caption=banner.description)

    kbds = get_user_main_btns(level=level)

    return image, kbds

async def catalog(session, level, page):
    services = await orm_check_catalog(session)

    paginator = Paginator(services, page=page)

    current_services = paginator.get_page()

    if current_services:
        service = current_services[0]
        image = InputMediaPhoto(
            media=service.image,
            caption=f"<strong>{service.name}</strong>\n{service.description}\nСтоимость: {round(service.price, 2)}\n"
                    f"<strong>Услуга {paginator.page} из {paginator.pages}</strong>",
        )
    else:
        image = None

    pagination_btns = pages(paginator)

    kbds = get_services_btns(
        level=level,
        page=page,
        pagination_btns=pagination_btns,
        service_id=service.id,
    )

    return image, kbds





async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    page: int | None = None,
):
    if level == 0:
        return await main(session=session, level=level, menu_name=menu_name)
    elif level == 1:
        image, kbds = await catalog(session, level, page)  # Распаковка значений
        return image, kbds

