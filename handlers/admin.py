from aiogram import types, Router
from aiogram.filters import Command
from sqlalchemy import delete, select
from db.models import admlist, accounts
from inlinekeyboars.inline_kbcreate import inkbcreate
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession


adm_router = Router()


class addadminglobal(StatesGroup):
    plusadm = State()


class addaccount(StatesGroup):
    game = State()
    categories = State()
    acclogin = State()
    accpasword = State()



admin_list23 = ['krutoy_cell']

@adm_router.message(Command('eta'))
async def evrytimeadm(message: types.Message, session: AsyncSession):
    # Проверяем, является ли пользователь администратором
    if message.from_user.username in admin_list23:
        # Проходим по каждому администратору из admin_list23
        for username in admin_list23:
            # Проверяем, существует ли уже этот юзер в базе данных
            result = await session.execute(select(admlist).where(admlist.usernameadm == username))
            existing_admin = result.scalars().first()

            if existing_admin is None:
                # Если пользователя нет в базе, добавляем его
                new_admin = admlist(usernameadm=username)
                session.add(new_admin)
                await session.commit()
                await message.answer(
                    'да брат ты опять админ'
                )
            else:
                await message.answer(
                    'ты всегда админ брат'
            )
    else:
        await message.reply(
            'а ты просто хуесос ди нахуй'
        )


@adm_router.message(Command('admin'))
async def chek_adm(message: types.Message, session: AsyncSession):
    result = await session.execute(select(admlist))
    admin_list = result.scalars().all()

    admin_usernames = [admin.usernameadm for admin in admin_list]

    if message.from_user.username in admin_usernames:
        await message.answer(
            'Здарова броууууу', reply_markup=inkbcreate(btns={
                'Добавить админа': 'Plus_adm',
                'Добавить аккаунт': 'Plus_acc',
                'Добавить категорию': 'Plus_cat'
            }, sizes=(2,))
        )
    else:
        await message.answer(
            'Динахуй тварь ебанная'
        )
        await message.delete()


@adm_router.callback_query(F.data == ('Plus_adm'))
async def addadm(callback: types.CallbackQuery, session: AsyncSession):
    # Получаем список администраторов из базы данных
    result = await session.execute(select(admlist))
    admins = result.scalars().all()

    # Извлекаем юзернеймы администраторов
    admin_usernames = [admin.usernameadm for admin in admins]

    # Проверяем, является ли пользователь администратором
    if callback.from_user.username in admin_usernames:
        await callback.message.answer('кого коронуем?')
        
        # Ожидаем следующий ввод от пользователя
        @adm_router.message()
        async def handle_username_to_add(msg: types.Message):
            username_to_add = msg.text.strip()

            if username_to_add in admin_usernames:
                await msg.answer(f'лох @{username_to_add} уже не лох')
            else:
                # Добавляем нового администратора в базу данных
                new_admin = admlist(usernameadm=username_to_add)
                session.add(new_admin)
                await session.commit()
                await msg.answer(
                    f'лох @{username_to_add} коронован'
                )

    else:
        await callback.message.reply(
            'пшёл нахуй пёс'
        )


@adm_router.callback_query(F.data == ('Plus_acc'))
async def addadmin1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Введи игры, которые есть на аккаунте'
    )
    await state.set_state(addaccount.game)

@adm_router.message(addaccount.game)
async def addgame(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(accgame=message.text)
    await message.reply(
        'Теперь логин или почту от аккаунта'
    )
    await state.set_state(addaccount.categories)

@adm_router.message(addaccount.categories)
async def addgame(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(acccat=message.text)
    await message.reply(
        'Теперь логин или почту от аккаунта'
    )
    await state.set_state(addaccount.acclogin)

@adm_router.message(addaccount.acclogin)
async def addlogin(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(accnewlogin=message.text)
    await message.reply(
        'теперь пароль'
    )
    await state.set_state(addaccount.accpasword)

@adm_router.message(addaccount.accpasword)
async def addpassword(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(accnewpassword=message.text)
    data = await state.get_data()
    newaccgame = accounts(
        gamesonaacaunt=data['accgame'],
        categories=data['acccat'],
        acclog=data['accnewlogin'],
        accpass=data['accnewpassword'],
    )

    session.add(newaccgame)
    await session.commit()

    await message.reply(
        'Аккаунт добавлен'
    )
    
    newacc = await session.execute(select(accounts))
    newacc = newacc.scalars().all()
    await state.clear()
    
    await message.answer(
        f'Текущий список аккаунтов: {", ".join(acc.gamesonaacaunt for acc in newacc)}'
    )


    
@adm_router.message(Command('chekadm'))
async def chekadm(message: types.Message, session: AsyncSession):
    result = await session.execute(select(admlist))
    admins = result.scalars().all()
    admin_usernames = [admin.usernameadm for admin in admins]
    if message.from_user.username in admin_usernames:
        if admins:
            admin_usernames = [admin.usernameadm for admin in admins]
            admin_list = "\n".join(admin_usernames)
            await message.answer(
                f'Список администраторов:\n{admin_list}'
            )
        else:
            await message.answer(
                'В базе данных нет администраторов.'
            )
    else:
        await message.reply(
            'Ты ничтожество ебнное динахуй'
        )

@adm_router.message(Command('delladm'))
async def delladm(message: types.Message, session: AsyncSession):
    # Получаем список администраторов из базы данных
    result = await session.execute(select(admlist))
    admins = result.scalars().all()

    # Извлекаем юзернеймы администраторов
    admin_usernames = [admin.usernameadm for admin in admins]

    # Проверяем, является ли пользователь администратором
    if message.from_user.username in admin_usernames:
        if admins:
            admin_list = "\n".join(admin_usernames)
            await message.answer(
                f'Список администраторов:\n{admin_list}\n\nВведите юзернейм администратора для удаления:'
            )
            
            # Ожидаем следующий ввод от пользователя
            @adm_router.message()
            async def handle_username_to_delete(msg: types.Message):
                username_to_delete = msg.text.strip()
                

                if username_to_delete in admin_usernames:

                    await session.execute(
                        delete(admlist).where(admlist.username == username_to_delete)
                    )
                    await session.commit()
                    await msg.answer(f'лох @{username_to_delete} унижен')
                else:
                    await msg.answer(f'лоха @{username_to_delete} несуществует')
        
        else:
            await message.answer('нихуя тут нет.')
    else:
        await message.answer('ты чмооооооооо')
    
