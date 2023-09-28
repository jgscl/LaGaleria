import scrapy

from scrapy.spiders import SitemapSpider
from scrapy.loader import ItemLoader
from prendas.items.prendaitem import PrendaItem
from itemloaders.processors import Join, TakeFirst
from scrapy import Request

import re
from datetime import datetime
import json

class ZaraSpider(SitemapSpider):
    """Araña que recorre la web de Zara a través del sitemap

    :return: item poblado con todos los campos menos descripción
    :rtype: PrendaItem
    """    

    """Nombre de la araña para gestión de Scrapy"""
    name = "zara"

    """Dominio permitido para que recorra la araña"""
    allowed_domains = ["zara.com"]

    """URL del sitemap que recorre la araña"""
    sitemap_urls = ['https://www.zara.com/sitemaps/sitemap-es-es.xml.gz']

    """Palabras que en caso de contener cada URL del sitemap no se le enviará petición a dicha URL"""
    sitemap_rules = [
        ('^((?!/help|-mkt[0-9]+|-pG[0-9]+|-pT[0-9]+|-p[1-9]|look-|kids|nino|girl|boy|baby|pendiente|abalorio|accessori|accesori|pack|boxer|mochila|calcetin|sombra|bolso|gafa|lip-|zapat|shoe|mini--|sujetador|refill|wallpaper|perfume|beachwear|beauty|lingerie|bag).)*$', 'parse')]

    """
    Ajustes de la araña:
    - Directorio donde se guardarán las imágenes descargadas de los productos de Zara
    """
    custom_settings = {
        "IMAGES_STORE": 'imagenes/zara',
    }

    """
    Constructor de ZaraSpider
    """

    def __init__(self, productos_bd=None, *args, **kwargs):
        """Constructor de ZaraSpider

        :param productos_bd: lista de URLs de los productos de Zara almacenados en la base
        de datos
        :type productos_bd: list
        """        
        super().__init__(*args, **kwargs)
        
        self.productos_bd = productos_bd
        if self.productos_bd:
            self.productos_bd = [tupla[0] for tupla in json.loads(productos_bd)]
        else:
            self.productos_bd = []

    """
    2.1) - Se procesa cada página de producto.
    """

    def parse_producto(self, response):
        """Se procesa cada página de producto. Se hace parsing para obtener todos los campos menos descripción.

        :param response: respuesta que contiene el HTML de un producto
        :type response: Response
        :return: item pobladdo con todos los campos menos descripción
        :rtype: PrendaItem
        """        

        il = ItemLoader(item=PrendaItem(), response=response)

        """
        Como los ItemLoaders guardan por defecto los elementos como listas y en este proyecto
        a prior solo se guardará un único valor por cada campo (Field()), pondremos como 
        metodo output_processor por defecto TakeFirst() que guarda los elementos como una variable
        única en vez de como lista
        """
        il.default_output_processor = TakeFirst()
        
        il.add_xpath('nombre', '//*[@class="product-detail-info__header-name"]/text()')
        il.add_xpath('precio', '//*[@class="money-amount__main"]/text()', re='[0-9,]+')
        il.add_xpath('url_imagen', '//meta[@property="og:image"]/@content')
        il.add_xpath('genero', '(//*[@itemprop="name"])[2]/text()')
        il.add_xpath('color', '//*[contains(@class, "product-color-extended-name")]/text()')
        il.add_xpath('descripcion', '//*[@class="expandable-text__inner-content"]/p/text()', Join())
        il.add_value('marca', 'Zara')

        il.add_value('url', response.url)
        il.add_value('fecha', datetime.now())

        return il.load_item()
    
    """
    2.1) - Se procesan las páginas de listas -l
    """

    def parse_lista(self, response):
        """Se obtienen todos los enlaces tipo -p, es decir, todos los productos del enlace tipo -l,
        y se envían peticiones a dichos enlaces -p cuya respuesta será procesada en parse_producto(). Estas listas
        -l se analizan de forma diaria.

        :param response: respuesta que contiene un HTML de lista de productos
        :type response: Response
        :yield: petición a enlaces tipo -p de productos
        :rtype: Request
        """        

        """Posibles XPath de los links"""
        links_1 = response.xpath('//*[@class="product-link _item product-grid-product-info__name link"]/@href').getall()
        links_2 = response.xpath('//*[@class="media-region link"]/@href').getall()
        links_3 = response.xpath('//*[@class="product-link product-grid-product__link link"]/@href').getall()

        links = links_1 + links_2 + links_3

        """
        Se convierte la lista en set y de vuelta a lista para eliminar los links duplicados.
        Los sets no tienen elementos duplicados, y en este caso se eliminan.
        """
        links_unicos = list(set(links))

        for link_p in links_unicos:
            if re.search('-p0[0-9]+', link_p) and link_p not in self.productos_bd:
                yield Request(link_p, callback = self.parse_producto)

    """
    2) - Procesa la respuesta y redirige a un método de gestión en cada caso
    """

    def parse(self, response):
        """Procesa la respuesta de cada petición realizada a las URLs provinientes de sitemap_filter().
        Los enlaces tipo -p se procesan como productos y los tipo -l como listas de productos

        :param response: respuesta que contiene el HTML de un producto o de una lista de productos
        :type response: Response
        :return: item en caso de ser una URL tipo -p o petición de un producto si es una URL tipo -l
        :rtype: PrendaItem o Request
        """

        """Contrato: unit test de una prenda
        Los contratos sirven para hacer unit testing sobre la url dada para ver que los XPath
        funcionan bien

        @url https://www.zara.com/es/es/camiseta-rotos-p04729353.html
        @returns items 1
        @scrapes nombre precio url_imagen color descripcion
        @scrapes url proyecto spider server fecha
        """
        
        if re.search('-p0[0-9]+', response.url):
            return self.parse_producto(response)
        
        if re.search('-l[0-9]+', response.url):
            return self.parse_lista(response)

    """
    1) - Recorre el sitemap y devuelve enlaces tipo -l o -p. Se ejecuta tras sitemap_rules
    """
    
    def sitemap_filter(self, entries):
        """Método cuya función es la de recorrer el sitemap y hacer un filtrado de las distintas URLs.
        El filtrado de entradas se hace en base a la etiqueta XML 'changefreq', de forma que diariamente
        se recorran las URLs con valor 'daily', en este caso las tipo -l y semanalmente los lunes las tipo -p.
        Se aplica primeramente los filtros de sitemap_rules y posteriormente se ejecuta este método.

        :param entries: elementos <url></url> del sitemap
        :yield: elemento <url></url> del sitemap cuya URL es tipo -l o tipo -p
        """        
        for entry in entries:
            if entry.get('changefreq'):
                if entry['changefreq'].lower() == 'weekly' and (
                    datetime.today().date().strftime("%A").lower() == 'monday'):
                    yield entry
                elif entry['changefreq'].lower() == 'daily':
                    yield entry
