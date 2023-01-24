# Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для
# конкретного пользователя, сохранить JSON-вывод в файле *.json.
import requests
import json
username = 'ShamrockOo4tune'  # Имя пользователя (учетка) на GitHub
url = f'https://api.github.com/users/{username}/repos'
repos = requests.get(url).json()
i = 1  # счетчик
print(f"У пользователя {username} имеется {len(repos)} репозиториев на GitHub:")
for repo in repos:
    print(f"{i}.\t{repo['full_name']}\n\tСсылка: {repo['html_url']}\n")
    i += 1
#  Сохраняем ответ в файл .json
with open(f'{username}_repos.json', 'w') as f:
    json.dump(repos, f)
print(f"Ответ сервера сохранен в файл {username}_repos.json")
