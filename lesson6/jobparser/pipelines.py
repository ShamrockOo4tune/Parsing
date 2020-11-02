# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.scrapy_vac

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['salary_min'], item['salary_max'], item['currency'] = self.process_salary_hh(item['salary'])
        elif spider.name == 'sjru':
            item['salary_min'], item['salary_max'], item['currency'] = self.process_salary_sj(item['salary'])
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def process_salary_hh(self, salary):
        salary_min = None
        salary_max = None
        currency = None
        numbers = []
        from_flag = 0
        to_flag = 0
        for el in salary:
            el = el.replace('\xa0', '')
            if el == 'руб.':
                currency = 'RUR'
            elif el == 'USD':
                currency = 'USD'
            elif el == 'EUR':
                currency = 'EUR'
            elif el == 'от ':
                from_flag = 1
            elif el == 'до ':
                to_flag = 1
            elif el.isdigit():
                numbers.append(int(el))
        if len(numbers) == 2:
            salary_min = numbers[0]
            salary_max = numbers[1]
        elif len(numbers) == 1 and from_flag:
            salary_min = numbers[0]
        elif len(numbers) == 1 and to_flag:
            salary_max = numbers[0]
        return salary_min, salary_max, currency

    def process_salary_sj(self, salary):
        salary_min = None
        salary_max = None
        currency = None
        numbers = []
        from_flag = 0
        to_flag = 0
        for el in salary:
            el = el.replace('\xa0', '')
            if 'руб.' in el:
                currency = 'RUR'
            elif 'USD' in el:
                currency = 'USD'
            elif 'EUR' in el:
                currency = 'EUR'
            elif el == 'от':
                from_flag = 1
            elif el == 'до':
                to_flag = 1
            str_number = el.replace('руб.', '').replace(' ', '')
            if str_number.isdigit():
                numbers.append(int(str_number))
        if len(numbers) == 2:
            salary_min = numbers[0]
            salary_max = numbers[1]
        elif len(numbers) == 1 and from_flag:
            salary_min = numbers[0]
        elif len(numbers) == 1 and to_flag:
            salary_max = numbers[0]
        return salary_min, salary_max, currency
