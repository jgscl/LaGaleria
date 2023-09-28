"""
El código de los archivos __init__.py se ejecuta al importar el paquete
en el que se encuentra __init__.py (gestion en este caso) o al importar cualquier 
modulo que se encuentre en el paquete con __init__. Por el simple hecho de encontrarse en una carpeta,
__init__.py ya define dicha carpeta como paquete en Python
"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+mariadbconnector://flaskserver:aclassserver@localhost:3306/prendas'
#Numero aleatorio generado con os.urandom(12)
app.config['SECRET_KEY'] = '44293aebb306aa1ea389d83f'
app.config['UPLOAD_FOLDER'] = '/home/j/prendas/imagenes'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

"""Al importar un modulo, python ejecuta todo su codigo, asi que lo ponemos en __init__.py
para que se ejecute"""

from gestion_galeria import direccionamiento
from gestion_galeria import modelos
