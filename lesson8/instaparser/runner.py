""" 1)Написать приложение, которое будет проходиться по указанному списку двух и/или более пользователей и
собирать данные об их подписчиках и подписках.
2) По каждому пользователю, который является подписчиком или на которого подписан исследуемый объект нужно
извлечь имя, id, фото (остальные данные по желанию). Фото можно дополнительно скачать.
3) Собранные данные необходимо сложить в базу данных. Структуру данных нужно заранее продумать, чтобы:
4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь"""

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from instaparser import settings
from instaparser.spiders.instagram_spider import InstagramSpiderSpider


# Задаем список пользователей инстаграм у которых будем собирать данные
def set_parse_users() -> list:
    users = []
    while 1:
        users.append(input(f'Введите не менее 2х аккаунтов пользователей Instagram для сбора данных.\n'
                           f'В списке уже указано {len(users)} пользователей.n'
                           f'Для заверщения ввода - ввести пустую строку (сразу жать enter): '))
        if not users[-1] and len(users) > 2:  # Если последний 0 и введено не менее 2х имен, то возвращаем список
            users.pop(-1)
            return users


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    parse_users = ['feruza_gumerova', 'rozakushnir40']  # set_parse_users()

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpiderSpider, parse_users=parse_users)

    process.start()
