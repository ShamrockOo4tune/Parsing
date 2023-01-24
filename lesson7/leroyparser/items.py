# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def price_clean(price):
    price = int(price.replace(' ', ''))
    return price


def values_clean(value):
    value = value.strip()
    return value


class LeroyparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(price_clean), output_processor=TakeFirst())
    _id = scrapy.Field()
    link = scrapy.Field()
    keys = scrapy.Field()
    values = scrapy.Field(input_processor=MapCompose(values_clean))
    pictures = scrapy.Field()
    characteristics = scrapy.Field()
