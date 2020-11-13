# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from pymongo import MongoClient


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram

    def process_item(self, item, spider):
        followers = [follower.pop('node') for follower in item['followers']]
        item['followers'] = followers
        following = [following.pop('node') for following in item['following']]
        item['following'] = following
        print(1)
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
