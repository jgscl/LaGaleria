from datetime import datetime
import re
import hashlib
import unicodedata

class PipelineLimpieza:
    """Función de procesamiento del item. Se limpian y estandarizan los valores de los campos de los
    productos para que todos tengan el mismo formato y sean más fáciles de procesar
    """    

    def asignar_color(self, color_entrada):
        """A la cantidad de colores de entrada que hay, se le asigna un color predefinido

        :param color_entrada: color aislado de entrada
        :type color_entrada: string
        :return: color asignado
        :rtype: string
        """        
        
        #Color NEGRO
        if color_entrada == 'Negro' or color_entrada == 'Antracita' or color_entrada == 'Black':
            color_final = 'Negro' 

        #Color GRIS
        elif color_entrada == 'Gris' or color_entrada == 'Cemento' or color_entrada == 'Piedra' or (
            color_entrada == 'Grises' or color_entrada == 'Acero' or color_entrada == 'Hielo' or
            color_entrada == 'Plomo' or color_entrada == 'Grey' or color_entrada == 'Grisáceo'): 
            color_final = 'Gris'

        #Color BEIGE
        elif color_entrada == 'Beige' or color_entrada == 'Arena' or color_entrada == 'Mantequilla' or (
             color_entrada == 'Camel' or color_entrada == 'Cava' or color_entrada == 'Crema' or
             color_entrada == 'Crudo' or color_entrada == 'Vigoré' or color_entrada == 'Barquillo' or
             color_entrada == 'Cuerda' or color_entrada == 'Vainilla' or color_entrada == 'Whisk'):
            color_final = 'Beige'

        #Color MARRÓN
        elif color_entrada == 'Marrón' or color_entrada == 'Chocolate' or color_entrada == 'Tabaco' or (
        color_entrada == 'Tostado' or color_entrada == 'Visón' or color_entrada == 'Toffe' or
        color_entrada == 'Ocre' or color_entrada == 'Caramelo' or color_entrada == 'Tierra' or
        color_entrada == 'Terracota' or color_entrada == 'Arcilla' or color_entrada == 'Bronce' or
        color_entrada == 'Brown'):
            color_final = 'Marrón'

        #Color AZUL
        elif color_entrada == 'Azul' or color_entrada == 'Índigo' or color_entrada == 'Marino' or (
            color_entrada == 'Turquesa' or color_entrada == 'Azules' or color_entrada == 'Celeste' or
            color_entrada == 'Azulina' or color_entrada == 'Azulado' or color_entrada == 'Azulón' or
            color_entrada == 'Cobalto' or color_entrada == 'Blue'):
            color_final = 'Azul'

        #Color VERDE
        elif color_entrada == 'Verde' or color_entrada == 'Khaki' or color_entrada == 'Kaki' or (
            color_entrada == 'Lima' or color_entrada == 'Botella' or color_entrada == 'Aceite' or
            color_entrada == 'Esmeralda' or color_entrada == 'Oliva' or color_entrada == 'Verdoso' or
            color_entrada == 'Menta' or color_entrada == 'Pistacho' or color_entrada == 'Verde' or
            color_entrada == 'Green'):
            color_final = 'Verde'

        #Color AMARILLO
        elif color_entrada == 'Amarillo' or color_entrada == 'Mostaza' or color_entrada == 'Paja' or (
            color_entrada == 'Yellow'):
            color_final = 'Amarillo'
    
        #Color NARANJA
        elif color_entrada == 'Naranja' or color_entrada == 'Naranjas' or color_entrada == 'Calabaza' or (
            color_entrada == 'Teja' or color_entrada == 'Mandarina' or color_entrada == 'Melocotón' or
            color_entrada == 'Salmón' or color_entrada == 'Orange' or color_entrada == 'Albaricoque'):
            color_final = 'Naranja'

        #Color ROJO
        elif color_entrada == 'Rojo' or color_entrada == 'Rojos' or color_entrada == 'Burdeos' or (
            color_entrada == 'Granate' or color_entrada == 'Coral' or color_entrada == 'Vino' or
            color_entrada == 'Burgundy' or color_entrada == 'Caldero' or color_entrada == 'Red'): 
            color_final = 'Rojo'

        #Color ROSA
        elif color_entrada == 'Rosa' or color_entrada == 'Magenta' or color_entrada == 'Fucsia' or (
            color_entrada == 'Rosado' or color_entrada == 'Marsala' or color_entrada == 'Rosas' or
            color_entrada == 'Chicle' or color_entrada == 'Pink'):
            color_final = 'Rosa'

        #Color MORADO
        elif color_entrada == 'Morado' or color_entrada == 'Lila' or color_entrada == 'Púrpura' or (
            color_entrada == 'Malva' or color_entrada == 'Berenjena' or color_entrada == 'Violeta' or
            color_entrada == 'Lavanda' or color_entrada == 'Purple'):
            color_final = 'Morado'

        #Color PLATEADO
        elif color_entrada == 'Plateado' or color_entrada == 'Plata':
            color_final = 'Plateado'
        
        #Color DORADO
        elif color_entrada == 'Dorado' or color_entrada == 'Oro':
            color_final = 'Dorado'
    
        #Color BLANCO
        elif color_entrada == 'Blanco' or color_entrada == 'Hueso' or color_entrada == 'White':
            color_final = 'Blanco'

        #Color MULTICOLOR
        elif color_entrada == 'Multicolor' or color_entrada == 'Estampado' or color_entrada == 'Leopardo' or (
          color_entrada == 'Varios' or color_entrada == 'Serpiente' or color_entrada == 'Rayas'):
            color_final = 'Multicolor'
        
        #Otros colores (debug)
        else:
            #color_final = color_entrada + '_' + 'sin_color'
            color_final = 'sin_color'

        return color_final
    
    """
    De los posibles formatos de entrada de Zara en los que vienen los colores:
        1. Marino | 5584/461
        2. Beige claro | 4467/003
        3. Crudo / Azul | 3057/051
        4. 0120/510
        5. azul-empolvado | 6045/366 o Marrón/Estampado
    Se obtiene el primer color, Marino, Beige o Azul. En caso del formato X / Y se coge el color Y

    Esta función cubre los casos de colores de tipo H&M y Carhartt
    """

    def limpieza_color(self, color_entrada):
        """De la cadena obtenida del XPath se extrae el color y en caso de haber varios, el más importante

        :param color_entrada: cadena que contiene el color
        :type color_entrada: string
        :return: color aislado
        :rtype: string
        """        

        if color_entrada == None:
            return 'sin_color'

        # Primero se comprueba si tiene el formato más común, el 2 (aunque también vale para el 5)
        objeto_regex_color = re.match('^([a-zA-ZÍáéíóú]+)\s?[a-zA-Záéíóú]*', color_entrada.title())

        # Si la cadena de color es un número (caso 4)
        if objeto_regex_color is None:
            return 'sin_color'

        """
        Comprobamos si se trata de un formato de color normal (casos 1, 2 o 5) o formato "X / Y"
        - Normal: seleccionamos la primera parte del color, por ejemplo, de Verde Claro, Verde
        - X / Y: seleccionamos la parte Y de color, por ejemplo, de Crudo / Azul, Azul
        """
        
        objeto_regex_crudo = re.match('^[a-zA-ZÍÁÉÓÚáéíóú]+\s/\s([a-zA-ZÍÁÉÓÚáéíóú]+)', color_entrada.title())
        
        # Si no se da formato "X / Y"
        if objeto_regex_crudo is None:
            color_final = self.asignar_color(objeto_regex_color.group(1))
        
        # Si se da formato "X / Y"
        else:
            color_final = self.asignar_color(objeto_regex_crudo.group(1))

        return color_final

    """
    En Carhartt, dado que los nombres de los items están en inglés, se añade la traducción del tipo
    de prenda que sea.
    Por ejemplo:
    - url: https://www.carhartt-wip.com/es/mujer-camisetas/w-s-s-pocket-t-shirt-ash-heather-1217_1
    - nombre original: 'W' S/S Pocket T-Shirt'
    Dado que la url en español contiene "camiseta" el nombre final será:
    - nombre final: 'W' S/S Pocket T-Shirt - Camiseta Manga Corta'
    """

    def limpieza_nombre(self, item):
        """Si el producto no es de Carhartt se pone en formato xx y en caso de ser Carhartt se añade una
        traducción del tipo de producto que es al nombre pues este se encuentra en inglés

        :param item: item a procesar
        :type item: PrendaItem
        :return: nombre del producto
        :rtype: string
        """        

        if item.get('marca'):
            if item['marca'] != 'Carhartt':
                return item['nombre'].title()
            
        traduccion = None

        if re.search('camiseta', item['url']):
            if re.search('larga', item['url']):
                traduccion = 'Camiseta Manga Larga'
            else:
                traduccion = 'Camiseta Manga Corta'   
        if re.search('chaqueta', item['url']):
            traduccion = 'Chaqueta'
        if re.search('jersei', item['url']):
            traduccion = 'Jerséi'
        if re.search('sudadera', item['url']):
            if re.search('jogger', item['url']):
                traduccion = 'Pantalón Largo'
            else:
                traduccion = 'Sudadera'
        if re.search('camisa', item['url']):
            traduccion = 'Camisa'
        if re.search('pantalon', item['url']):
            traduccion = 'Pantalón Largo'
        if re.search('bermudas|shorts', item['url']):
            traduccion = 'Pantalón Corto'
        if re.search('mono', item['url']):
            traduccion = 'Mono'
        
        return f"{item['nombre'].title()} - {traduccion}"

    def limpieza_composicion(self, item):
        """Se asigna el valor 'sin_composicion' a los productos que no tengan composicion y se
        eliminan los caracters inútiles y se normaliza el valor de composición de los productos 
        de Carhartt porque contiene caracteres unicode extraños

        :param item: item a procesar
        :type item: PrendaItem
        :return: composición del ítem
        :rtype: string
        """        

        if item.get('composicion') is None:
            return 'sin_composicion'
        
        if item.get('marca'):
            if item['marca'] == 'Carhartt':
                composicion = re.sub('^[^0-9]+', '', item['composicion'])
                """
                Nuevo algoritmo de normalizado NFC que sustituye a NFKD porque formaba de forma
                incorrecta para este proyecto los caracteres con acento
                """
                #composicion_normalizada = unicodedata.normalize('NFKD', composicion)
                composicion_normalizada = unicodedata.normalize('NFC', composicion)
    
                return composicion_normalizada
            return item['composicion']

    def crear_id(self, url):
        """Crea el id de cada ítem con los últimos 10 dígitos del número entero producido por
        el algoritmo de hashing MD5. Se utiliza como elemento de entrada para hacer el hash
        la URL del producto ya que es única.

        :param url: URL del producto
        :type url: string
        :return: identificador del producto
        :rtype: int
        """        
        s = url.encode()
        return int(hashlib.md5(s).hexdigest(), 16) % 10000000000
    
    """
    Formato final de los campos:
    - nombre: la primera letra de cada palabra mayúscula, el resto en minúsculas.
    En caso de Carhartt al estar en inglés se incluye el tipo de prenda que es en español
    - precio: número decimal
    - genero: 'Hombre' o 'Mujer'
    - id: número decimal de 10 dígitos
    - color: uno de los siguientes colores, negro, gris, beige, marrón, azul, verde, amarillo,
    naranja, rojo, rosa, plateado, dorado, blanco, multicolor o sin_color en caso de error,
    color desconocido o no tener color.
    - composicion: tiene que tener el material y el porcentaje que lleva de dicho material la prenda
    - fecha: formato aaaa-mm-dd hh:mm:ss
    - url: url normal excluyéndo los métodos llamados dentro del recurso. https://....html (o sin html)
    """

    def process_item(self, item, spider):
        """Función de procesamiento del item. Llama a distintos métodos para que hagan labores de limpieza 
        y estandarización de los campos de los ítems

        :param item: ítem a procesar
        :type item: PrendaItem
        :param spider: araña asociada con esta clase de Item Pipeline
        :type spider: Spider
        :return: se devuelve el ítem para que siga pasando por las clases de Item Pipelines
        :rtype: PrendaItem
        """        
        item['nombre'] = self.limpieza_nombre(item)
        item['precio'] = float(item['precio'].replace(',', '.'))
        item['genero'] = item['genero'].title()
        item['id'] = self.crear_id(item['url'])
        item['color'] = self.limpieza_color(item.get('color'))
        item['composicion'] = self.limpieza_composicion(item)
        #item['fecha'] = item['fecha'].astimezone().strftime("%d-%m-%Y %H:%M:%S")
        item['fecha'] = item['fecha'].astimezone().strftime("%Y-%m-%d %H:%M:%S")
        if re.search('html', item['url']):
            item['url'] = (re.match('.+[.]html', item['url'])).group()
        return item
        

    