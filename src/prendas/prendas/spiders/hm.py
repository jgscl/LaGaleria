import scrapy

from scrapy import Request
from scrapy.loader import ItemLoader
from prendas.items.prendaitem import PrendaItem
from itemloaders.processors import TakeFirst

from datetime import datetime
import re
import json

class HmSpider(scrapy.Spider):
    """Araña que recorre la web de H&M a través de la API JSON

    :return: item poblado con todos los campos
    :rtype: PrendaItem
    """    

    """Nombre de la araña para gestión de Scrapy"""
    name = "hm"

    #contador_errores_http = 0

    """Dominios que le está permitido recorrer"""
    allowed_domains = ["hm.com"]

    """URLS a las que se mandará petición primero"""
    start_urls = ["https://www2.hm.com/es_es/hombre/compra-por-producto/view-all.html",
                  "https://www2.hm.com/es_es/mujer/compra-por-producto/view-all.html"]

    """
    Ajustes de la araña:
    - Directorio donde se guardarán las imágenes descargadas de los productos de H&M
    """
    custom_settings = {
        "IMAGES_STORE": 'imagenes/hm',
    }

    """
    4)
    """
    
    def parse_item_description_composition(self, response, callback_item):
        """Obtención de los campos de descripción y composición. Se termina de poblar el item y
        se devuelve.

        :param response: respuesta que contiene el HTML de un producto
        :type response: Response
        :param callback_item: item que le faltan los campos de descripción y composición
        :type callback_item: PrendaItem
        :return: item poblado con todos los campos
        :rtype: PrendaItem
        """  

        il = ItemLoader(item=callback_item, response=response)
        il.default_output_processor = TakeFirst()

        il.add_xpath('descripcion', '//*[@id="section-descriptionAccordion"]/descendant::p/text()')

        ul = response.xpath('//*[@id="section-materialsAndSuppliersAccordion"]/ul[1]')

        """
        Se recorren los nietos del <ul></ul> seleccionado en el xpath de arriba. Estos nietos
        contienen la zona de composición (Tela exterior, Forro, Forro de la manda/bolsillos) y el
        material de dicha zona (Algodón, Poliéster, etc). Se busca coger como composición el elemento
        más grande de todo el producto, aunque no siempre es posible.
        Criterios de selección de composición:
        - El elemento detrás de 'Tela exterior', 'Parte delantera' o 'Parte superior'. Ej:
            h4 Forro
            p Poliéster 100%
            h4 Tela exterior
            p Poliamida 100
        - El elemento que hay si solo hay uno
        - El primer elemento si no contiene zona de composición. Ej:
            p Algodón 99%, Elastano 1%
            h4 Forro del bolsillo
            p Algodón 100%
        """
        
        composicion = None
        if len(ul.xpath('./*')) == 1:
            composicion = ul.xpath('./*/*/text()').get()
        else:
            i = 0
            encontrado = False
            for grandchild in ul.xpath('./*/child::*'):
                #debug
                #tag = grandchild.xpath('name()').get()
                contenido = grandchild.xpath('text()').get()
                if encontrado == True:
                    composicion = contenido
                    break
                if re.search('exterior|superior|delantera', contenido):
                    encontrado = True
                if re.search('%', contenido) and i == 0:
                    composicion = contenido
                    break

                i += 1
        
        il.add_value('composicion', composicion)

        return il.load_item()
    
    """
    3)
    """
    
    def parse_item_but_description(self, response, genero):
        """Se hace parsing de un producto obteniendo de los atributos de los items del archivo JSON
        todos los campos menos descripción y composición, que no se encuentran en ningún atributo. 
        Para obtener estos se hará una petición a la URL del producto.

        :param response: respuesta que contiene un archivo JSON con productos
        :type response: Response
        :param genero: género, hombre o mujer, al que pertenecen los ítems del archivo JSON
        :type genero: string
        :yield: petición de un producto
        :rtype: Request
        """        

        lista_items = json.loads(response.body)

        for elemento in lista_items.get('products'):
            busqueda_categoria = None
            busqueda_nombre = None

            if elemento.get('title') and elemento.get('category'):
                busqueda_categoria = re.search('accessorie|kid|care|lingerie|underwear|shoe|swim|sock|slipper|beauty', elemento['category'])
                busqueda_nombre = re.search('pack', elemento['title'], re.IGNORECASE)

            if busqueda_categoria is None and busqueda_nombre is None:
                il = ItemLoader(item=PrendaItem(), response=response)
                il.default_output_processor = TakeFirst()

                if elemento.get('link'):
                    url_item = f"https://www2.hm.com{elemento['link']}"

                il.add_value('nombre', elemento.get('title'))

                precio = re.search('[0-9,]+', elemento.get('price'))
                if precio:
                    il.add_value('precio', precio.group())

                if elemento.get('image') and len(elemento.get('image')) > 0 and elemento.get('image')[0].get('src'):
                    il.add_value('url_imagen', re.sub('style', 'main', f"https:{elemento['image'][0]['src']}"))
                
                il.add_value('genero', genero)

                if "0" != elemento.get('swatchesTotal') and elemento.get('swatches') and (
                    len(elemento.get('swatches')) > 0 and elemento.get('swatches')[0].get('colorName')):
                    il.add_value('color', elemento.get('swatches')[0].get('colorName'))               
                
                il.add_value('marca', 'H&M')
                        
                """Parametros para depuracion y auxiliares"""
                il.add_value('url', url_item)
                il.add_value('fecha', datetime.now())
                        
                item = il.load_item()
                    
                yield Request(url_item, cb_kwargs={"callback_item": item}, callback=self.parse_item_description_composition)
    
    """
    2)
    """  

    def crear_peticiones_json(self, genero, prefijo_genero, numero_articulos, tamano_bloque):
        """Se crean las URLs de la API JSON que devuelven todos los ítems de hombre y de mujer y se
        realizan dichas peticiones

        :param genero: cadena que contiene el género, puede ser hombre o mujer
        :type genero: string
        :param prefijo_genero: prefijo asociado al género, fa5b para hombre o 30ab para mujer
        :type prefijo_genero: string
        :param numero_articulos: número máximo de artículos de hombre o de mujer que hay en H&M
        :type numero_articulos: int
        :param tamano_bloque: número de productos que contendrá el archivo JSON
        :type tamano_bloque: int
        :return: lista de Request por partes a la API JSON hasta cubrir el número total de productos de cada género
        :rtype: list
        """        

        """
        Se divide el número máximo de elementos en bloques de tamano_bloques elementos y
        uno último del resto de elementos
        """
        numero_articulos = int(numero_articulos)
        num_bloques =  numero_articulos // tamano_bloque
        resto = numero_articulos % tamano_bloque

        """Se forman las urls de las peticiones a la API y se agrupan en una lista de Request"""
        offset = 0
        requests = []
        for i in range(num_bloques + 1):
            if i == num_bloques and resto != 0:
                url_json = f"https://www2.hm.com/es_es/{genero}/compra-por-producto/view-all/_jcr_content/main/productlisting_{prefijo_genero}.display.json?sort=stock&image-size=small&image=model&offset={offset}&page-size={resto}"
            else:
                url_json = f"https://www2.hm.com/es_es/{genero}/compra-por-producto/view-all/_jcr_content/main/productlisting_{prefijo_genero}.display.json?sort=stock&image-size=small&image=model&offset={offset}&page-size={tamano_bloque}"
            
            requests.append(Request(url=url_json, cb_kwargs={"genero": genero.title()}, callback=self.parse_item_but_description))
            offset += tamano_bloque
        return requests
    
    """
    1) - Se ejecuta lo primero
    """

    def parse(self, response):
        """Se gestiona la respuesta a las URLs de start_urls. Se obtienen el número de ítems de hombre
        o de mujer y se preparan parámetros para llamar a la API JSON

        :param response: respuesta tipo Response a un objeto Request de las URLs de start_urls
        :type response: Response
        :return: lista de Request de peticiones a la API JSON
        :rtype: list
        """        

        numero_articulos = re.search('[0-9]+', response.xpath('//*[@class="filter-pagination"]/text()').get()).group()
        tamano_bloque = 500
        if re.search('hombre', response.url):
            genero = 'hombre'
            prefijo_genero = 'fa5b'
            return self.crear_peticiones_json(genero, prefijo_genero, numero_articulos, tamano_bloque)
               
        elif re.search('mujer', response.url):
            genero = 'mujer'
            prefijo_genero = '30ab'
            return self.crear_peticiones_json(genero, prefijo_genero, numero_articulos, tamano_bloque)
        #debug mas menos
        else:
            print('Error, url rara no tiene ni hombre ni mujer')
