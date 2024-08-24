from sqlite3 import IntegrityError
from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram import F
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from inlinekeyboars.inline_kbcreate import inkbcreate
from db.models import Accounts, Backet

user_router = Router()


account_list = [] 


@user_router.message(F.text.lower().contains('старт'))
@user_router.message(CommandStart())
async def comm_start(message: types.Message):
    await message.answer(
        'Здарова', reply_markup=inkbcreate(btns={
            'Главное меню': 'menu',
        })
    )

@user_router.message(F.text.lower().contains('меню'))
@user_router.callback_query(F.data == ('menu'))
async def comm_cat(callback: types.CallbackQuery):
    await callback.message.answer(
        'Выбирай что ты хочешь', reply_markup=inkbcreate(btns={
            'Ваша корзина': 'checkbacket',
            'Категории игр': 'categ',
            'Все доступные аккаунты': 'allacc',
            'Поиск аккаунта с игрой': 'searchgame',
            'Определение категории по игре': 'search_cat_ongame'
        })
    )



@user_router.message(F.text.lower().contains('аккаунты'))
@user_router.callback_query(F.data == "allacc")
async def view_all_accounts(message_or_query: types.Message | types.CallbackQuery, session: AsyncSession):
    if isinstance(message_or_query, types.CallbackQuery):
        await message_or_query.answer()
        message = message_or_query.message
    else:
        message = message_or_query

    # Получаем все аккаунты из таблицы accounts
    result = await session.execute(select(Accounts))
    account_list = result.scalars().all()

    if account_list:
        for account in account_list:
            desc_name = account.name if account.name else "Без названия"
            description = account.description if account.description else "Нет описания"
            account_info = (
                f"Аккаунт: {desc_name}\n"
                f"Игры: {account.gamesonaacaunt}\n"
                f"Цена: {account.price}"
            )

            # Создаем инлайн-кнопку для каждого аккаунта
            inline_button = InlineKeyboardButton(text=f"Подробнее о {desc_name}", callback_data=f"details_{desc_name}_{description}")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])

            # Отправляем информацию об аккаунте с кнопкой "Подробнее" и изображением
            if account.image:  # Проверяем, есть ли изображение
                await message.answer_photo(photo=account.image, caption=account_info, reply_markup=keyboard)
            else:
                await message.answer(account_info, reply_markup=keyboard)
    else:
        await message.answer(
            'Нет аккаунтов братик', reply_markup=inkbcreate(btns={
                'В меню': 'menu'
            })
        )

@user_router.callback_query(F.data == 'categ')
async def categor(cb: types.CallbackQuery, session: AsyncSession):
    result = await session.execute(select(Accounts))
    account_list = result.scalars().all()
        
    if account_list:
        categories = {}
        # Группируем аккаунты по категориям
        for account in account_list:
            if account.categories not in categories:
                categories[account.categories] = []
            categories[account.categories].append(account)

        # Отправляем категории и создаем инлайн-кнопки
        for category_name in categories.keys():
            await cb.message.answer(
                f"Категория: {category_name}",
                reply_markup=inkbcreate(btns={
                    "Показать аккаунты": f'show_accounts:{category_name}'
                })
            )
    else:
        await cb.message.answer(
            'Нет категорий, братик', 
            reply_markup=inkbcreate(btns={
                'В меню': 'menu'
            })
        )

@user_router.callback_query(F.data.startswith('show_accounts:'))
async def show_accounts(cb: types.CallbackQuery, session: AsyncSession):
    category = cb.data.split(':')[1]  # Получаем категорию из callback_data
    result = await session.execute(select(Accounts).where(Accounts.categories == category))
    account_list = result.scalars().all()
    
    if account_list:
        for account in account_list:       
            await cb.message.answer_photo(
                photo=account.image , 
                caption=f"Имя: {account.name}\nИгры: {account.gamesonaacaunt}\nЦена: {account.price}",
                reply_markup=inkbcreate(btns={
                    f"Подробнее о {account.name}": f"details_{account.name}_{account.description}"
                })
            )
    else:
        await cb.message.answer(
            f'Нет аккаунтов в категории: {category}'
            )


@user_router.callback_query(F.data.startswith('details_'))
async def account_details(cb: types.CallbackQuery, session: AsyncSession):
    _, account_name, description = cb.data.split('_')
    
    # Получаем аккаунт из базы данных
    result = await session.execute(select(Accounts).where(Accounts.name == account_name))
    account = result.scalars().first()

    if account:
        account_info = (
            f"Имя: {account.name}\n"
            f"Описание: {description}\n"
            f"Игры: {account.gamesonaacaunt}\n"
            f"Цена: {account.price}"
        )
        
        # Создаем кнопки для добавления в корзину и выбора другого аккаунта
        buttons = {
            "Добавить в корзину": f"addback_{account.name}",
            "Выбрать другой аккаунт": "choose_another_account"
        }
        
        keyboard = inkbcreate(btns=buttons)

        await cb.message.answer(account_info, reply_markup=keyboard)
    else:
        await cb.message.answer("Аккаунт не найден.")

@user_router.callback_query(F.data == 'choose_another_account')
async def choose_another_account(cb: types.CallbackQuery, session: AsyncSession):
    # Логика для отображения списка доступных аккаунтов
    result = await session.execute(select(Accounts))
    accounts = result.scalars().all()

    if accounts:
        accounts_buttons = {account.name: f"details_{account.name}_{account.description}" for account in accounts}
        keyboard = inkbcreate(btns=accounts_buttons)

        await cb.message.answer("Выберите другой аккаунт:", reply_markup=keyboard)
    else:
        await cb.message.answer("Нет доступных аккаунтов.")

