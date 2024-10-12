from aiogram import types, Router
from aiogram.filters import Command, StateFilter
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Admins, Accounts
from db.orm_query import orm_change_account, orm_check_catalog, orm_del_account, orm_del_admin, orm_for_ETA, orm_get_info_pages, orm_change_banner_image, orm_use_admin, orm_update_catalog
from inlinekeyboars.inline_kbcreate import inkbcreate
from db.engine import AsyncSessionLocal


adm_router = Router()

adminlist = ['civqw']
####################################АВТОДОБАВЛЕНИЕ АДМИНА ИЗ ЛИСТА ADMINLIST####################################
@adm_router.message(Command('eta'))
async def Evry_Time_Adm(message: types.Message, session: AsyncSession):
    if message.from_user.username in adminlist:
        for username in adminlist:
            # Проверяем, существует ли уже этот юзер в базе данных
            existing_admin = await orm_for_ETA(session, username)
            
        if existing_admin is None:
            # Если пользователя нет в базе, добавляем его
            new_admin = Admins(usernameadm=username)
            session.add(new_admin)
            await session.commit()
            await message.answer(
                'Ты теперь админ'
            )
        else:
            await message.answer(
                'Ты и так админ '
        )
    else:
        await message.reply(
            'ты не админ'
        )
####################################АДМ МЕНЮ КОЛЛБЕК####################################

@adm_router.callback_query(F.data==('admin'))
async def admin_commands_cb(callback: types.CallbackQuery):
    await callback.message.answer(
        'Разделяй и властвуй', reply_markup=inkbcreate(btns={
            'Власть над админами': 'admcomm',
            'Власть над аккаунтами': 'acccomm',
            'Добавить изменить банер':  'banner'
        })
    )

    await callback.message.delete()

####################################АДМ МЕНЮ МСГ####################################
@adm_router.message(Command('ad'))
async def admin_commands_msg(message: types.Message, session: AsyncSession):
    admin_list = await orm_use_admin(session)
    admin_usernames = [admin.usernameadm for admin in admin_list]
    if message.from_user.username in admin_usernames:
        await message.answer(
            'Разделяй и властвуй', reply_markup=inkbcreate(btns={
                'Власть над админами': 'admcomm',
                'Власть над аккаунтами': 'acccomm',
                'Добавить изменить банер':  'banner'
                }))
        await message.delete()
    else:
        await message.answer(
            'ты не админ'
        )
        await message.delete()

###################################АДМ МЕНЮ####################################
@adm_router.callback_query(F.data == ('admcomm'))
async def comm_adm(cb: types.CallbackQuery,):
    await cb.message.answer(
        'Что хочешь??',reply_markup=inkbcreate(btns={
            'Добавить админа': 'Plus_adm',
            'Удалить админа': 'deladm',
            'Назад':    'admin'
        }, sizes=(3,))
    )
####################################МЕНЮ АККАУНТОВ####################################
@adm_router.callback_query(F.data == ('acccomm'))
async def acc_adm(cb: types.CallbackQuery,):
    await cb.message.answer(
        'Что хочешь?',reply_markup=inkbcreate(btns={
        
            'Дабавить аккаунт': 'Plus_acc',
            'Изменить аккаунты': 'showall',
            'Назад':    'admin'
        },sizes=(2,))
        )

####################################ДОБАВЛЕНИЕ АДМИНА####################################
class PlusAdmin(StatesGroup):
    plusadm = State()
user_data = {}

