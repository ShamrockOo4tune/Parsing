import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://yuzhno-sakhalinsk.superjob.ru/vacancy/search/?keywords=водитель']

    def parse(self, response: HtmlResponse):
        links = response.xpath("//div[contains(@class, 'f-test-vacancy-item')]//a[@target='_blank']/@href").extract()
        next_page = response.xpath("//a[contains(@class, 'f-test-button-dalshe')]/@href").extract_first()
        # print(1)
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)
            # print(1)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        salary = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']/text()").extract()
        link = response.url
        from_site = 'superjob.ru'
        # print(1)
        yield JobparserItem(name=name, salary=salary, link=link, from_site=from_site)
