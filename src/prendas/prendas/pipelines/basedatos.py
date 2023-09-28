import mariadb

from scrapy.exceptions import DropItem

class PipelineBaseDatos:
    """Clase de Item Pipelines cuya función es la de insertar los items en la base de datos
    """    


    def process_item(self, item, spider):
        """Función de procesamiento del item. Se inserta un objeto :class 'prendas.items.prendaitem.PrendaItem' 
        :class `prendas.items.prendaitem.PrendaItem` en la base de datos.

        :param item: ítem a procesar
        :type item: PrendaItem
        :param spider: araña asociada a esta clase de Item Pipeline
        :type spider: Spider
        :raises DropItem: excepción que se lanza en caso de descartar un ítem
        :return: se devuelve el ítem para que siga pasando por las clases de Item Pipelines
        :rtype: PrendaItem
        """ 

        sentencia = """
        INSERT INTO item (id, nombre, precio, url_imagen, genero, color, descripcion, marca, url, fecha, composicion, ruta_imagen, ruta_miniatura) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE
            nombre = VALUES(nombre),
            precio = VALUES(precio),
            url_imagen = VALUES(url_imagen),
            genero = VALUES(genero),
            color = VALUES(color),
            descripcion = VALUES(descripcion),
            marca = VALUES(marca),
            url = VALUES(url),
            fecha = VALUES(fecha),
            composicion = VALUES(composicion),
            ruta_imagen = VALUES(ruta_imagen),
            ruta_miniatura = VALUES(ruta_miniatura);
        """
        valores = (item['id'], item['nombre'], item['precio'], item['url_imagen'], item['genero'], 
                   item['color'], item['descripcion'], item['marca'], item['url'], item['fecha'], 
                   item['composicion'], item['ruta_imagen'], item['ruta_miniatura'])
        
        try:
            self.cursor.execute(sentencia, valores)

            self.conn.commit()
        except mariadb.Error as err:
            raise DropItem(f"Descartado {item.get('url')}, error en MariaDB: {err}, {valores}")
        else:
            return item

    def open_spider(self, spider):
        """Método que se activa al abrirse la araña asociada a esta clase de Item Pipelines.
        Su función es la de crear una conexión a la base de datos para posteriormente acceder a ella.

        :param spider: araña asociada a esta clase de Item Pipelines
        :type spider: Spider
        """        
        
        try:
            self.conn = mariadb.connect(
                user='scrapybot',
                password='aclassscraper',
                host='localhost',
                database='prendas'
            )

        except mariadb.Error as err:
            self.logger.error(f"Error al conectar a MariaDB: {err}")
        else:
            self.cursor = self.conn.cursor()
    
    def close_spider(self, spider):
        """Método que se activa al cerrarse la araña asociada a esta clase de Item Pipelines.
        Su función es la de cerrar la conexión a la base de datos de forma segura.

        :param spider: araña asociada a esta clase de Item Pipelines
        :type spider: Spider
        """        
        self.cursor.close()
        self.conn.close()

