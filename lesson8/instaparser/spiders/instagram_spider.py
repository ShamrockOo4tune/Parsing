import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem


class InstagramSpiderSpider(scrapy.Spider):
    name = 'instagram_spider'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login = 'shamrockofortune'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1605125785:ASdQANaIHXCQMH5vuB3Sl7OqBubImeKLvz4LFsGWqDP7byE6Z+ny9N6AxxtefZxzs' \
                '/EszgVsg/rJ/tfJ2omCo8mfu5jXmwy4wd8DXVtaTEDc1LBKVooafaXpPiLqzNJLUMZbrhT4d+Tg1TB/Q08='
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = 'eddbde960fed6bde675388aac39a3657'
    followers_hash = 'c76146de99bb02f6415203be841dd25a'
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076'
    followers, following = {}, {}


    def __init__(self, parse_users: list):
        self.parse_users = parse_users  # Список пользователей, у которых собираем посты
        for user in parse_users:
            self.followers[user] = []
            self.following[user] = []

    def parse(self, response: HtmlResponse):
        csrf_token = self.get_csrf_token(response.text)
        yield scrapy.FormRequest(  # заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for parse_user in self.parse_users:

                yield response.follow(                  # Переходим на желаемую страницу пользователя
                    f'/{parse_user}/',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': deepcopy(parse_user)}
                )

    def user_data_parse(self, response: HtmlResponse, username: str):
        user_id = self.fetch_user_id(response.text, username)       # Получаем id пользователя
        variables_posts = {'id': user_id,                           # Формируем словарь для передачи даных в запрос
                           'first': 12}                             # 12 постов. Можно больше (макс. 50)
        variables_followers = {'id': user_id,
                               'first': 50}
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables_followers)}'  # ссылка о подписчиках

        yield response.follow(
            url_followers,
            callback=self.user_followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables_followers': deepcopy(variables_followers)}  # variables ч/з deepcopy во избежание гонок
        )


        """
        url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables_posts)}'  # ссылка данных о постах
        yield response.follow(
            url_posts,
            callback=self.user_posts_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables_posts': deepcopy(variables_posts)}         # variables ч/з deepcopy во избежание гонок
        )
        """

    # Принимаем ответ. Не забываем про параметры от cb_kwargs
    def user_followers_parse(self, response: HtmlResponse, username: str, user_id: str, variables_followers: dict):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables_followers['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables_followers)}'
            yield response.follow(
                url_followers,
                callback=self.user_followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables_followers': deepcopy(variables_followers)}
            )
        self.followers[username] += j_data.get('data').get('user').get('edge_followed_by').get('edges')
        if not page_info.get('has_next_page'):
            variables_following = {'id': user_id,
                                   'first': 24}
            url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables_following)}'
            yield response.follow(
                url_following,
                callback=self.user_following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables_following': deepcopy(variables_following)
                           }#'followers': self.followers}
            )

    def user_following_parse(self, response: HtmlResponse, username: str, user_id: str, variables_following: dict):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables_following['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables_following)}'
            yield response.follow(
                url_following,
                callback=self.user_following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables_following': deepcopy(variables_following)}
            )
        self.following[username] += j_data.get('data').get('user').get('edge_follow').get('edges')
        if not page_info.get('has_next_page'):
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                followers=self.followers[username],
                following=self.following[username]
            )
            print(1)
            yield item  # В пайплайн
        """
    def user_posts_parse(self, response: HtmlResponse, username: str, user_id: str, variables_posts: dict):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables_posts['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables_posts)}'
            yield response.follow(
                url_posts,
                callback=self.user_posts_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables_posts)}
            )

        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')  # Сами посты
        for post in posts:  # Перебираем посты, собираем данные
            item = InstaparserItem(
                user_id=user_id,
                photo=post['node']['display_url'],
                likes=post['node']['edge_media_preview_like']['count'],
                post=post['node']
            )
        yield item  # В пайплайн
    """

    def get_csrf_token(self, response_text: str) -> str:
        matched = re.search('\"csrf_token\":\"\\w+\"', response_text).group()
        # return matched.split(':')[-1].replace('\"', '')
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, response_text: str, username: str) -> str:
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, response_text
        ).group()
        return json.loads(matched).get('id')
