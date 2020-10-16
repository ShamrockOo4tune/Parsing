""" Вариант 1
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайтов
Superjob и HH. Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:
    Наименование вакансии.
    Предлагаемую зарплату (отдельно минимальную и максимальную).
    Ссылку на саму вакансию.
    Сайт, откуда собрана вакансия.
### По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas."""
import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs

#def stage_job_data():



# https://yuzhno-sakhalinsk.hh.ru/search/vacancy?clusters=true&area=1960&enable_snippets=true&salary=&st=searchVacancy&text=Python
# https://yuzhno-sakhalinsk.superjob.ru/vacancy/search/?keywords=python
job_name = input('Введите название вакансии для поиска в г.Южно-Сахалинск: ')  # НН принимается в параметре 'text' запроса
headers = {'User-Agent': 'Mozilla / 5.0 (X11; Ubuntu; Linux x86_64; rv: 75.0) Gecko / 20100101 Firefox / 75.0'}
jobs = []  # сюда будем складывать резульататы

resource_name = 'hh.ru'
main_link = r'https://yuzhno-sakhalinsk.hh.ru'
params = dict(clusters='true',
              area=1960,
              enable_snippets='true',
              salary="",
              st='searchVacancy',
              text=job_name)
response = requests.get(main_link+r'/search/vacancy', params=params, headers=headers)
soup = bs(response.text, 'html.parser')
jobs_list = soup.findAll('div', {'class': 'vacancy-serp-item'})  # итерируемый
# объект bs4 с результатами поиска по запросу на job_name вакансию
for job_data in jobs_list:
    job_name = job_data.find('div', {'class': 'vacancy-serp-item__row_header'}).find('a').text
    salary_data = job_data.find('div', {'class': 'vacancy-serp-item__row_header'}).findAll('span')[-1].text  # з/п data
    salo = salary_data.replace('\xa0', '').replace('-', ' ').split(' ')  # очистка, нарезка на элементы
    salary_from, salary_to, currency = None, None, None  # сбрасываем предыдущие значения в None
    '''ниже происходит "понимание" и "разделение" зарплаты при различном ее представлении с использованием одного или 
    нуля или двух пределов, с использованием или без "от" и "до"'''
    from_flag, to_flag = 0, 0
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
    salo = salary_data.replace('\xa0', '').replace('-', ' ').replace('руб.', '').replace('USD', '').replace('EUR', '')
    salo = salo.replace('от', '').replace('до', '').strip().split(' ')
    if len(salo) == 2:
        salary_from = salo[0]
        salary_to = salo[1]
    elif len(salo) == 1 and from_flag:
        salary_from = salo[0]
    elif len(salo) == 1 and to_flag:
        salary_to = salo[0]
    link = job_data.find('a', {'class': ['bloko-link', 'HH-LinkModifier']}).attrs['href']
    jobs.append(dict(resource_name=resource_name,
                     job_name=job_name,
                     salary_from=salary_from,
                     salary_to=salary_to,
                     currency=currency,
                     link=link))
pprint(jobs)
print(1)