@user_router.callback_query(F.data.startswith('addback_'))
async def addback(cb: types.CallbackQuery, session: AsyncSession):
    account_name = cb.data.split('_')[1]  # Извлекаем имя аккаунта из callback_data

    # Получаем аккаунт из базы данных
    result = await session.execute(select(Accounts).where(Accounts.name == account_name))
    account = result.scalars().first()

    if account:
        user_id = cb.from_user.id 
        nameacc = account.name 
        info_acc = f"{account.acclog},{account.accpass}"
        imgacc = account.image 

        # Создаем новый объект Backet
        new_backet = Backet(username=user_id, image=imgacc, name=nameacc, infoacc=info_acc)

        try:
            session.add(new_backet)
            await session.commit()
            await cb.message.answer("Аккаунт успешно добавлен в корзину!",reply_markup=inkbcreate(btns={
                'В главное меню':   'menu',
                'Ещё аккаунт': ('allacc')
            }))
        except IntegrityError:
            await session.rollback()
            await cb.message.answer("Ошибка: аккаунт уже существует в корзине.",reply_markup=inkbcreate(btns={
                'В главное меню':   'menu',
                'Ещё аккаунт': ('allacc')
                }))
        except Exception as e:
            await session.rollback()
            await cb.message.answer(f"Произошла ошибка: {str(e)}")
    else:
        await cb.message.answer("Аккаунт не найден.")

@user_router.callback_query(F.data == 'searchgame')
async def search_game(callback: types.CallbackQuery):
    await callback.message.answer('Введи название игры')
    @user_router.message()
    async def process_game_name(message: types.Message, session: AsyncSession):
        game_name = message.text  # Получаем название игры от пользователя
    
        # Выполняем запрос к базе данных
        result = await session.execute(select(Accounts).where(Accounts.gamesonaacaunt.contains(game_name)))
        account_list = result.scalars().all()
    
        if account_list:
            for account in account_list:
                desc_name = account.description if account.description else "Без описания"
                price = account.price
                
                # Получаем список игр из аккаунта
                games_on_account = account.gamesonaacaunt.split(',')  # Предполагаем, что игры разделены запятыми
                games_list = "\n".join([f"- {game.strip()}" for game in games_on_account])
    
                # Формируем сообщение с информацией об аккаунте
                message_text = f"Аккаунт:\nОписание: {desc_name}\nЦена: {price}\nИгры на аккаунте:\n{games_list}"
    
                # Отправляем сообщение с информацией об аккаунте
                await message.answer(message_text, reply_markup=inkbcreate(btns={
                    'Найти ещё': 'searchgame',
                    'В главное меню': 'menu'
                }))
        else:
            await message.answer("К сожалению, аккаунты с искомой игрой не найдены.", reply_markup=inkbcreate(btns={
                'Другая игра?': 'searchgame',
                'В главное меню': 'menu'
            }))


@user_router.callback_query(F.data == 'checkbacket')
async def chekback(cb: types.CallbackQuery, session: AsyncSession):
    user_id = cb.from_user.id

    # Получаем все элементы корзины для данного пользователя
    result = await session.execute(select(Backet).where(Backet.username == user_id))
    backet_items = result.scalars().all()

    if not backet_items:
        await cb.message.answer("Ваша корзина пуста.")
        return

    account_messages = []

    for item in backet_items:
        # Разделяем информацию об аккаунте на логин и пароль
        login, password = item.infoacc.split(',')

        # Получаем аккаунт из базы данных по логину и паролю
        account_result = await session.execute(
            select(Accounts).where(Accounts.acclog == login, Accounts.accpass == password)
        )
        account = account_result.scalars().first()

        if account:
            # Формируем сообщение с информацией об аккаунте
            account_info = (
                f"Имя: {account.name}\n"
                f"Цена: {account.price}\n"
                f"Игры на аккаунте: {account.gamesonaacaunt}\n"
            )

            # Кнопки для взаимодействия
            buttons = {
                "Оплатить": f"pay_{account.name}",
                "Убрать из корзины": f"remove_{account.name}"
            }
            keyboard = inkbcreate(btns=buttons)

            account_messages.append((account_info, keyboard))
        else:
            account_messages.append(("Аккаунт не найден в системе.", None))

    # Отправляем сообщения с информацией об аккаунтах
    for account_info, keyboard in account_messages:
        await cb.message.answer_photo(photo=account.image, caption=account_info, reply_markup=keyboard if keyboard else None)

    await cb.answer()

@user_router.callback_query(F.data.startswith('pay_'))
async def pay_account(cb: types.CallbackQuery,):
    account_name = cb.data.split('_')[1]
    # Логика обработки оплаты (например, отправка пользователю информации о способах оплаты)
    await cb.answer(f"Вы выбрали оплату для аккаунта: {account_name}")


@user_router.callback_query(F.data.startswith('remove_'))
async def remove_from_backet(cb: types.CallbackQuery, session: AsyncSession):
    account_name = cb.data.split('_')[1]
    username = cb.from_user.id
    result = await session.execute(select(Backet).where(Backet.username == username, Backet.name == account_name))
    accounts_to_remove = result.scalars().all()
    if accounts_to_remove:
        await session.execute(delete(Backet).where(Backet.username == username, Backet.name == account_name))
        await cb.message.answer(f"Аккаунт {account_name} был убран из корзины.",reply_markup=inkbcreate(btns={
            'В главное меню': 'menu'
        }))
        await session.commit()
    else:
        await cb.message.answer(f"Аккаунт {account_name} не найден в корзине.")

@user_router.message()
async def qwe(message: types.Message):
    await message.answer(
        text='Мужик нажми на интерисующую комманду', reply_markup=inkbcreate(btns={
                'В меню': 'menu'
        })
    )


