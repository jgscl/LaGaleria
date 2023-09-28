import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from prendas.spiders.zara import ZaraSpider
from prendas.spiders.hm import HmSpider
from prendas.spiders.carhartt import CarharttSpider

import logging

from datetime import datetime
import mariadb
import json

def create_db_connection():
    """Crea la conexión con la base de datos

    :raises mariadb.Error: excepción que se lanza si hay algún error al crear la conexión con la base de datos
    :return: devuelve la conexión y el cursor de la base de datos
    """    
    try:
        conn = mariadb.connect(
        user='scrapybot',
        password='aclassscraper',
        host='localhost',
        database='prendas'
        )
        cursor = conn.cursor()

    except mariadb.Error as err:
        raise mariadb.Error(f"Error al crear la conexion a MariaDB por {__file__}: {err}")
    else:
        return conn, cursor

def get_zara_database_urls(cursor):
    """Se obtienen las URLs de todos los productos de Zara de la base de datos

    :param cursor: cursor de la base de datos
    :raises mariadb.Error: excepción que se lanza si hay algún error al ejecutar la sentencia
    :return: lista de URLs de productos de Zara
    :rtype: list
    """

    try:
        sentencia = "SELECT url FROM item WHERE marca = 'Zara'"
        cursor.execute(sentencia)
        urls_sitemap = cursor.fetchall()
    
    except mariadb.Error as err:
        raise mariadb.Error(f"Error al obtener las urls de MariaDB por {__file__}: {err}")
    else:
        return urls_sitemap

def close_db(conn, cursor):
    """Se cierra la conexión con la base de datos

    :param conn: conexión con la base de datos
    :param cursor: cursor de la base de datos
    :raises mariadb.Error: excepción que se lanza si hay algún error al cerrar la base de datos
    """
    try:
        cursor.close()
        conn.close()
    except mariadb.Error as err:
        raise mariadb.Error(f"Error al cerrar MariaDB por {__file__}: {err}")

def main():
    """Se obtienen las URLs de los productos de Zara, se pasan a la araña de Zara por parámetro y
    se ejecutan las arañas de Zara, H&M y Carhartt. Estas dos últimas de forma semanal los lunes
    """
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    logger = logging.getLogger('prendas')

    try:
        conn, cursor = create_db_connection()
        productos_bd = get_zara_database_urls(cursor)
        close_db(conn, cursor)

    except mariadb.Error as err:
        logger.error(f"{err}")
    else:
        if productos_bd:
            productos_bd = json.dumps(productos_bd)
    
        process.crawl(ZaraSpider, productos_bd=productos_bd)
        if datetime.today().date().strftime("%A").lower() == 'monday':
            process.crawl(HmSpider)
            process.crawl(CarharttSpider)
            
        process.start()

if __name__ == '__main__':
    main()

