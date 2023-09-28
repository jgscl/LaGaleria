from gestion_galeria import db, bcrypt, login_manager
from flask_login import UserMixin

"""
Esta funcion es una callback para recargar el usuario dado su user_id almacenado
en la sesión. Es necesaria para que los usuarios puedan mantener el acceso
a la pagina web
"""
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

"""
Se ha añadido la herencia de UserMixin pues esta clase contiene los métodos:
- is_authenticated
- is_active
- is_anonymous
- get_id()
Es necesario para que el usuario pueda mantener el acceso a la pagina web
"""
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(length=15), nullable = False, unique=True)
    email = db.Column(db.String(length=50), nullable = False, unique=True)
    hash_contrasena = db.Column(db.String(length=64), nullable=False)

    #filtros

    @property
    def contrasena(self):
        return self.contrasena
    
    @contrasena.setter
    def contrasena(self, contrasena_texto_llano):
        self.hash_contrasena = bcrypt.generate_password_hash(contrasena_texto_llano).decode('utf-8')

    def comprobar_hash_contrasena(self, posible_contrasena):
        return bcrypt.check_password_hash(self.hash_contrasena, posible_contrasena)

class Item(db.Model):
    __tablename__ = 'item'

    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    nombre = db.Column(db.String(length=100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    url_imagen = db.Column(db.String(length=250), nullable=False)
    genero = db.Column(db.String(length=30), nullable=False)
    color = db.Column(db.String(length=30), nullable=False)
    descripcion = db.Column(db.String(length=800), nullable=False)
    marca = db.Column(db.String(length=30), nullable=False)
    url = db.Column(db.String(length=200), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    composicion = db.Column(db.String(length=100), nullable=False)
    ruta_imagen = db.Column(db.String(length=100), nullable=False)
    ruta_miniatura = db.Column(db.String(length=100), nullable=False)

    def __repr__(self):
        return f"Item {self.id} - {self.nombre}"