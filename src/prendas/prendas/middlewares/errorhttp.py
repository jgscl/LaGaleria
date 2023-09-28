from scrapy.exceptions import IgnoreRequest

import logging

class ErrorHttpDownloaderMiddleware:
    """DownloadeMiddleware cuya función es la de cerrar una araña si esta ha recibido más de max_errores códigos
    HTTP 403 seguidos porque si se han recibido tantos significa que se le ha prohibido el acceso a la página
    """    

    def __init__(self):
        """Constructor de ErrorHttpDownloaderMiddleware
        """
        self.contador_zara = 0
        self.contador_hm = 0
        self.contador_carhartt = 0
        self.previo_zara = False
        self.previo_hm = False
        self.previo_carhartt = False
        self.max_errores = 50

        self.logger = logging.getLogger('prendas')
    """
    @classmethod
    def from_crawler(cls, crawler):
        Instancia la 

        :param crawler: _description_
        :type crawler: _type_
        :return: _description_
        :rtype: _type_
        
        settings = crawler.settings
        max_errores = settings.getint('MAX_HTTP_ERRORS_MIDDLEWARE', 50)
        return cls(max_errores)
    """
    def process_response(self, request, response, spider):
        """Función de procesamiento de respuestas de los Middlewares. Llama a la función gestion_codigo_error()
        para analizar la respuesta que ha recibido la araña spider y se actualizan los valores de contador de
        errores 403 y el estado previo del error HTTP

        :param request: petición asociada con la respuesta recibida
        :type request: Request
        :param response: respuesta recibida
        :type response: Response
        :param spider: araña que ha recibido la respuesta
        :type spider: Spider
        :return: respuesta recibida
        :rtype: Response
        """

        match spider.name:
            case 'zara':
                self.contador_zara, self.previo_zara = self.gestion_codigo_http(
                    response, self.contador_zara, self.previo_zara, spider)

            case 'hm':
                self.contador_hm, self.previo_hm = self.gestion_codigo_http(
                    response, self.contador_hm, self.previo_hm, spider)

            case 'carhartt':
                self.contador_carhartt, self.previo_carhartt = self.gestion_codigo_http(
                    response, self.contador_carhartt, self.previo_carhartt, spider)
        
        if response.status >= 400 and response.status < 500:
            #self.logger.warning(f"{response.status}: peticion a {response.url}")
            raise IgnoreRequest

        return response

    def gestion_codigo_http(self, response, contador, previo, spider):
        """Si se reciben max_errores códigos HTTP 403 seguidos, se cierra la araña que ha recibido dicho código porque se
        le ha prohibido el acceso a la página web. En caso de recibir un código 200 se resetea el contador. 

        :param estatus_http: código HTTP recibido en la última respuesta
        :type estatus_http: int
        :param contador: contador de códigos HTTP 403
        :type contador: int
        :param previo: indica si en la previa respuesta se recibió un código 403 (True) o no (False)
        :type previo: boolean
        :param spider: araña que ha recibido la respuesta
        :type spider: Spider
        :return: devuelve el contador y el estado previo para actualizar los valores
        :rtype: int, boolean
        """
        if response.status == 403:
            contador += 1
            previo = True
        elif response.status == 200:
            previo = False
        if not previo:
            contador = 0
        if contador == self.max_errores:
            self.logger.warning(f"Cerrando spider '{spider.name}' por exceso de códigos de error HTTP 403")
            spider.crawler.engine.close_spider(
                spider, f"Cerrando spider '{spider.name}' por exceso de códigos de error HTTP 403")

        return contador, previo
