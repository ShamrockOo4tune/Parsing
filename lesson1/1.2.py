# Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
import requests
import json

# Сценарий запрашивает данные о ютуб канале по его ID c использованием API
API_KEY = '*********************************'  # <-- Здесь нужно указать свой API ключ googleapis.com
channel_id = 'UCPlNTldnwzmIW1ULCzWoJ-Q'
url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics' \
      f'&id={channel_id}' \
      f'&key={API_KEY}'

channel_data = requests.get(url).json()
print(f"У Youtube канала с ID {channel_id} следующие данные:\n\t"
      f"Название канала:\t\t\t{channel_data['items'][0]['snippet']['title']}\n\t"
      f"Количество просмотров:\t\t{channel_data['items'][0]['statistics']['viewCount']}\n\t"
      f"Количество видеозаписей: \t{channel_data['items'][0]['statistics']['videoCount']}")

with open(f'{channel_id}_data.json', 'w') as f:
    json.dump(channel_data, f)
print(f"Ответ сервера сохранен в файл:\t{channel_id}_data.json")
