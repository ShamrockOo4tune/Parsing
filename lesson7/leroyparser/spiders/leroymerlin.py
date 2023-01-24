import scrapy
from scrapy.http import HtmlResponse
from leroyparser.items import LeroyparserItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        goods = response.xpath("//product-card/@data-product-url").extract()
        for good in goods:
            yield response.follow(good, callback=self.parse_good)

    def parse_good(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyparserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_value('link', response.url)
        loader.add_xpath('keys', "//div[@class='def-list__group']//dt/text()")
        loader.add_xpath('values', "//div[@class='def-list__group']//dd//text()")
        loader.add_xpath('pictures', "//img[@alt='product image']/@src")
        yield loader.load_item()

        """
        name = response.xpath("//h1/text()").extract_first()
        price = response.xpath("//span[@slot='price']/text()").extract_first()
        link = response.url
        keys = response.xpath("//div[@class='def-list__group']//dt/text()").extract()
        values = response.xpath("//div[@class='def-list__group']//dd/text()").extract()
        pictures = response.xpath("//img[@alt='product image']/@src").extract()
        yield LeroyparserItem(name=name, price=price, link=link, keys=keys, values=values, pictures=pictures)
        """