@adm_router.callback_query(F.data == ('Plus_adm'))
async def add_adm(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введи телеграм юз ')
    await state.set_state(PlusAdmin.plusadm)  

@adm_router.message(PlusAdmin.plusadm)
async def handle_username_to_add(msg: types.Message, session: AsyncSession, state: FSMContext):
    admins = await orm_use_admin(session)
    admin_usernames = [admin.usernameadm for admin in admins]

    new_username = msg.text.strip()  # Получаем имя пользователя из сообщения
    await state.update_data(newadmq=new_username)  # Обновляем данные состояния

    if new_username not in  admin_usernames:

        newadm = Admins(usernameadm=new_username)
        session.add(newadm)
        await session.commit()
        await msg.reply(f'@{new_username} теперь админ',reply_markup=inkbcreate(btns={
            'Ещё админ?': 'Plus_adm',
            'Админ меню': 'admcomm'
            }))
        await state.clear()

    else:
        await msg.answer(f' @{new_username} и так админ',reply_markup=inkbcreate(btns={
            'Ещё админ?': 'Plus_adm',
        'Админ меню': 'admcomm' 
        }))
        await state.clear()

################# Микро FSM для загрузки/изменения баннеров ############################

class AddBanner(StatesGroup):
    image = State()

# Отправляем перечень информационных страниц бота и становимся в состояние отправки photo
@adm_router.callback_query(StateFilter(None), F.data == ('banner'))
async def add_banner(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await cb.message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.image)

# Добавляем/изменяем изображение в таблице (там уже есть записанные страницы по именам:
# main, catalog, cart(для пустой корзины), about, payment, shipping
@adm_router.message(AddBanner.image, F.photo)
async def add_banner1(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите коректное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id,)
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()

# ловим некоррекный ввод
@adm_router.message(AddBanner.image)
async def add_banner2(message: types.Message):
    await message.answer("Отправьте фото баннера или напишите отмена")

##################Добавление аккаунта################################################################
class PlussAccount(StatesGroup):
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
        'PlussAccount.name':    'Введите название заново',
        'PlussAccount.desc':    'Введите описание заново',
        'PlussAccount.game':    'Введите игры заново',
        'PlussAccount.categories':  'Введите категории заново',
        'PlussAccount.priceacc':    'Введите цену заново',
        'PlussAccount.accim':   'Картинку заново',
        'PlussAccount.acclogin':    'Введите логин  заново',
        'PlussAccount.accpasword':  'Введите пароль заново',
        'PlussAccount.accmail': 'Введите почту заново',
        'PlussAccount.imap':    'Введите imap  заново'
    }

