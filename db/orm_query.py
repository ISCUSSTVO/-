from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Accounts, Banner

############### Работа с баннерами (информационными страницами) ###############

async def orm_add_banner_description(session: AsyncSession, data: dict):
    #Добавляем новый или изменяем существующий по именам
    #пунктов меню: main, about, cart, shipping, payment, catalog
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_add_catalog(session: AsyncSession, data: dict):
    obj = Accounts()(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
    )
    session.add(obj)
    await session.commit()

async def orm_check_catalog(session: AsyncSession):
    query = select(Accounts)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_accounts_by_game(session: AsyncSession, game_cat: str):
    query = select(Accounts).where(Accounts.categories == game_cat )
    result = await session.execute(query)
    accounts = result.scalars().all()
    return accounts

async def orm_get_accounts_by_game1(session: AsyncSession, game: str):
    query = select(Accounts).where(Accounts.gamesonaacaunt == game )
    result = await session.execute(query)
    accounts = result.scalars().all()
    return accounts



