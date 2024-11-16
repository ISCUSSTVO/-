import asyncio
import email
import imaplib
import re
from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query import orm_check_catalog1, orm_get_accounts_by_game, orm_get_category, orm_get_banner, orm_check_catalog
from inlinekeyboars.inline_kbcreate import back_kbds, get_user_main_btns, inkbcreate, inkburlcreate



IMAP_SERVER = "imap.mail.ru"
SMTP_SERVER = "smtp.mail.ru"
shop_id = 506751
async def main(session, menu_name, level):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_main_btns(level=level)
    return image, kbds


async def categ(session):
    # Получаем баннер (если он нужен)
    banner = await orm_get_banner(session, "catalog")

    # Получаем все аккаунты
    accounts = await orm_check_catalog(session)


    if banner:
        image = InputMediaPhoto(
            media=banner.image,
            caption="Категории:\n",
        )
    else:
        image = None

    # Создаем кнопки с названиями игр
    game_buttons = []
    game_count = {}

    for account in accounts:
        game_cat = account.categories
        if game_cat in game_count:
            game_count[game_cat] += 1
        else:
            game_count[game_cat] = 1

    # Создаем кнопки с учетом количества
    for game_cat in game_count:
        game_buttons.append(
            {
                "text": f"{game_cat}",  # Название игры с количеством
                "callback_data": f"show_cat_{game_cat}",  # Передаем название игры
            }
        )

    kbds = {"inline_keyboard": [game_buttons]}

    return image, kbds


async def game_catalog(session: AsyncSession, game_cat: str, level):
    banner = await orm_get_banner(session, "catalog")
    # Получаем игры по категории из базы данных
    games = await orm_get_category(session, game_cat)
    # Формируем список игр для отображения
    games_list = "\n".join(
        [f"`{game.gamesonaacaunt}`" for game in games]
    )  
    
    if banner:
        image = InputMediaPhoto(
            media=banner.image,
            caption=f"Игры:\n{games_list}\nНажмите на название игры и вставьте в чат ",
            parse_mode='MarkdownV2'
        )
    else:
        image = None
    
    kbds = back_kbds(
        level=level,
    )

    return image, kbds


async def game_searching(session: AsyncSession, game: str):
    account_qwe = await orm_get_accounts_by_game(session, game)
    banner = await orm_get_banner(session, "catalog")
    image = None
   
    for account in account_qwe:  # Проходим по всем найденным услугам
        account_info = (
            f'Аккаунт: {account.description}\n Цена: {account.price} rub'
        )

        if banner:
            image = InputMediaPhoto(
                media=banner.image,
                caption=account_info
            )
        


        kbds = inkbcreate(btns={
            'Оплатить 💸': f'buy_{account.gamesonaacaunt}'
        })
    return image, kbds


       
async def vidachalogs(session: AsyncSession, game:str):
    account_qwe = await orm_get_accounts_by_game(session, game)
    banner = await orm_get_banner(session, "catalog")
    image = None
    for account in account_qwe:  # Проходим по всем найденным услугам
        account_info = (
            f"Логин:    {account.acclog}\nПороль:   {account.accpass}"
        )
        if banner:
            image = InputMediaPhoto(
                media=banner.image,
                caption=account_info
            )
        kbds = inkbcreate(btns={
            "Проверить почту":    f'chek_mail_{account.gamesonaacaunt}'
        })

        return image, kbds

async def chek_mail(session: AsyncSession, game: str):
    qwe = None
    extracted_phrase = None
    result = await orm_get_accounts_by_game(session, game)
    for account in result:
        user_data = (account.accmail, account.imap)
        try:
            loop = asyncio.get_event_loop()
            # Создание цикла событий asyncio

            if user_data is None:
               # await callback.message.answer("Не удалось получить данные из почтового ящика")
                return
            # Проверка наличия данных пользователя из почтового ящика

            mail_connection = await loop.run_in_executor(
                None, lambda: imaplib.IMAP4_SSL(IMAP_SERVER)
            )
            # Установка защищенного соединения с почтовым сервером

            mail_connection.login(user_data[0], user_data[1])
            mail_connection.select("INBOX")
            # Вход в почтовый ящик и выбор папки "INBOX"

            status, data = mail_connection.search(None, "FROM", '"Steam"')
            # Поиск писем от Steam

            latest_email_id = data[0].split()[-1]
            status, data = mail_connection.fetch(latest_email_id, "(RFC822)")
            # Извлечение последнего письма от Steam

            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            # Извлечение содержимого письма

            decoded_payload = None
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        decoded_payload = part.get_payload(decode=True).decode("utf-8")
                        break
            else:
                decoded_payload = email_message.get_payload(decode=True).decode("utf-8")
            # Декодирование содержимого письма

            if decoded_payload:
                match = re.search(r'Россия(.*?)Если это были не вы', decoded_payload, re.DOTALL)
                extracted_phrase = match.group(1).strip()
                #await callback.message.answer(f"{extracted_phrase}")
            #else:
               # await callback.message.answer("Не удалось декодировать содержимое письма")
            # Извлечение кода доступа из письма и отправка его пользователю

        except Exception as e:
            qwe = (f'Произошла ошибка при чтении почты обратитесь к администратору:\n{e}')
        finally:
            if "mail_connection" in locals():
                mail_connection.logout()
    return qwe, extracted_phrase

async def chek_code_guard(session: AsyncSession, mail: str):
    qwe = "Успешно"  # Инициализируем значение по умолчанию
    extracted_phrase = None

    result = await orm_check_catalog1(session, mail)
    if result is None:
        return "Не удалось найти данные пользователя.", None

    user_data = (result.accmail, result.imap)

    try:
        loop = asyncio.get_event_loop()

        mail_connection = await loop.run_in_executor(
            None, lambda: imaplib.IMAP4_SSL(IMAP_SERVER)
        )

        mail_connection.login(user_data[0], user_data[1])
        mail_connection.select("INBOX")

        status, data = mail_connection.search(None, "FROM", '"Steam"')
        if not data[0]:  # Проверка на наличие писем
            return "Нет писем от Steam.", None

        latest_email_id = data[0].split()[-1]
        status, data = mail_connection.fetch(latest_email_id, "(RFC822)")
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)

        decoded_payload = None
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    decoded_payload = part.get_payload(decode=True).decode("utf-8")
                    break
        else:
            decoded_payload = email_message.get_payload(decode=True).decode("utf-8")

        if decoded_payload:
            match = re.search(r'Россия(.*?)Если это были не вы', decoded_payload, re.DOTALL)
            if match:
                extracted_phrase = match.group(1).strip()
            else:
                qwe = "Не удалось извлечь код доступа из письма."
        else:
            qwe = "Не удалось декодировать содержимое письма."

    except Exception as e:
        qwe = f'Произошла ошибка при чтении почты. Обратитесь к администратору:n{e}'
    finally:
        if "mail_connection" in locals():
            mail_connection.logout()

    return qwe, extracted_phrase

async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    game_cat: str = None,
    state: str = None
):
    if level == 0:
        return await main(session=session, level=level, menu_name=menu_name)

    elif level == 2:
        return await categ(session)

    elif level == 3:
        return await game_catalog(session, game_cat, level)
    