@adm_router.callback_query(F.data == ('Plus_acc'))
async def add_account(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.reply(
        text='Введи описание'
    )
    await state.set_state(PlussAccount.desc)

@adm_router.message(PlussAccount.desc)
async def add_game_desc(message: types.Message, state: FSMContext):
    await state.update_data(accdesc=message.text)
    await message.reply(
        'Введи игры на аккаунте'
    )
    await state.set_state(PlussAccount.game)

@adm_router.message(PlussAccount.game)
async def add_game_game(message: types.Message, state: FSMContext):
    await state.update_data(accgame=message.text)
    await message.reply(
        'Введи цену аккаунта'
    )
    await state.set_state(PlussAccount.priceacc)

@adm_router.message(PlussAccount.priceacc)
async def add_priceacc(message: types.Message, state: FSMContext):
    await state.update_data(priceacc=message.text)
    await message.reply(
        'Введи категории игр на аккаунте'
    )
    await state.set_state(PlussAccount.categories)

@adm_router.message(PlussAccount.categories)
async def add_categories(message: types.Message, state: FSMContext):
    await state.update_data(acccat=message.text)
    await message.reply(
        'Теперь картинку заглавной игры аккаунта'
    )
    await state.set_state(PlussAccount.accim)

@adm_router.message(PlussAccount.accim)
async def add_image(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data(acccim=message.photo[0].file_id)
    await message.reply(
        'Теперь логин '
    )
    await state.set_state(PlussAccount.acclogin)

@adm_router.message(PlussAccount.acclogin)
async def add_login(message: types.Message, state: FSMContext):
    await state.update_data(accnewlogin=message.text)
    await message.reply(
        'Теперь пароль от аккаунта'
    )
    await state.set_state(PlussAccount.accpasword)

@adm_router.message(PlussAccount.accpasword)
async def add_password(message: types.Message,state: FSMContext):
    await state.update_data(accnewpassword=message.text)
    await message.reply(
        'Теперь почту'
    )
    await state.set_state(PlussAccount.accmail)

@adm_router.message(PlussAccount.accmail)
async def add_mail(message: types.Message,state: FSMContext):
    await state.update_data(accmail=message.text)
    await message.reply(
        'Теперь пароль от почты'
    )
    await state.set_state(PlussAccount.imap)

@adm_router.message(PlussAccount.imap)
async def add_imap(message: types.Message, session: AsyncSession, state: FSMContext):
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
async def show_all_accounts(cb: types.CallbackQuery, session: AsyncSession):
    account_list = await orm_check_catalog(session)

    if account_list:
        for account in account_list:
            desc_name = account.description
            account_info = (
                f"Аккаунт: {desc_name}\n"
                f"Игры: {account.gamesonaacaunt}\n"
                f"Цена: {account.price}"
            )
            reply_markup = inkbcreate(btns={
                f'Изменить {desc_name}': f'chgacc_{desc_name}',
                f'Удалить {desc_name}': f'delacc_{desc_name}'
            })
            await cb.message.answer_photo(photo=account.image, caption=account_info, reply_markup=reply_markup)
    else:
        await cb.message.answer(
            'Нет аккаунтов, братик', reply_markup=inkbcreate(btns={
                'В меню': 'acccom'
            })
        )

##################Удаление аккаунта ################################################################
@adm_router.callback_query(F.data.startswith('delacc_'))
async def delete_acc(cb: types.CallbackQuery, session: AsyncSession):
    desc_name = cb.data.split('_')[1]
    await orm_del_account(session, desc_name )
    await session.commit()
    await cb.message.answer(f'Аккаунт {desc_name} удалён.')
    await cb.message.delete()

###СМЕНА ИНФОРМАЦИИ ОБ АКАУНТЕ###
@adm_router.callback_query(F.data.startswith('chgacc_'))
async def chng_acc(cb: types.CallbackQuery, session: AsyncSession):
    _, account_name = cb.data.split('_')
    account = await orm_change_account(session, account_name)
    
    await cb.message.answer(
        f"Вы выбрали аккаунт: {account.description}\n"
        f"Игры: {account.gamesonaacaunt}\n"
        f"Цена: {account.price}\n\n"
        "Что вы хотите изменить?",
        reply_markup=inkbcreate(btns={
            "Изменить игры": f"change_games_{account_name}",
            "Изменить цену": f"change_price_{account_name}",
            "Изменить описание": f"change_description_{account_name}",
            "Изменить категории": f"change_categories_{account_name}",
            "Изменить логин": f"change_login_{account_name}",
            "Изменить пароль": f"change_password_{account_name}",
            "Изменить почту": f"change_email_{account_name}",
            "Изменить изображение": f"change_image_{account_name}",
            "Изменить imap": f"change_imap_{account_name}"

        })
    )
    
    await cb.answer()


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
        'categories': "Введите новые категории",
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

@adm_router.message(StateFilter("new_categories"))
async def update_categories(message: types.Message, state: FSMContext):
    await update_account_field(message, state, 'categories')

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
        await orm_update_catalog(session, account_name, field_name, new_value)
        await session.commit()

    
    await message.answer(f"{field_name.replace('_', ' ').capitalize()} аккаунта обновлено на: {new_value}")
    await state.clear()



##################УДАЛЕНИЕ АДМИНА################################################################
@adm_router.callback_query(F.data == 'deladm')
async def delete_adm(callback: types.CallbackQuery, session: AsyncSession):
    admins = await orm_use_admin(session)
    if admins:
        btns = {f'Удалить @{admin.usernameadm}': f'delete_{admin.usernameadm}' for admin in admins}
        DellAdmKb = inkbcreate(btns=btns, sizes=(2,))
        
        await callback.message.answer('Список администраторов:', reply_markup=DellAdmKb)
    else:
        await callback.message.answer('Нет администраторов.')

@adm_router.callback_query(F.data.startswith('delete_'))
async def handle_delete_admin(callback: types.CallbackQuery, session: AsyncSession):
    username_to_delete = callback.data.split('_')[1].strip()

    await orm_del_admin(session, username_to_delete)
    await session.commit()
    
    await callback.message.answer(f'Администратор @{username_to_delete} удалён.')
    await callback.message.delete()

##################Назад к прошлому стейту, и отмена действия################################################################ 
@adm_router.message(F.text.casefold()==('назад'))
async def backstep(msg: types.Message,state: FSMContext):
    curstate = await state.get_state()
    if curstate == PlussAccount.name:
        await msg.answer(
            'Предыдущего шага нет'
        )
        return
    prev = None
    for step in PlussAccount.__all_states__:
        if step.state == curstate:
            await state.set_state(prev)
            await msg.answer(
                f"Вы вернулись к предыдущему шагу\n{PlussAccount.texts[prev.state]}"
            )
        prev = step

@adm_router.message(StateFilter('*'), F.text.casefold()==('отмена'))
async def cancel_hand(msg: types.Message, state: FSMContext):
    curstate = await state.get_state()
    if curstate is None:
        return
    await state.clear()
    await msg.answer('Отмена действия',reply_markup=inkbcreate(btns={
        'меню': 'admin'
    }))

