"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные
    вакансии в созданную БД.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
"""
import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient

search_job_name = input('Введите название вакансии для поиска в г.Южно-Сахалинск: ')
headers = {'User-Agent': 'Mozilla / 5.0 (X11; Ubuntu; Linux x86_64; rv: 75.0) Gecko / 20100101 Firefox / 75.0'}
jobs = []  # сюда будем складывать резульататы
resource_name = 'hh.ru'
main_link = 'https://yuzhno-sakhalinsk.hh.ru'
params = dict(clusters='true',
              area=81,
              enable_snippets='true',
              salary="",
              st='searchVacancy',
              text=search_job_name,
              L_is_autosearch='false')
n = 1  # флаг наличия следующей страницы для парсинга
page = 0

while n:
    response = requests.get(main_link+r'/search/vacancy', params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    jobs_list = soup.findAll('div', {'class': 'vacancy-serp-item'})  # итерируемый
    # объект bs4 с результатами поиска по запросу на job_name вакансию
    for job_data in jobs_list:
        job_name = job_data.find('div', {'class': 'vacancy-serp-item__row_header'}).find('a').text
        salary_data = job_data.find('div', {'class': 'vacancy-serp-item__row_header'}).findAll('span')[-1].text
        salo = salary_data.replace('\xa0', '').replace('-', ' ').split(' ')  # очистка, нарезка на элементы
        salary_from, salary_to, currency = None, None, None  # сбрасываем предыдущие значения в None
        '''ниже происходит "понимание" и "разделение" зарплаты при различном ее представлении с использованием 
        одного или нуля или двух пределов, с использованием или без "от" и "до"'''
        from_flag, to_flag = 0, 0
        numbers = []
        for el in salo:
            if el == 'руб.':
                currency = 'RUR'
            elif el == 'USD':
                currency = 'USD'
            elif el == 'EUR':
                currency = 'EUR'
            elif el == 'от':
                from_flag = 1
            elif el == 'до':
                to_flag = 1
            elif el.isdigit():
                numbers.append(int(el))
        salo = salary_data.replace('\xa0', '').replace('-', ' ').replace('руб.', '')
        salo = salo.replace('USD', '').replace('EUR', '')
        salo = salo.replace('от', '').replace('до', '').strip().split(' ')
        if len(numbers) == 2:
            salary_from = numbers[0]
            salary_to = numbers[1]
        elif len(numbers) == 1 and from_flag:
            salary_from = numbers[0]
        elif len(numbers) == 1 and to_flag:
            salary_to = numbers[0]
        link = job_data.find('a', {'class': ['bloko-link', 'HH-LinkModifier']}).attrs['href']
        jobs.append(dict(resource_name=resource_name,
                         job_name=job_name,
                         salary_from=salary_from,
                         salary_to=salary_to,
                         currency=currency,
                         link=link))
    n = soup.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
    page = n.attrs['data-page'] if n else None
    params['page'] = page

#  теперь с superjob.ru
resource_name = 'superjob.ru'
main_link = 'https://yuzhno-sakhalinsk.superjob.ru'
params = dict(keywords=search_job_name)
n = 1  # флаг наличия следующей страницы для парсинга
while n:
    response = requests.get(main_link + '/vacancy/search/', params=params, headers=headers)
    jobs_list = bs(response.text, 'html.parser').findAll('div', {'class': 'f-test-vacancy-item'})
    for job_data in jobs_list:
        job_name = job_data.findAll('a')[0].text
        link = main_link + job_data.findAll('a')[0].attrs['href']
        salary_data = job_data.findAll('span', {'class': 'f-test-text-company-item-salary'})[0].text
        salo = salary_data.replace('\xa0', ' \xa0 ').replace('\xa0', '')\
            .replace('000', '').replace('/', ' /').split(' ')
        # очистка,нарезка на элементы
        salary_from, salary_to, currency = None, None, None  # сбрасываем предыдущие значения в None
        '''ниже происходит "понимание" и "разделение" зарплаты при различном ее представлении с использованием 
        одного или нуля или двух пределов, с использованием или без "от" и "до"'''
        from_flag, to_flag = 0, 0
        numbers = []
        for el in salo:
            if el == 'руб.':
                currency = 'RUR'
            elif el == 'USD':
                currency = 'USD'
            elif el == 'EUR':
                currency = 'EUR'
            elif el == 'от':
                from_flag = 1
            elif el == 'до':
                to_flag = 1
            elif el.isdigit():
                numbers.append(int(el)*1000)
        salo = salary_data.replace('\xa0', '').replace('-', ' ').replace('руб.', '')
        salo = salo.replace('USD', '').replace('EUR', '')
        salo = salo.replace('от', '').replace('до', '').strip().split(' ')
        if len(numbers) == 2:
            salary_from = numbers[0]
            salary_to = numbers[1]
        elif len(numbers) == 1 and from_flag:
            salary_from = numbers[0]
        elif len(numbers) == 1 and to_flag:
            salary_to = numbers[0]
        jobs.append(dict(resource_name=resource_name,
                         job_name=job_name,
                         salary_from=salary_from,
                         salary_to=salary_to,
                         currency=currency,
                         link=link))
    n = bs(response.text, 'html.parser').find('a', {'class': 'f-test-button-dalshe'})
    if n:
        next_page = bs(response.text, 'html.parser').findAll('a', {'class': 'f-test-button-dalshe'})[0].attrs['href']
        params['page'] = next_page[next_page.find('&page=')+6:]

print(f'{len(jobs)} vacancies has been scrapped\n')

# Задание №1
"""
client = MongoClient('localhost', 27017)
db = client['vacancies']
count = 0
for job in jobs:
    db.vacancies.insert_one(job)
    count += 1
print(f'OK: successfully dumped {count} new documents to mongodb "vacancies" .vacancies collection')
"""


def search_by_salary(salary: int):  # Задание №2
    """
    :param salary:
    :return:
    Search vacancies db .vacancies collection for documents where salary_to or salary from are > 'salary':
    """
    result = [db.vacancies.find({'salary_from': {'$gt': salary}}), db.vacancies.find({'salary_to': {'$gt': salary}})]
    print(f'following vacancies have salary > {salary}:')
    for i in result:
        for vacancy in i:
            print(vacancy)


def insert_if_not_exists(vacancy: dict):  # Задание №3
    vac = [vac for vac in db.vacancies.find(vacancy, {'resource_name': 1, 'job_name': 1, 'salary_from': 1,
                                                      'salary_to': 1, 'currency': 1, 'link': 1, '_id': 0})]
    if len(vac) == 0:
        db.vacancies.insert_one(vacancy)
#       print('new vacancy has been dumped to mongodb "vacancies" .vacancies collection')
#   elif len(vac) > 0:
#       print('such vacancy already exists in db')


client = MongoClient('localhost', 27017)
db = client['vacancies']
count = 0
for job in jobs:
    insert_if_not_exists(job)

# search_by_salary(80000)
# search_by_salary(120000)
