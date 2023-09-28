import scrapy

from scrapy.spiders import SitemapSpider
from scrapy.loader import ItemLoader
from prendas.items.prendaitem import PrendaItem
from itemloaders.processors import TakeFirst

import re
from datetime import datetime


class CarharttSpider(SitemapSpider):
    """Araña que recorre la web de Carhartt WIP a través del sitemap

    :yield: item poblado con todos los campos menos descripción
    :rtype: PrendaItem
    """    

    """Nombre de la araña para gestión de Scrapy"""
    name = "carhartt"

    """Dominios que le está permitido recorrer"""
    allowed_domains = ["carhartt-wip.com"]
    
    """URL del sitemap a recorrer"""
    sitemap_urls = ['https://www.carhartt-wip.com/es/sitemap-products.xml']

    """Palabras que en caso de contener cada URL del sitemap no se le enviará petición a dicha URL"""
    sitemap_rules = [
        ('^((?!accesorio|gadget|ropa-interior|zapato).)*$', 'parse')]
    
    """
    Ajustes de la araña:
    - Directorio donde se guardarán las imágenes descargadas de los productos de Carhartt
    """
    custom_settings = {
        "IMAGES_STORE": 'imagenes/carhartt',
    }
    
    def parse(self, response):
        """Se procesa cada página de producto. Se hace parsing para obtener todos los campos.

        :param response: respuesta que contiene el HTML de un producto
        :type response: Response
        :yield: item poblado con todos los campos
        :rtype: PrendaItem
        """

        """
        Contrato
        @url https://www.carhartt-wip.com/es/hombre-camisetas-manga-corta/s-s-braxton-shirt-yucca-white-1490_1
        @returns items 1
        @scrapes nombre precio url_imagen color descripcion
        @scrapes url proyecto spider server fecha composicion
        """

        il = ItemLoader(item=PrendaItem(), response=response)
        il.default_output_processor = TakeFirst()

        il.add_xpath('nombre', '//*[@class="product-title"]/descendant::*[@class="title"]/text()')
        il.add_xpath('precio', '//*[contains(@class, "price country_eur")]/text()')

        """
        Forma antigua/alternativa de obtener url_imagen
        carhartt_id = response.xpath('//li[contains(text(), "_")]/text()').get()
        if carhartt_id is not None:
            il.add_value('url_imagen', f"https://i1.adis.ws/i/carhartt_wip/{carhartt_id}-ST-01")
        """
        il.add_xpath('url_imagen', '//*[@data-mobile]/@data-mobile')

        if re.search('hombre', response.url) is not None:
            genero = 'hombre'
            il.add_value('genero', genero.title())
        elif re.search('mujer', response.url) is not None:
            genero = 'mujer'
            il.add_value('genero', genero.title())
        
        """
        El color se encuentra en una cadena de caracteres compleja, como la siguiente:
        'Carhartt WIP Awake NY Teddy Jacket | Chaquetas ligeras - Awake NY Dark Green / Awake NY Wax  / Verde | comprar online, entrega rápida ➤ envío gratuito'
        Se quiere extraer el 'Verde' por lo que primero, eliminaremos toda la cadena anterior
        a la última '/' y posteriormente buscaremos el color en la subcadena restante más sencilla
        """

        campo_color = response.xpath('//*[@property="og:description"]/@content').get()

        if campo_color is not None:
            indice_ultima_barra = campo_color.rfind("/")
            if indice_ultima_barra > 0:
                campo_color = campo_color[indice_ultima_barra:]
                color = re.search('(?<=/)\s([a-zA-ZÁÉÍÓÚáéíóú]+)', campo_color)
                if color is not None:
                    il.add_value('color', color.group(1))

        il.add_xpath('descripcion', '//*[@class="inner productDescription"]/p/text()')
        il.add_value('marca', 'Carhartt')
        il.add_xpath('composicion', '//li[contains(text(), "%")]/text()')

        """Parametros de limpieza"""
        il.add_value('url', response.url)
        il.add_value('fecha', datetime.now())

        yield il.load_item()

        
