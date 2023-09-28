from scrapy.exceptions import DropItem

class PipelineNinos:
    """Clase de Item Pipelines cuya función es la de descartar a prendas de Zara que sean
    de niños
    """    
    
    def process_item(self, item, spider):
        """Función de procesamiento del item. Descarta un ítem si contiene el valor 'NIÑOS'
        en el campo de género, como ocurre con los ítems de niños de Zara

        :param item: item a procesar
        :type item: PrendaItem
        :param spider: araña asociada a esta clase de Item Pipeline
        :type spider: Spider
        :raises DropItem: excepción que se lanza en caso de que se quiera rechazar un ítem
        :return: se devuelve el item para que siga pasando por el resto de clases de Item Pipelines
        :rtype: PrendaItem
        """        
        
        if item['genero'].upper() == 'NIÑOS':
            raise DropItem(f"Descartado {item['nombre']}: articulo de ninos") 
        return item