from aiogram import types, Router
from aiogram.filters import Command, StateFilter
from sqlalchemy import delete, select, update
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Admlist, Accounts
from db.orm_query import orm_get_info_pages, orm_change_banner_image
from inlinekeyboars.inline_kbcreate import inkbcreate
import logging
from db.engine import AsyncSessionLocal


logging.basicConfig(level=logging.INFO)

 





adm_router = Router()


class addadminglobal(StatesGroup):
    plusadm = State()
user_data = {}

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
    imap = State()

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
        'addaccount.imap':'Введите imap  заново'
    }



adminlist = ['civqw']
####################################АВТОДОБАВЛЕНИЕ АДМИНА ИЗ ЛИСТА ADMINLIST####################################
@adm_router.message(Command('eta'))
async def evrytimeadm(message: types.Message, session: AsyncSession):
    # Проверяем, является ли пользователь администратором
    if message.from_user.username in adminlist:
        # Проходим по каждому администратору из admin_list23
        for username in adminlist:
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
            'ты не админ'
        )
####################################АДМ МЕНЮ КОЛЛБЕК####################################
@adm_router.message(Command('ad'))
@adm_router.callback_query(F.data==('admin'))
async def chek_adm1(cb_or_msg: types.CallbackQuery | types.Message, session: AsyncSession):
    if isinstance(cb_or_msg, types.CallbackQuery):
        await cb_or_msg.answer()
        message = cb_or_msg.message
    else:
        message = cb_or_msg
    result = await session.execute(select(Admlist))
    admin_list = result.scalars().all()
    admin_usernames = [admin.usernameadm for admin in admin_list]
    if message.from_user.username in admin_usernames:
        await message.answer(
            'Здарова броууууу', reply_markup=inkbcreate(btns={
                'Власть над админами': 'admcomm',
                'Власть над аккаунтами': 'acccomm',
                'Добавить изменить банер':  'banner'
            })
        )
    else:
        await message.answer(
            'ты не админ'
        )
        await message.delete()

####################################АДМ МЕНЮ МСГ####################################
#@adm_router.message(Command('ad'))
#async def chek_adm(message: types.Message, session: AsyncSession):
#   result = await session.execute(select(Admlist))
#   admin_list = result.scalars().all()
#   admin_usernames = [admin.usernameadm for admin in admin_list]
#   if message.from_user.username in admin_usernames:
#       await message.answer(
#           'Здарова броууууу', reply_markup=inkbcreate(btns={
#               'Власть над админами': 'admcomm',
#               'Власть над аккаунтами': 'acccomm'
#           })
#       )
#   else:
#       await message.answer(
#           'ты не админ'
#       )
#       await message.delete()
###################################АДМ МЕНЮ####################################
@adm_router.callback_query(F.data == ('admcomm'))
async def commadm(cb: types.CallbackQuery,):
    await cb.message.answer(
        'Что хочешь??',reply_markup=inkbcreate(btns={
            'Добавить админа': 'Plus_adm',
            'Удалить админа': 'deladm',
            'Админ лист':   'chekadm'
        })
    )
####################################МЕНЮ АККАУНТОВ####################################
@adm_router.callback_query(F.data == ('acccomm'))
async def accadm(cb: types.CallbackQuery,):
    await cb.message.answer(
        'Что хочешь?',reply_markup=inkbcreate(btns={
            'Дабавить аккаунт': 'Plus_acc',
            'Изменить аккаунты': 'showall'
        })
        )

