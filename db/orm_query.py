from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Accounts, Admins, Banner

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


############### Работа с каталогами###############
async def orm_check_catalog(session: AsyncSession):
    query = select(Accounts)
    result = await session.execute(query)
    return result.scalars().all()
async def orm_check_catalog1(session: AsyncSession, user_data):
    query = select(Accounts).where(Accounts.accmail == user_data[0])
    result = await session.execute(query)
    return result.scalars().all()
############### Работа с админским хендлером###############
async def orm_use_admin(session: AsyncSession):
    query = select(Admins)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_category(session: AsyncSession, game_cat: str ):
    query = select(Accounts).where(Accounts.categories == game_cat )
    result = await session.execute(query)
    return result.scalars().all()

async def orm_for_ETA(session: AsyncSession, username: str ):
    query = select(Admins).where(Admins.usernameadm == username)
    result = await session.execute(query)
    return result.scalars().first()

async def orm_change_account(session: AsyncSession, account_name:str):
    query = select(Accounts).where(Accounts.description == account_name)
    result = await session.execute(query)
    return result.scalars().first()

async def orm_get_accounts_by_game(session: AsyncSession, game: str):
    query = select(Accounts).where(Accounts.gamesonaacaunt == game )
    result = await session.execute(query)
    return result.scalars().all()

async def orm_del_account(session: AsyncSession, desc_name : str):
    query = delete(Accounts).where(Accounts.description ==desc_name)
    result = await session.execute(query)
    return result

async def orm_del_admin(session: AsyncSession, username_to_delete : str):
    query = delete(Admins).where(Admins.usernameadm == username_to_delete)
    result = await session.execute(query)
    return result

async def orm_update_catalog(session: AsyncSession, account_name : str, field_name: str, new_value: str ):
    query = update(Accounts).where(Accounts.description == account_name).values({field_name: new_value})
    result = await session.execute(query)
    return result



