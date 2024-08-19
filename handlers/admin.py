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
    name = State()
    desc = State()
    game = State()
    categories = State()
    priceacc = State()
    accim = State()
    acclogin = State()
    accpasword = State()




admin_list23 = ['krutoy_cell', 'Staryubogopodomniy']

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
            'ты просто хуесос ди нахуй'
        )


@adm_router.message(Command('ad'))
async def chek_adm(message: types.Message, session: AsyncSession):
    result = await session.execute(select(admlist))
    admin_list = result.scalars().all()

    admin_usernames = [admin.usernameadm for admin in admin_list]

    if message.from_user.username in admin_usernames:
        await message.answer(
            'Здарова броууууу', reply_markup=inkbcreate(btns={
                'Власть над админами': 'admcomm',
                'Власть над аккаунтами': 'acccomm'
            })
        )
    else:
        await message.answer(
            'Динахуй тварь ебанная'
        )
        await message.delete()

@adm_router.callback_query(F.data == ('admcomm'))
async def commadm(cb: types.CallbackQuery,):
    await cb.message.answer(
        'Что хочешь??',reply_markup=inkbcreate(btns={
            'Добавить админа': 'Plus_adm',
            'Удалить админа': 'deladm',
            'Админ лист':   'chekadm'
        })
    )

@adm_router.callback_query(F.data == ('acccomm'))
async def commadm(cb: types.CallbackQuery,):
    await cb.message.answer(
        'Что хочешь?',reply_markup=inkbcreate(btns={
            'Дабавить аккаунт': 'Plus_acc',
            'Изменить аккаунт': 'Chenge_acc',
            'Удалить аккаунт': 'Del_acc'
        })
        )


@adm_router.callback_query(F.data == ('Plus_adm'))
async def addadm(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Кого коронуем?')
    await state.set_state(addadminglobal.plusadm)  # Установите состояние правильно

@adm_router.message(addadminglobal.plusadm)
async def handle_username_to_add(msg: types.Message, session: AsyncSession, state: FSMContext):
    result = await session.execute(select(admlist))
    admins = result.scalars().all()
    admin_usernames = [admin.usernameadm for admin in admins]

    new_username = msg.text.strip()  # Получаем имя пользователя из сообщения
    await state.update_data(newadmq=new_username)  # Обновляем данные состояния

    if new_username in admin_usernames:
        await msg.answer(f'Лох @{new_username} не лох',reply_markup=inkbcreate(btns={
            'Ещё админ?': 'Plus_adm',
            'Админ меню': 'admcomm'
        }))
        await state.clear()
    else:
        newadm = admlist(usernameadm=new_username)
        session.add(newadm)
        await session.commit()
        await msg.reply(f'Лох @{new_username} коронован',reply_markup=inkbcreate(btns={
            'Ещё админ?': 'Plus_adm',
            'Админ меню': 'admcomm'
            }))
        await state.clear()

    
    await msg.answer(
        f'Список админов: {", ".join(adm.usernameadm for adm in admins)}'
    )


##################Добавление аккаунта################################################################
@adm_router.callback_query(F.data == ('Plus_acc'))
async def addadmin1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Введи имя аккаунта'
    )
    await state.set_state(addaccount.name)

@adm_router.message(addaccount.name)
async def addname(message: types.Message, state: FSMContext):
    await state.update_data(accname = message.text)
    await message.answer(
        text='Введи описание аккаунта'
    )
    await state.set_state(addaccount.desc)

@adm_router.message(addaccount.desc)
async def addgame_desc(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(accdesc=message.text)
    await message.reply(
        'Введи игры на аккаунте'
    )
    await state.set_state(addaccount.game)

@adm_router.message(addaccount.game)
async def addgame_game(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(accgame=message.text)
    await message.reply(
        'Введи цену аккаунта'
    )
    await state.set_state(addaccount.priceacc)

@adm_router.message(addaccount.priceacc)
async def addgame_game(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(priceacc=message.text)
    await message.reply(
        'Введи категории игр на аккаунте'
    )
    await state.set_state(addaccount.categories)

@adm_router.message(addaccount.categories)
async def addcategories(message: types.Message, state: FSMContext):
    await state.update_data(acccat=message.text)
    await message.reply(
        'Теперь картинку заглавной игры аккаунта'
    )
    await state.set_state(addaccount.accim)

@adm_router.message(addaccount.accim)
async def addcategories(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data(acccim=message.photo[0].file_id)
    await message.reply(
        'Теперь логин или почту от аккаунта'
    )
    await state.set_state(addaccount.acclogin)

@adm_router.message(addaccount.acclogin)
async def addlogin(message: types.Message, state: FSMContext):
    await state.update_data(accnewlogin=message.text)
    await message.reply(
        'Теперь пароль'
    )
    await state.set_state(addaccount.accpasword)

@adm_router.message(addaccount.accpasword)
async def addpassword(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(accnewpassword=message.text)
    
    # Получаем данные состояния
    data = await state.get_data()
    
    # Создаем новый объект аккаунта
    newaccgame = accounts(
        name=data['accname'],
        description=data['accdesc'],
        gamesonaacaunt=data['accgame'],
        price=data['priceacc'],
        image=data['acccim'],  # Здесь будет правильный тип данных
        categories=data['acccat'],
        acclog=data['accnewlogin'],
        accpass=data['accnewpassword'],
    )

    # Добавляем и коммитим в сессии базы данных
    session.add(newaccgame)
    await session.commit()
    await state.clear()

    await message.reply(
        'Аккаунт добавлен'
    )
    await message.answer(
        f'Текущий список аккаунтов: {", ".join(acc.description for acc in newaccgame)}'
    )

##################ПРОВЕРКА НА АДМИНА################################################################

    
@adm_router.callback_query(F.data ==('chekadm'))
async def chekadm(cb: types.CallbackQuery, session: AsyncSession):
    result = await session.execute(select(admlist))
    admins = result.scalars().all()
    admin_usernames = [admin.usernameadm for admin in admins]
    if admins:
        admin_usernames = [admin.usernameadm for admin in admins]
        admin_list = "\n".join(admin_usernames)

        await cb.message.answer(
        f'Список администраторов:\n{admin_list}'
        )
    else:
            await cb.message.answer(
                'В базе данных нет администраторов.'
            )

##################УДАЛЕНИЕ АДМИНА################################################################
@adm_router.callback_query(F.data == 'deladm')
async def delladm(callback: types.CallbackQuery, session: AsyncSession):
    result = await session.execute(select(admlist))
    admins = result.scalars().all()
    
    if admins:
        btns = {f'Удалить @{admin.usernameadm}': f'delete_{admin.usernameadm}' for admin in admins}
        reply_markup = inkbcreate(btns=btns, sizes=(2,))
        
        await callback.message.answer('Список администраторов:', reply_markup=reply_markup)
    else:
        await callback.message.answer('Нет администраторов.')

@adm_router.callback_query(F.data.startswith('delete_'))
async def handle_delete_admin(callback: types.CallbackQuery, session: AsyncSession):
    username_to_delete = callback.data.split('_')[1].strip()
    
    # Удаляем администратора из базы данных
    await session.execute(
        delete(admlist).where(admlist.usernameadm == username_to_delete)
    )
    await session.commit()
    
    await callback.message.answer(f'Администратор @{username_to_delete} удалён.')
    await callback.message.delete()
