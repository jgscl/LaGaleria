from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request
from prendas import settings

import re

class PipelineImagenes(ImagesPipeline):
    """Función de procesamiento del item. Se encarga de descargar las imágenes
    cuyas URL contiene cada ítem
    """    

    def get_media_requests(self, item, info):
        """Obtiene las URLs de las imágenes de un ítem

        :param item: item a procesar
        :type item: PrendaItem
        :param info: información de la descarga
        :return: petición de descarga de la imagen de url_imagen
        :rtype: Request
        """        
        return Request(item['url_imagen'])

    def generador_ruta_imagen(self, miniaturas, item):
        """Genera el nombre de la ruta desde el directorio IMAGES_STORE

        :param miniaturas: cadena que contiene o 'miniaturas' o None
        :type miniaturas: string
        :param item: item a procesar
        :type item: PrendaItem
        :return: ruta de la miniatura o imagen desde el directorio IMAGES_STORE
        :rtype: string
        """        
        if miniaturas:
            return f"miniaturas/{item['id']}.jpg"
        return f"{item['id']}.jpg"
        
    def file_path(self, request, response=None, info=None, *, item=None):
        """Devuelve el nombre de la ruta donde está descargada la imagen
        del producto

        :param request: solicitud del producto
        :type request: Request
        :param response: respuesta del producto, valor por defecto None
        :type response: Response, opcional
        :param info: información de la descarga, valor por defecto None
        :param item: item a procesar, valor por defecto None
        :type item: PrendaItem, opcional
        :return: nombre de la ruta de la imagen
        :rtype: string
        """        
        if item:
            return self.generador_ruta_imagen(None, item)
    
    def thumb_path(self, request, thumb_id, response=None, info=None, *, item=None):
        """Devuelve el nombre de la ruta donde está descargada la miniatura
        del producto

        :param request: solicitud del producto
        :type request: Request
        :param thumb_id: identificador de la miniatura
        :type thumb_id: int
        :param response: respuesta del producto, valor por defecto None
        :type response: Response, opcional
        :param info: información de la descarga, valor por defecto None
        :param item: item a procesar, valor por defecto None
        :type item: PrendaItem, opcional
        :return: nombre de la ruta de la miniatura
        :rtype: string
        """        
        if item:
            return self.generador_ruta_imagen('miniaturas', item)
    
    def item_completed(self, results, item, info):
        """Se llama a este método cuando se han descargado todas las imágenes
        de un ítem

        :param results: resultados de la descarga
        :param item: item a procesar
        :type item: PrendaItem
        :param info: información de la descarga
        :raises DropItem: excepción que se lanza para descarar un ítem si no tiene imagen descargada o tiene una marca desconocida
        :return: se devuelve el ítem para que siga pasando por las clases de Item Pipelines
        :rtype: PrendaItem
        """        

        nombres_imagenes = [x["path"] for ok, x in results if ok]
        if not nombres_imagenes:
            raise DropItem(f"Descartado {item.get('url')}: articulo sin imagen descargada")
        if not nombres_imagenes[0]:
            raise DropItem(f"Descartado {item.get('url')}: articulo sin imagen descargada")
        match(item['marca']):
            case 'Zara':
                ruta_relativa = "zara/"
            case 'H&M':
                ruta_relativa = "hm/"
            case 'Carhartt':
                ruta_relativa = "carhartt/"
            case _:
                raise DropItem(f"Descartado {item.get('url')}: articulo con marca desconocida")
        
        item['ruta_imagen'] = ruta_relativa + nombres_imagenes[0]
        item['ruta_miniatura'] = ruta_relativa + 'miniaturas/' + nombres_imagenes[0]
        return item
