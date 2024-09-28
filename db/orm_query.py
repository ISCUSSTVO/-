from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Accounts, Banner

############### Работа с баннерами (информационными страницами) ###############


async def orm_add_banner_description(session: AsyncSession, data: dict):
    query = select(Banner)
    result = await session.execute(query)
    
    if result.first():
        return  # Если уже есть баннеры, ничего не делаем

    # Добавляем новые баннеры
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()



async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()

async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    banner = result.scalar()

    if banner is None:
        # Логируем ошибку или обрабатываем ситуацию
        print(f"Banner not found for page: {page}")
        return None  # Возвращаем None, если баннер не найден

    return banner  # Возвращаем найденный баннер

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
    accounts = result.scalars().all()
    print(f"Найдено аккаунтов: {len(accounts)}")  # Отладочный вывод
    return accounts

async def orm_check_catalogs(session: AsyncSession, game_name: str):
    query = select(Accounts).where(Accounts.gamesonaacaunt == game_name)
    result = await session.execute(query)
    accounts = result.scalars().all()
    print(f"Найдено аккаунтов для игры '{game_name}': {len(accounts)}")  # Отладочный вывод
    return accounts
