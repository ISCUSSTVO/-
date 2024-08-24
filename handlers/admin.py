from aiogram import types, Router
from aiogram.filters import Command, StateFilter
from sqlalchemy import delete, select
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Admlist, Accounts
from inlinekeyboars.inline_kbcreate import inkbcreate
import logging

logging.basicConfig(level=logging.INFO)

 





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
    accmail = State()
    accmailpasword = State()
    im4p = State()

    texts = {
        'addaccount.name':'Введите название заново',
        'addaccount.desc':'Введите описание заново',
        'addaccount.game':'Введите игры заново',
        'addaccount.categories':'Введите категории заново',
        'addaccount.priceacc':'Введите цену заново',
        'addaccount.accim':'Картинку заново',
        'addaccount.acclogin':'Введите логин  заново',
        'addaccount.accpasword':'Введите пароль заново',
        'addaccount.accmail':'Введите почту заново',
        'addaccount.accmailpasword':'Введите пароль от почты заново',
        'addaccount.im4p':'Введите im4p  заново'
    }



admin_list23 = ['krutoy_cell', 'Staryubogopodomniy', 'xuypisd']

@adm_router.message(Command('eta'))
async def evrytimeadm(message: types.Message, session: AsyncSession):
    # Проверяем, является ли пользователь администратором
    if message.from_user.username in admin_list23:
        # Проходим по каждому администратору из admin_list23
        for username in admin_list23:
            # Проверяем, существует ли уже этот юзер в базе данных
            result = await session.execute(select(Admlist).where(Admlist.usernameadm == username))
            existing_admin = result.scalars().first()

        if existing_admin is None:
            # Если пользователя нет в базе, добавляем его
            new_admin = Admlist(usernameadm=username)
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

@adm_router.callback_query(F.data==('admin'))
async def chek_adm1(cb: types.CallbackQuery, session: AsyncSession):
    await cb.message.answer(
        'Здарова броууууу', reply_markup=inkbcreate(btns={
            'Власть над админами': 'admcomm',
            'Власть над аккаунтами': 'acccomm'
        })
    )

    await cb.message.delete()


@adm_router.message(Command('ad'))
async def chek_adm(message: types.Message, session: AsyncSession):
    result = await session.execute(select(Admlist))
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
async def accadm(cb: types.CallbackQuery,):
    await cb.message.answer(
        'Что хочешь?',reply_markup=inkbcreate(btns={
            'Дабавить аккаунт': 'Plus_acc',
            'Изменить аккаунты': 'showall'
        })
        )


@adm_router.callback_query(F.data == ('Plus_adm'))
async def addadm(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Кого коронуем?')
    await state.set_state(addadminglobal.plusadm)  # Установите состояние правильно

@adm_router.message(addadminglobal.plusadm)
async def handle_username_to_add(msg: types.Message, session: AsyncSession, state: FSMContext):
    result = await session.execute(select(Admlist))
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
        newadm = Admlist(usernameadm=new_username)
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
@adm_router.callback_query(StateFilter(None), F.data == ('Plus_acc'))
async def addadmin1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Введи имя аккаунта'
    )
    await state.set_state(addaccount.name)

@adm_router.message(StateFilter('*'), F.text.casefold()==('отмена'))
async def cancel_hand(msg: types.Message, state: FSMContext):
    curstate = await state.get_state()
    if curstate is None:
        return
    await state.clear()
    await msg.answer('Отмена действия',reply_markup=inkbcreate(btns={
        'меню': 'admin'
    }))
    
@adm_router.message(F.text.casefold()==('назад'))
async def backstep(msg: types.Message,state: FSMContext):
    curstate = await state.get_state()
    if curstate == addaccount.name:
        await msg.answer(
            'Предыдущего шага нет'
        )
        return
    prev = None
    for step in addaccount.__all_states__:
        if step.state == curstate:
            await state.set_state(prev)
            await msg.answer(
                f"Вы вернулись к предыдущему шагу\n{addaccount.texts[prev.state]}"
            )
        prev = step

@adm_router.message(addaccount.name)
async def addname(message: types.Message, state: FSMContext):
    await state.update_data(accname = message.text)
    await message.answer(
        text='Введи описание аккаунта'
    )
    await state.set_state(addaccount.desc)

@adm_router.message(addaccount.desc)
async def addgame_desc(message: types.Message, state: FSMContext):
    await state.update_data(accdesc=message.text)
    await message.reply(
        'Введи игры на аккаунте'
    )
    await state.set_state(addaccount.game)

@adm_router.message(addaccount.game)
async def addgame_game(message: types.Message, state: FSMContext):
    await state.update_data(accgame=message.text)
    await message.reply(
        'Введи цену аккаунта'
    )
    await state.set_state(addaccount.priceacc)

