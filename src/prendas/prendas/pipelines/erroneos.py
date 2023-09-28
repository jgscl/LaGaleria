from scrapy.exceptions import DropItem

class PipelineErroneos:
    """Clase de Item Pipelines cuya función es la de descartar a prendas que carezcan de algún campo
    como nombre, precio, url_imagen, género o descripción
    """    

    def process_item(self, item, spider):
        """Función de procesamiento del item. Descarta un ítem en caso de que carezca de algún campo.

        :param item: ítem a procesar
        :type item: PrendaItem
        :param spider: araña asociada a esta clase de Item Pipeline
        :type spider: Spider
        :raises DropItem: excepción que se lanza para descartar un ítem
        :return: se devuelve el item para que siga pasando por las clases de Item Pipelines
        :rtype: PrendaItem
        """        
        
        if item.get('nombre') is None: 
            raise DropItem(f"Descartado {item.get('url')}: articulo sin nombre")
        if item.get('precio') is None: 
            raise DropItem(f"Descartado {item.get('url')}: articulo sin precio")
        if item.get('url_imagen') is None:
            raise DropItem(f"Descartado {item.get('url')}: articulo sin url_imagen")  
        if item.get('genero') is None:
            raise DropItem(f"Descartado {item.get('url')}: articulo sin genero")
        if item.get('descripcion') is None:
            raise DropItem(f"Descartado {item.get('url')}: articulo sin descripcion")
        return item