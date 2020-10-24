""" Написать приложение, которое собирает основные новости с сайтов
news.mail.ru, lenta.ru, yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
        название источника;
        наименование новости;
        ссылку на новость;
        дата публикации.
    Сложить собранные данные в БД"""

from lxml import html
import requests
from datetime import datetime
from datetime import timedelta
from pymongo import MongoClient


def dd_rus_mm_yyyy_convert(string: str) -> str:
    months = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06',
              'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}
    rus_month = string.split(' ')[3]
    num_month = months[rus_month]
    yyyy_mm_dd = '-'.join((string.split(' ')[4], num_month, string.split(' ')[2]))
    return yyyy_mm_dd


def yandex_time_convert(string: str) -> str:
    # 'вчера в 05:34'
    string_list = string.split(' ')
    if string_list[0] == 'вчера':
        date_string = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        date_string = datetime.today().strftime('%Y-%m-%d')
    return date_string


main_link = ['https://news.mail.ru/', 'https://lenta.ru/', 'https://yandex.ru/news']  # три ресурса для сбора новостей
headers = {'User-Agent': 'Mozilla / 5.0 (X11; Ubuntu; Linux x86_64; rv: 75.0) Gecko / 20100101 Firefox / 75.0'}

news = []  # Причесанный список с новостями

# Собираем данные с news.mail.ru
response = requests.get(main_link[0], headers=headers)
dom = html.fromstring(response.text)
news_block = dom.xpath("//div[contains(@class, 'newsitem newsitem')]")
for news_data in news_block:
    news_name = news_data.xpath(".//a[@class='newsitem__title link-holder']/span/text()")
    news_link = news_data.xpath(".//a[@class='newsitem__title link-holder']/@href")
    news_source = news_data.xpath(".//span[@class='newsitem__param']/text()")
    news_date = news_data.xpath(".//div[@class='newsitem__params']/span[@datetime]/@datetime")

    news.append(dict(news_name=None if not news_name else news_name[0],
                     news_link=None if not news_link else news_link[0],
                     news_source=None if not news_source else news_source[0],
                     news_date=None if not news_date else news_date[0][:10]))

# Собираем данные с lenta.ru
response = requests.get(main_link[1], headers=headers)
dom = html.fromstring(response.text)
news_block = dom.xpath("//time[contains(@class, 'g-time')]/..")
for news_data in news_block:
    news_name = news_data.xpath("./text()")
    news_link = news_data.xpath("./@href")
    news_source = ['lenta.ru']
    news_date = news_data.xpath("./time/@datetime")

    # Преобразование ссылок из составных
    if not news_link:
        news_link = None
    elif news_link[0].startswith('/'):
        news_link = main_link[1] + news_link[0]
    else:
        news_link = news_link[0]

    # Раскрываем одноэлементные списки
    news.append(dict(news_name=None if not news_name else news_name[0].replace('\xa0', ''),
                     news_link=news_link,
                     news_source=None if not news_source else news_source[0],
                     news_date=None if not news_date else dd_rus_mm_yyyy_convert(news_date[0])))

# Собираем данные с yandex-новости
response = requests.get(main_link[2], headers=headers)
dom = html.fromstring(response.text)
news_block = dom.xpath("//div[contains(@class, 'news-top-stories')]//article")
for news_data in news_block:
    news_name = news_data.xpath(".//h2/text()")
    news_link = news_data.xpath(".//h2/../@href")
    news_source = news_data.xpath(".//span[@class='mg-card-source__source']/a/text()")
    news_date = news_data.xpath(".//span[@class='mg-card-source__time']/text()")
    news.append(dict(news_name=None if not news_name else news_name[0],
                     news_link=None if not news_link else news_link[0],
                     news_source=None if not news_source else news_source[0],
                     news_date=None if not news_date else yandex_time_convert(news_date[0])))

# Складываем списки словарей в MongoDB, дубликаты отсеиваем по значению ссылки на новость (news_link)
client = MongoClient('localhost', 27017)
db = client['news']
for piece_of_news in news:
    if not db.news.count_documents({"news_link": piece_of_news['news_link']}):
        db.news.insert_one(piece_of_news)
