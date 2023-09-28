import scrapy
import gzip
from scrapy.utils.gz import gunzip
from scrapy.http import XmlResponse, TextResponse
from scrapy import signals
from scrapy import Request

import re


class DailySpider(scrapy.Spider):
    name = "daily"
    #f = open('/home/j/Desktop/volcado.txt', "a")

    allowed_domains = ["www.zara.com"]
    start_urls = ["https://www.zara.com/sitemaps/sitemap-es-es.xml.gz"]
    #file:///home/j/Downloads/sitemap-es-es-11-5.xml
    #https://www.zara.com/sitemaps/sitemap-es-es.xml.gz
    """
    def spider_opened(self, spider):
        self.f = open('/home/j/Desktop/volcado.txt', "a")
    """   
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DailySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        
        if self.f:
            self.f.close()

    def parse(self, response):
        db = gzip.decompress(response.body)
        decoded_body = db.decode('utf-8')
        lineas = set(decoded_body.split('\n'))

        lista_l = []
        lista_p = []
        lista_pT = []

        for linea in lineas:
            url = re.search('https:.+[.]html', linea)
            if url is not None:
                url = url.group()
                contiene_l = re.search('-l[0-9]+', url)
                contiene_p = re.search('-p[0-9]+', url)
                contiene_pT = re.search('-pT[0-9]+', url) 
  
                """Contar el número de urls tipo daily"""
                if contiene_l is not None:
                    lista_l.append(url)
                
                """Weekly"""
                if contiene_pT is not None:
                    lista_pT.append(url)
                        
                if contiene_p is not None:
                    lista_p.append(url)
                        
        
        for l in lista_l:
            yield Request(l, meta={"ruta_sitemap": response.url, "productos": lista_p}, callback=self.parse_l)

        
        for pT in lista_pT:
            yield Request(pT, meta={"ruta_sitemap": response.url, "productos": lista_p}, callback = self.parse_pT)
           
    def chequear_en_sitemap(self, total_productos, links, link_padre):
        contador = 0
        repes = []
        print(f"chequeo site: {len(total_productos)} {len(links)}")
        self.f.write(f"Link padre: {link_padre}\n")
        #print(len(response.meta['productos']))
        for l in links:
            if l not in total_productos:
                self.f.write(f"- Tipo -p {contador}/{len(links)}- {l}\n")
                repes.append(l)
                contador += 1
                
        
    def parse_l(self, response):
        links_1 = response.xpath('//*[@class="product-link _item product-grid-product-info__name link"]/@href').getall()
        links_2 = response.xpath('//*[@class="media-region link"]/@href').getall()
        links = links_1 + links_2

        links_pT = []

        i= 0
        for l in links:
            if re.search('-pT[0-9]+', l) is not None:
                links_pT = links.pop(i)
            i += 1

        if len(links_pT) > 0:
            for l in links_pT:
                yield Request(l, meta={"productos":response.meta['productos']}, callback = self.parse_pT)
        
        self.chequear_en_sitemap(response.meta['productos'], links, response.url)
           
    def parse_pT(self, response):
        if re.search('-pT[0-9]+', response.url) is not None:
            links = response.xpath('//*[@class="product-link product-secondary-product__link link"]/@href').getall()

            self.chequear_en_sitemap(response.meta['productos'], links, response.url)
    




