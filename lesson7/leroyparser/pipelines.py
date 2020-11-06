# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import os
from urllib.parse import urlparse
from pymongo import MongoClient


class LeroyparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlen

    def process_item(self, item, spider):
        item['characteristics'] = dict(zip(item['keys'], item['values']))  # сшиваем названия параметров и значения
        # параметров в словарь
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class LeroyPhotoPipeline (ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['pictures']:
            for img in item['pictures']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e, 'что то пошло не так...')

    def item_completed(self, results, item, info):
        if results:
            item['pictures'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        dir_name = 'named_files/' + item['name'].replace(' ', '_')  # название каталога для хранения текущего файла
        file_name_dot_ext = os.path.basename(urlparse(request.url).path)  # восстанавливаем "заводское" имя файла
        result = dir_name + '/' + file_name_dot_ext
        return result
