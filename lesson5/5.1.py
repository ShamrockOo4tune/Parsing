""" Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о
письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172 """
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient


def date_from_rus_string(string_date: str) -> str:

    from datetime import datetime
    months = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06',
              'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}
    date_list = string_date.split(',')[0].split(' ')
    if len(date_list) == 2:
        year = str(datetime.now().year)
        month = months[date_list[1]]
        day = date_list[0]
        date = '-'.join((year, month, day))
    elif len(date_list) == 3:
        date_list[1] = months[date_list[1]]
        date = '-'.join((date_list[2], date_list[1], date_list[0]))
    elif date_list[0] == 'Сегодня':
        date = datetime.now().strftime('%Y-%m-%d')
    else:
        date = string_date
    return date


chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)

driver.get('https://mail.ru/')

login = driver.find_element_by_id('mailbox:login-input')
login.send_keys('study.ai_172')
login.send_keys(Keys.ENTER)
# ждем появления поля для ввода пароля
passw = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, 'mailbox:password-input')))
passw.send_keys('NextPassword172')
passw.send_keys(Keys.ENTER)

links = []

while True:
    # контейнеры с сылками. Ожидаем загрузки перед началом обработки.
    link_containers = WebDriverWait(driver, 30).until(ec.visibility_of_all_elements_located((By.CLASS_NAME, 'llc')))

    # Если такая ссылка уже попала в список, значит мы еже догребли до дна ящика входящих писем --> на выход
    if link_containers[-1].get_attribute('href') in links:
        links = set(links)  # убираем дубликаты
        break

    # Разделываем контейнер с сылкой и складываем очищенные ссылки в links[]:
    for link in link_containers:
        current_link = link.get_attribute('href')
        links.append(current_link)

    # Перемотка к последнему обработаному контейнеру
    actions = ActionChains(driver)
    actions.move_to_element(link_containers[-1])
    actions.perform()

# заходим в каждое письмо и собираем данные и формируем в список словарей messages:

messages = []
count = 0
client = MongoClient('localhost', 27017)
db = client['mails']
for link in links:
    driver.get(link)
    author = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, 'letter-contact'))).\
        get_attribute('title')
    date = date_from_rus_string(driver.find_element_by_class_name('letter__date').text)
    topic = driver.find_element_by_class_name('thread__subject').text
    message_body = driver.find_element_by_class_name('letter-body').text
    messages.append(dict(author=author, date=date, topic=topic, message_body=message_body, link=link))

    if not db.mails.count_documents({"link": link}):
        db.mails.insert_one(messages[-1])

    count += 1
    print(f'{round(count * 100 / len(links))} parsed')

print(1)