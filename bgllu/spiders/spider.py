import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import BglluItem
from itemloaders.processors import TakeFirst


class BglluSpider(scrapy.Spider):
	name = 'bgllu'
	start_urls = ['https://www.bgl.lu/fr/qui-sommes-nous/actualites.html']

	def parse(self, response):
		post_links = response.xpath('//div[@class="wrapper-article"]')
		for post in post_links:
			date = post.xpath('./div[@class="article-text"]//text()').getall()
			date = [p.strip() for p in date]
			date = ' '.join(date).strip()
			try:
				date = re.findall(r'\d+[a-zA-ZÀ-ÿ. ]*\s[a-zA-ZÀ-ÿ-. ]+\s\d{4}', date)[0]
			except:
				date = ''
			link = post.xpath('./@onclick').get()
			if link:
				link = re.sub(r'location.href=', '', link)
				link = re.sub(r'window.open\(', '', link)
				link = re.sub(r'location.href=', '', link)
				link = re.sub(r"'", '', link)
				link = re.sub(r"\)", '', link)
				if link[-3:] != 'pdf':
					yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//section[@class="bloc-assistance anchor"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BglluItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