@adm_router.message(addaccount.priceacc)
async def addpriceacc(message: types.Message, state: FSMContext):
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
async def addimage(message: types.Message, state: FSMContext):
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
async def addpassword(message: types.Message,state: FSMContext):
    await state.update_data(accnewpassword=message.text)
    await message.reply(
        'Теперь почту'
    )
    await state.set_state(addaccount.accmail)

@adm_router.message(addaccount.accmail)
async def addmail(message: types.Message,state: FSMContext):
    await state.update_data(accmail=message.text)
    await message.reply(
        'Теперь пароль от почты'
    )
    await state.set_state(addaccount.im4p)

@adm_router.message(addaccount.im4p)
async def addim4p(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(accim4p=message.text)
    data = await state.get_data()
    # Создаем новый объект аккаунта
    newaccgame = Accounts(
        name=data['accname'],
        description=data['accdesc'],
        gamesonaacaunt=data['accgame'],
        price=data['priceacc'],
        image=data['acccim'],  # Здесь будет правильный тип данных
        categories=data['acccat'],
        acclog=data['accnewlogin'],
        accpass=data['accnewpassword'],
        accmail = data['accmail'],
        im4p=data['accim4p']
    )
    image = data['acccim']
    qwe = data['accname']
    price = data['priceacc']

    # Добавляем и коммитим в сессии базы данных
    session.add(newaccgame)
    await session.commit()
    await state.clear()

    # Отправляем изображение вместе с текстом
    await message.reply_photo(
        photo=image,
        caption=f'Аккаунт добавлен\nНазвание: {qwe}\nЦена: {price}',
        reply_markup=inkbcreate(btns={
            'Ещё аккаунт?': 'Plus_acc',
            'Админ меню': 'admin'
        })
    )

@adm_router.callback_query(F.data == 'showall')
async def changeacc(cb: types.CallbackQuery, session: AsyncSession):
    result = await session.execute(select(Accounts))
    account_list = result.scalars().all()

    if account_list:
        for account in account_list:
            desc_name = account.name if account.name else "Без названия"
            account_info = (
                f"Аккаунт: {desc_name}\n"
                f"Игры: {account.gamesonaacaunt}\n"
                f"Цена: {account.price}"
            )
            reply_markup = inkbcreate(btns={
                f'Изменить {desc_name}': f'chgacc_{desc_name}',
                f'Удалить {desc_name}': f'delacc_{desc_name}'
            })

            if account.image:  # Проверяем, есть ли изображение
                await cb.message.answer_photo(photo=account.image, caption=account_info, reply_markup=reply_markup)
            else:
                await cb.message.answer(account_info, reply_markup=reply_markup)
    else:
        await cb.message.answer(
            'Нет аккаунтов, братик', reply_markup=inkbcreate(btns={
                'В меню': 'acccom'
            })
        )



@adm_router.callback_query(F.data == ('chgacc'))
async def chngacc(cb: types.CallbackQuery, session: AsyncSession):
    _, account_name, description = cb.data.split('_')
    
    # Получаем аккаунт из базы данных
    result = await session.execute(select(Accounts).where(Accounts.name == account_name))
    account = result.scalars().first()



@adm_router.callback_query(F.data.startswith('delacc_'))
async def dellgacc(cb: types.CallbackQuery, session: AsyncSession):
    logging.info(f"Удаление аккаунта: {cb.data}")
    desc_name = cb.data.split('_')[1]
    
    # Выполняем запрос на получение аккаунта по имени
    result = await session.execute(select(Accounts).where(Accounts.name == desc_name))
    accounts_to_remove = result.scalars().all()
    
    if accounts_to_remove:
        # Удаляем аккаунт из базы данных
        await session.execute(delete(Accounts).where(Accounts.name == desc_name))
        await session.commit()  # Подтверждаем изменения в базе данных
        
        await cb.answer(f"Аккаунт {desc_name} был удален")
        await cb.message.answer(
            f"Аккаунт {desc_name} был удален",
            reply_markup=inkbcreate(btns={
                'В главное меню': 'menu'
            })
        )
    else:
        await cb.answer(f"Аккаунт {desc_name} не найден.")

##################ПРОВЕРКА НА АДМИНА################################################################
@adm_router.callback_query(F.data ==('chekadm'))
async def chekadm(cb: types.CallbackQuery, session: AsyncSession):
    result = await session.execute(select(Admlist))
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
    result = await session.execute(select(Admlist))
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
        delete(Admlist).where(Admlist.usernameadm == username_to_delete)
    )
    await session.commit()
    
    await callback.message.answer(f'Администратор @{username_to_delete} удалён.')
    await callback.message.delete()
