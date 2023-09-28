"""Si queremos importar una variable inicializada en __init__.py hay que poner
from <paquete> import <variable>, como en este caso app"""

from gestion_galeria import app
from flask import render_template, redirect, url_for, flash, send_from_directory, request, abort
from gestion_galeria.modelos import Item
from gestion_galeria.formulario import FormularioRegistro, FormularioAcceso
from gestion_galeria.modelos import Usuario
from gestion_galeria import db
from flask_login import login_user, logout_user
from sqlalchemy import or_

"""
Dirección donde se mostrarán las prendas
"""

@app.route('/')
@app.route('/galeria', methods=['GET', 'POST'])
def galeria_page():

    """Se obtiene el número de página, que en caso de no darse o ser erróneo, el valor por defecto es 1"""
    pagina = request.args.get('page', 1, type=int)

    """Si el método es POST, es decir, se envía petición de filtrado de prendas"""
    if request.method == 'POST':
        paginas = []

        """Se obtienen los valores cada parámetro en listas"""
        prenda = request.form.getlist('prenda')
        genero = request.form.getlist('genero')
        color = request.form.getlist('color')
        marca = request.form.getlist('marca')
        composicion = request.form.getlist('composicion')
        orden_precio = request.form.get('ordenar')

        """Lista que contendrá todos los parámetros de la consulta a la base de datos"""
        lista_query = []

        """En los siguientes if se comprueba si las listas de los parámetros de los filtros contienen
        algún valor. En caso afirmativo se genera una comprobación de ese valor y se añade a la lista que
        contiene todas las condiciones para generar una consulta final con todas las comprobaciones"""
        if prenda:
            lista_query_prenda = []
            for p in prenda:
                """Se comprueba que el parámetro nombre contiene el tipo de prenda seleccionada"""
                lista_query_prenda.append(Item.nombre.like(f"%{p}%"))
                match p:
                    case 'jerséi':
                        lista_query_prenda.append(Item.nombre.like(f"%jersey%"))
                    case 'pantalón':
                        lista_query_prenda.append(Item.nombre.like(f"%jeans%"))
                        lista_query_prenda.append(Item.nombre.like(f"%chinos%"))
                        lista_query_prenda.append(Item.nombre.like(f"%bermuda%"))
                        lista_query_prenda.append(Item.nombre.like(f"%shorts%"))
            lista_query.append(or_(*lista_query_prenda))
 
        if genero:
            query_genero = Item.genero.in_(genero)
            lista_query.append(query_genero)
        if color:
            query_color = Item.color.in_(color)
            lista_query.append(query_color)
        if marca:
            query_marca = Item.marca.in_(marca)
            lista_query.append(query_marca)
        if composicion:
            lista_query_composicion = []
            for c in composicion:
                lista_query_composicion.append(Item.composicion.like(f"%{c}%"))
            lista_query.append(or_(*lista_query_composicion))
        
        """Se ordena el precio de menor a mayor, de mayor a menor o no se ordena"""
        if orden_precio and orden_precio == 'preciomenor':
            paginas = Item.query.filter(*lista_query).order_by(Item.precio.asc()).paginate(page=pagina, per_page=40)
        elif orden_precio and orden_precio == 'preciomayor':
            paginas = Item.query.filter(*lista_query).order_by(Item.precio.desc()).paginate(page=pagina, per_page=40)
        else:
            paginas = Item.query.filter(*lista_query).paginate(page=pagina, per_page=40)

    elif request.method == 'GET':
        paginas = Item.query.paginate(page=pagina, per_page=40)

    if paginas:
        filas = len(paginas.items) // 4
        resto = len(paginas.items) % 4

        if resto != 0:
            filas += 1
    else:
        filas = 0
        resto = 0

    return render_template('galeria.html', paginas=paginas, filas=filas, resto=resto)

"""
Si una URL necesita el método POST de http, es necesario declararlo.
Los métodos de registro necesitan POST pues se pasa info al servidor
"""
"""
Al hacer login o registro, primero para obtener el html se usa el método GET y una vez
se rellena y se clicka Aceptar, se manda en método POST
Ejecución GET:
1 - form = FormularioRegistro()
2 - return = render_template(...)

Ejecución POST:
1 - form = ...
2 - if form.validate_on_submit()
3 - if form.errors (si son incorrectos los datos)
"""
@app.route('/registro', methods=['GET', 'POST'])
def register_page():
    form = FormularioRegistro()

    #Se chequea si el usuario ha clickado el botón de Aceptar/Submit
    #contrasena se ejecuta como setter, más menos
    if form.validate_on_submit():
        nuevo_usuario = Usuario(nombre_usuario=form.nombre_usuario.data,
                                email=form.email.data,
                                contrasena=form.contrasena.data)
        #Se añade el nuevo usuario a la bbdd
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash(f"Te has registrado como \"{nuevo_usuario.nombre_usuario}\" correctamente. Inicia sesión", category='success')

        #redireccionamos a la pagina principal de la tienda
        return redirect(url_for('login_page'))

    #Se chequea que no ha habido errores al rellenar el formulario
    if form.errors != {}:
        #En caso de haber errores se notifica al usuario con un mensaje flash
        for mensaje_error in form.errors.values():
            flash(f"Error al registrar usuario: {mensaje_error}", category='danger')

    return render_template('registro.html', form=form)

"""
Dirección para iniciar sesión
"""
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = FormularioAcceso()

    """En caso de darle a aceptar al iniciar sesión y comprobarse los parámetros"""
    if form.validate_on_submit():
        usuario_actual = Usuario.query.filter_by(nombre_usuario=form.nombre_usuario.data).first()

        """Si el usuario introducido existe y la contraseña es correcta"""
        if usuario_actual and usuario_actual.comprobar_hash_contrasena(
            posible_contrasena=form.contrasena.data):
            login_user(usuario_actual)
            flash(f"¡Éxito! Has accedido como {usuario_actual.nombre_usuario}", category='success')
            return redirect(url_for('galeria_page'))
        else:
            flash(f"¡Error! El usuario o la contraseña con incorrectos", category='danger')

    return render_template('acceso.html', form=form)

"""
Dirección para cerrar sesión
"""
@app.route('/logout')
def logout_page():
    logout_user()
    flash('Has cerrado sesión de forma correcta. ¡Vuelve Pronto!', category='info')

    return redirect(url_for('home_page'))

"""
Dirección para acceder a la información del ítem seleccionado
"""
@app.route('/<int:item_id>')
def item_page(item_id):
    item = Item.query.filter_by(id=item_id).first()
    return render_template('item.html', item=item)

"""
API para obtener las imágenes de forma dinámica
"""
@app.route('/obtener_imagen')
def get_image():

    id_imagen = request.args.get('id')
    miniatura = request.args.get('miniatura')

    if id_imagen and id_imagen.isdigit() and (miniatura == '0' or miniatura == '1'):
        item = Item.query.filter_by(id=int(id_imagen)).first()

        if not item:
            abort(404)
        if miniatura == '0':
            ruta_imagen = item.ruta_imagen

            return send_from_directory(app.config['UPLOAD_FOLDER'], ruta_imagen, mimetype='image/jpeg')
        
        ruta_imagen = item.ruta_miniatura
        return send_from_directory(app.config['UPLOAD_FOLDER'], ruta_imagen, mimetype='image/jpeg')
        
    abort(400)

@app.route('/huevo_de_pascua')
def huevo_de_pascua():
    return render_template('huevo_pascua.html')