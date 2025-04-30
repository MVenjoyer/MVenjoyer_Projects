import asyncio
import logging
import sys
from dotenv import load_dotenv
import os
from bot_db import init_db, get_hist, get_stats, add_stat, add_hist
import aiohttp
import typing as tp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bs4 import BeautifulSoup

load_dotenv()
TOKEN = os.getenv("TOKEN")
HEADERS_KINOPOISK = {
    "X-API-KEY": os.getenv("X_API_KEY"),
}
USER_HEADERS = {
    "User-Agent": os.getenv("USER_AGENT"),
}
dp = Dispatcher()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

init_db()


# COMMANDS
@dp.message(CommandStart())
async def command_start(message: Message) -> None:
    try:
        await message.answer(
            "Вот всё что я умею:\n"
            "/help - чтобы узнать что я умею\n"
            "/history - история последних 10-ти запросов\n"
            "/stats - сколько раз пользователь спрашивал про каждый фильм\n"
            "Для получения доступа к бесплатному просмотру фильма, введите его название."
        )
    except Exception as e:
        logging.error(f"Ошибка при выполнении команды /help: {e}")
        await message.answer("Произошла ошибка при выполнении команды. Попробуйте снова позже.")


@dp.message(Command("help"))
async def command_help(message: Message) -> None:
    try:
        await message.answer(
            "Вот всё что я умею:\n"
            "/help - чтобы узнать что я умею\n"
            "/history - история последних 10-ти запросов\n"
            "/stats - сколько раз пользователь спрашивал про каждый фильм\n"
            "Для получения доступа к бесплатному просмотру фильма, введите его название."
        )
    except Exception as e:
        logging.error(f"Ошибка при выполнении команды /help: {e}")
        await message.answer("Произошла ошибка при выполнении команды. Попробуйте снова позже.")


@dp.message(Command("history"))
async def command_history(message: Message) -> None:
    try:
        user_id = message.from_user.id
        hist_data = await get_hist(user_id)
        if hist_data:
            answer = "\n".join([f"Время: {tm}, запрос: {msg}" for tm, msg in hist_data])
            await message.answer(answer)
        else:
            await message.answer("Не смог найти информацию ваших запросов. Попробуй /start.")
    except Exception as e:
        logging.error(f"Ошибка при получении истории запросов: {e}")
        await message.answer("Произошла ошибка при получении вашей истории запросов. Попробуйте снова позже.")


@dp.message(Command("stats"))
async def command_stats(message: Message) -> None:
    try:
        user_id = message.from_user.id
        stat_data = await get_stats(user_id)
        if stat_data:
            answer = "\n".join([f"Имя фильма: {fn}, количество запросов: {rc}" for fn, rc in stat_data])
            await message.answer(answer)
        else:
            await message.answer("Извините, не смог найти информацию о количестве ваших запросов, попробуйте /start.")
    except Exception as e:
        logging.error(f"Ошибка при получении статистики запросов: {e}")
        await message.answer("Произошла ошибка при получении вашей статистики. Попробуйте снова позже.")


@dp.message()
async def command_film(message: Message) -> None:
    try:
        film_data = (await __get_film_by_name(message.text))[0]
        if film_data:
            caption = await __parse_film(film_data)
            links = {
                "Lordfilm": await __find_link(film_data, "lordfilm"),
                "Rutube": await __find_link(film_data, "rutube")
            }
            keyboard = await __create_inline_keyboard(links)
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=film_data["poster"]["url"],
                caption=caption,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            await add_stat(message.from_user.id, film_data["name"])
            await add_hist(message.from_user.id, message.text)
        else:
            await message.answer(f"Фильм с названием '{message.text}' не найден.")
    except Exception as e:
        logging.error(f"Ошибка при обработке запроса фильма: {e}")
        await message.answer(
            f"Произошла ошибка при поиске фильма '{message.text}'. "
            f"Проверьте название или попробуйте ввести снова позже.")


# PARSING

async def __create_inline_keyboard(links: dict) -> InlineKeyboardMarkup:
    try:
        buttons = [InlineKeyboardButton(text=name, url=url) for name, url in links.items()
                   if url != "Не удалось найти рабочую ссылку, содержащую ресурс."]
        if not buttons:
            raise ValueError("Нет доступных ссылок для создания клавиатуры.")
        return InlineKeyboardMarkup(inline_keyboard=[buttons])
    except ValueError as ve:
        logging.warning(f"Ошибка при создании клавиатуры: {ve}")
        raise
    except Exception as e:
        logging.error(f"Ошибка при создании клавиатуры: {e}")
        raise


async def __find_link(film: dict[tp.Any], resource: str) -> str:
    try:
        url = "https://www.google.com/search"
        params = {"q": f"{film['name']} {film['year']} {resource}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=USER_HEADERS) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, "html.parser")
                    for lnk in soup.select(".tF2Cxc .yuRUbf a", limit=5):
                        link = lnk["href"]
                        if resource.lower() in link.lower():
                            try:
                                async with session.get(link, timeout=0.8) as test_response:
                                    if test_response.status == 200:
                                        return link
                            except Exception as e:
                                logging.error(f"Ошибка при тестировании ссылки {link}: {e}")
                                continue
                    return "Не удалось найти рабочую ссылку, содержащую ресурс."
                else:
                    logging.error(f"Ошибка при запросе к Google (статус: {response.status})")
                    return f"Ошибка: {response.status}"
    except Exception as e:
        logging.error(f"Ошибка при поиске ссылки: {e}")
        return "Произошла ошибка при поиске ссылки. Попробуйте позже."


async def __parse_film(film_data: dict[tp.Any]) -> str:
    try:
        descr = ""
        if len(film_data['description']) < 512 and len(film_data['description']) != 0:
            descr = f"<b>Описание:</b> {film_data['description']}"
        elif len(film_data['shortDescription']) < 512 and len(film_data['shortDescription']) != 0:
            descr = f"<b>Описание:</b> {film_data['shortDescription']}"
        genres = ", ".join([genre["name"] for genre in film_data["genres"]])
        return (f"<b>Название:</b> {film_data['name']}\n"
                f"<b>Год выпуска:</b> {film_data['year']}\n"
                f"<b>Жанры:</b> {genres}\n\n"
                f"{descr}")
    except KeyError as e:
        logging.error(f"Ошибка при парсинге данных фильма: отсутствует ключ {e}")
        return "Ошибка при парсинге данных фильма."
    except Exception as e:
        logging.error(f"Ошибка при парсинге данных фильма: {e}")
        return "Произошла ошибка при обработке информации о фильме."


async def __get_film_by_name(name: str) -> tp.List[tp.Dict]:
    try:
        url = "https://api.kinopoisk.dev/v1.4/movie/search"
        async with aiohttp.ClientSession() as cli:
            async with cli.get(url, headers=HEADERS_KINOPOISK, params={"query": name}) as resp:
                if resp.status == 200:
                    tmp = await resp.json()
                    return tmp.get("docs", [])
                else:
                    logging.error(f"Ошибка при запросе к API Kinopoisk (статус: {resp.status})")
                    return []
    except aiohttp.ClientError as e:
        logging.error(f"Сетевые ошибки при запросе к Kinopoisk: {e}")
        return []
    except Exception as e:
        logging.error(f"Ошибка при получении фильма по названию: {e}")
        return []


async def main() -> None:
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
