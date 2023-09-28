from scrapy.item import Item, Field

from itemloaders.processors import Join, TakeFirst, Identity

class PrendaItem(Item):
    """Clase que representa una prenda de ropa
    """    
    id = Field()
    nombre = Field()
    precio = Field()
    url_imagen = Field()
    ruta_imagen = Field()
    ruta_miniatura = Field()
    genero = Field()
    color = Field()
    descripcion = Field()
    marca = Field()
    composicion = Field()
    
    url = Field()
    fecha = Field()