from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.types import LabeledPrice
from db.engine import AsyncSessionLocal
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query import orm_check_catalog1, orm_get_accounts_by_game, orm_get_banner
from inlinekeyboars.inline_kbcreate import Menucallback, inkbcreate, get_keyboard
from aiogram.fsm.state import State, StatesGroup
from handlers.menu_proccesing import chek_code_guard, chek_mail, game_catalog, game_searching, get_menu_content, vidachalogs

user_router = Router()


account_list = [] 


@user_router.message(F.text.lower().contains('start'))
async def start(message: types.Message, session: AsyncSession):
    banner = await orm_get_banner(session, "about")
    msg = await message.answer_photo(photo=banner.image, caption = banner.description, reply_markup=get_keyboard(btns={
        'Главное меню',
        'Я уже купил аккаунт'
    }))  




@user_router.message(F.text.lower().contains('menu'))
@user_router.message(F.text.lower().contains('меню'))
async def menu (message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


@user_router.callback_query(Menucallback.filter())
async def user_manu(callback: types.CallbackQuery, callback_data: Menucallback, session: AsyncSession):

    result = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name
    )
    if result is None:
        await callback.answer("Не удалось получить данные.", show_alert=True)
        return
    media, reply_markup = result
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@user_router.callback_query(F.data.startswith('show_cat_'))
async def process_show_game(callback_query: types.CallbackQuery, session: AsyncSession):
    # Извлекаем категорию из колбек-данных
    game_cat = callback_query.data.split('_')[2]  # Получаем название категории
    message_text, kbds = await game_catalog(session, game_cat, level=3)
    # Отправляем сообщение пользователю
    await callback_query.message.edit_media(message_text, reply_markup=kbds)
    await callback_query.answer()


@user_router.callback_query(F.data.startswith('buyacc_'))
async def buy_acc(callback:types.CallbackQuery, session:AsyncSession):
    game = callback.data.split('_')[-1]
    image, kbds = await game_searching(session, game)
    await callback.message.edit_media(image, reply_markup=kbds)
    

@user_router.callback_query(F.data.startswith('buy_'))
async def send_invoice(callback_query:types.CallbackQuery, session: AsyncSession):
    game = callback_query.data.split('_')[-1]    
    account = await orm_get_accounts_by_game(session, game)
    for result in account:
        prices = [LabeledPrice(label=result.description, amount=result.price * 100)]  # Указываем цену в копейках
        banner = await orm_get_banner(session, 'catalog')
        await callback_query.message.answer_invoice(
            title='Оплата',
            description=result.gamesonaacaunt,
            payload='payload',
            provider_token='381764678:TEST:93111',  # Замените на ваш токен провайдера
            currency='RUB',
            prices=prices,
            #start_parameter='test',
            photo_url=banner.image if banner else None,
            photo_size=512,
            photo_width=512,
            photo_height=512,
            #need_name=True,
            need_phone_number=True,
            #need_email=True,
            is_flexible=False
        )
        await callback_query.answer()


@user_router.callback_query(F.data.startswith('oplatil_'))
async def oplata(callback: types.CallbackQuery, session:AsyncSession):
    game = callback.data.split('_')[-1]
    image, kbds = await vidachalogs(session, game)
    await callback.message.edit_media(image, reply_markup=kbds)



@user_router.callback_query(F.data.startswith('chek_mail_'))
async def chek_mail1(callback: types.CallbackQuery, session: AsyncSession):
    game = callback.data.split('_')[-1]

    qwe, result = await chek_mail(session, game)
    if result:
        await callback.message.answer(result)
    else:
        await callback.message.answer(qwe)
        



############################Получение кода купленного аккаунта############################
class GetCode(StatesGroup):
    mail = State()
    passw = State()

@user_router.message(F.text == ('Я уже купил аккаунт'))
async def handle_steam_guard(message: types.Message, state: FSMContext, session: AsyncSession):
    banner  = await orm_get_banner(session, "steam_guard")

   #image , caption= await take_code(session)
    await state.set_state(GetCode.mail)
    await message.answer_photo(photo=banner.image,caption= banner.description)
    await message.delete()
   


@user_router.message(GetCode.mail)
async def chek_code(message:types.Message, state: FSMContext):
    mail1 = message.text

    async with AsyncSessionLocal as session:  # Используйте
        res = await orm_check_catalog1(session, mail1)
    if res:
        await message.answer('Введи пароль')
        await state.update_data(email=mail1)
        await state.update_data(pas=res.imap)
        await state.set_state(GetCode.passw) 
    else: 
        await message.answer('Нет аккаунта с такой почтой')

@user_router.message(GetCode.passw)
async def chek_code1(message: types.Message, state: FSMContext, session: AsyncSession):
    password = message.text
    data = await state.get_data()
    mail = data.get('email') 
    passs = data.get('pas') 
    print(f"Введённый пароль: {password}, Сохранённый пароль: {passs}")
    
    if password == passs:
        qwe, extracted_phrase = await chek_code_guard(session, mail)
        
        if extracted_phrase is not None:
            await message.answer(extracted_phrase)
        else:
            await message.answer(qwe)
            
        await state.clear()
    else:
        await message.answer('Неверный пароль.')
        await state.clear()


################################################################



@user_router.message()
async def game_search(message: types.Message, session: AsyncSession):  
    game = message.text
    account_qwe = await orm_get_accounts_by_game(session, game)
    games_list = [account.gamesonaacaunt for account in account_qwe]
    if game not in games_list or not F.text:
        await message.answer('Напиши старт')
        return
    for account in account_qwe:
        account_info = (
            f"{account.description}\n" 
            f"Цена: {account.price} rub"
        )

        kbds = inkbcreate(btns={
                "Выбрать ✅":    f"buyacc_{account.gamesonaacaunt}"
        })
        await message.answer_photo(account.image,caption=account_info, reply_markup=kbds)
        await message.delete()