####################################ДОБАВЛЕНИЕ АДМИНА####################################
@adm_router.callback_query(F.data == ('Plus_adm'))
async def addadm(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('ВВеди юз ')
    await state.set_state(addadminglobal.plusadm)  # Установите состояние правильно

@adm_router.message(addadminglobal.plusadm)
async def handle_username_to_add(msg: types.Message, session: AsyncSession, state: FSMContext):
    result = await session.execute(select(Admlist))
    admins = result.scalars().all()
    admin_usernames = [admin.usernameadm for admin in admins]

    new_username = msg.text.strip()  # Получаем имя пользователя из сообщения
    await state.update_data(newadmq=new_username)  # Обновляем данные состояния

    if new_username in admin_usernames:
        await msg.answer(f' @{new_username} и так админ',reply_markup=inkbcreate(btns={
            'Ещё админ?': 'Plus_adm',
            'Админ меню': 'admcomm'
        }))
        await state.clear()
    else:
        newadm = Admlist(usernameadm=new_username)
        session.add(newadm)
        await session.commit()
        await msg.reply(f'@{new_username} теперь админ',reply_markup=inkbcreate(btns={
            'Ещё админ?': 'Plus_adm',
            'Админ меню': 'admcomm'
            }))
        await state.clear()
    await msg.answer(
        f'Список админов: {", ".join(adm.usernameadm for adm in admins)}'
    )




##################Отмена действия ################################################################
@adm_router.message(StateFilter('*'), F.text.casefold()==('отмена'))
async def cancel_hand(msg: types.Message, state: FSMContext):
    curstate = await state.get_state()
    if curstate is None:
        return
    await state.clear()
    await msg.answer('Отмена действия',reply_markup=inkbcreate(btns={
        'меню': 'admin'
    }))


################# Микро FSM для загрузки/изменения баннеров ############################

class AddBanner(StatesGroup):
    image = State()

# Отправляем перечень информационных страниц бота и становимся в состояние отправки photo
@adm_router.callback_query(StateFilter(None), F.data == ('banner'))
async def add_image2(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await cb.message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.image)

# Добавляем/изменяем изображение в таблице (там уже есть записанные страницы по именам:
# main, catalog, cart(для пустой корзины), about, payment, shipping
@adm_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите нормальное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id,)
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()

# ловим некоррекный ввод
@adm_router.message(AddBanner.image)
async def add_banner2(message: types.Message):
    await message.answer("Отправьте фото баннера или отмена")
##################Назад к прошлому стейту################################################################ 
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
##################Добавление аккаунта################################################################
@adm_router.callback_query(StateFilter(None), F.data == ('Plus_acc'))
async def addadmin1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Введи описание'
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
    await state.set_state(addaccount.imap)

@adm_router.message(addaccount.imap)
async def addimap(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(accimap=message.text)
    data = await state.get_data()
    # Создаем новый объект аккаунта
    newaccgame = Accounts(
        description=data['accdesc'],
        gamesonaacaunt=data['accgame'],
        price=data['priceacc'],
        image=data['acccim'],  # Здесь будет правильный тип данных
        categories=data['acccat'],
        acclog=data['accnewlogin'],
        accpass=data['accnewpassword'],
        accmail = data['accmail'],
        imap=data['accimap']
    )
    image = data['acccim']
    qwe = data['accdesc']
    price = data['priceacc']

    # Добавляем и коммитим в сессии базы данных
    session.add(newaccgame)
    await session.commit()
    await state.clear()

    # Отправляем изображение вместе с текстом
    await message.reply_photo(
        photo=image,
        caption=f'Аккаунт добавлен\nОписание: {qwe}\nЦена: {price} rub',
        reply_markup=inkbcreate(btns={
            'Ещё аккаунт?': 'Plus_acc',
            'Админ меню': 'admin'
        })
    )
###АККАУНТЫ ДЛЯ ИЗМЕНЕНИЯ\УДАЛЕНИЯ###
@adm_router.callback_query(F.data == 'showall')
async def showallaccounts(cb: types.CallbackQuery, session: AsyncSession):
    result = await session.execute(select(Accounts))
    account_list = result.scalars().all()

    if account_list:
        for account in account_list:
            desc_name = account.description if account.description else "Без названия"
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

###СМЕНА ИНФОРМАЦИИ ОБ АКАУНТЕ###
@adm_router.callback_query(F.data.startswith('chgacc_'))
async def chngacc(cb: types.CallbackQuery, session: AsyncSession):
    _, account_name = cb.data.split('_')
    
    # Получаем информацию об аккаунте из базы данных
    result = await session.execute(select(Accounts).where(Accounts.description == account_name))
    account = result.scalar_one_or_none()

    await cb.message.answer(
        f"Вы выбрали аккаунт: {account.name}\n"
        f"Игры: {account.gamesonaacaunt}\n"
        f"Цена: {account.price}\n\n"
        "Что вы хотите изменить?",
        reply_markup=inkbcreate(btns={
            "Изменить игры": f"change_games_{account_name}",
            "Изменить цену": f"change_price_{account_name}",
            "Изменить описание": f"change_description_{account_name}",
            "Изменить логин": f"change_login_{account_name}",
            "Изменить пароль": f"change_password_{account_name}",
            "Изменить почту": f"change_email_{account_name}",
            "Изменить изображение": f"change_image_{account_name}",
            "Изменить imap": f"change_imap_{account_name}"

        })
    )
    
    await cb.answer()  # Убираем уведомление о нажатой кнопке


###СМЕНА ИНФОРМАЦИИ ОБ АКАУНТЕ КОНКРЕТНО ПО ПУНКТАМ###
@adm_router.callback_query(F.data.startswith('change_'))
async def process_change_selection(cb: types.CallbackQuery, state: FSMContext):
    _, change_type, account_name = cb.data.split('_')

    # Сохраняем имя аккаунта в состоянии
    await state.update_data(account_name=account_name)

    prompts = {
        'games': "Введите новые игры:",
        'price': "Введите новую цену:",
        'description': "Введите новое описание:",
        'login': "Введите новый логин:",
        'password': "Введите новый пароль:",
        'email': "Введите новую почту:",
        'image': "Введите URL нового изображения:",
        'imap': "Введите новое imap:"
    }

    if change_type in prompts:
        await cb.message.answer(prompts[change_type])
        await state.set_state(f"new_{change_type}")


@adm_router.message(StateFilter("new_games"))
async def update_games(message: types.Message, state: FSMContext):
    await update_account_field(message, state, 'gamesonaacaunt')

@adm_router.message(StateFilter("new_price"))
async def update_price(message: types.Message, state: FSMContext):
    await update_account_field(message, state, 'price')

@adm_router.message(StateFilter("new_description"))
async def update_description(message: types.Message, state: FSMContext):
    await update_account_field(message, state, 'description')

@adm_router.message(StateFilter("new_login"))
async def update_login(message: types.Message, state: FSMContext):
    await update_account_field(message, state, 'login')

@adm_router.message(StateFilter("new_password"))
async def update_password(message: types.Message, state: FSMContext):
    await update_account_field(message, state, 'password')

@adm_router.message(StateFilter("new_email"))
async def update_email(message: types.Message, state: FSMContext):
    await update_account_field(message, state, 'email')

@adm_router.message(StateFilter("new_image"))
async def update_image(message: types.Message, state: FSMContext):
    await update_account_field(message, state, 'image_url')

@adm_router.message(StateFilter("new_imap"))
async def update_imap(message: types.Message, state: FSMContext):
    await update_account_field(message, state, 'imap')

async def update_account_field(message: types.Message, state: FSMContext, field_name: str):
    new_value = message.text
    user_data = await state.get_data()
    account_name = user_data.get('account_name')

    
    async with AsyncSessionLocal as session:  # Используйте AsyncSessionLocal
        await session.execute(
            update(Accounts).where(Accounts.name == account_name).values({field_name: new_value})
        )
    await session.commit()

    
    await message.answer(f"{field_name.replace('_', ' ').capitalize()} аккаунта обновлено на: {new_value}")
    await state.clear()
##################Удаление аккаунта ################################################################
@adm_router.callback_query(F.data.startswith('delacc_'))
async def dellgacc(cb: types.CallbackQuery, session: AsyncSession):
    desc_name = cb.data.split('_')[1]
    await session.execute(
    delete(Accounts).where(Accounts.description ==desc_name)
    )
    await session.commit()
    await cb.message.answer(f'Аккаунт {desc_name} удалён.')
    await cb.message.delete()

##################Список админов################################################################
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