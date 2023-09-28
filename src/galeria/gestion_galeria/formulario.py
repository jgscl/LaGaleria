from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, Email, DataRequired, EqualTo, ValidationError
from gestion_galeria.modelos import Usuario

class FormularioRegistro(FlaskForm):

    def validate_nombre_usuario(self, nombre_usuario_validar):
        nombre = Usuario.query.filter_by(nombre_usuario=nombre_usuario_validar.data).first()

        if nombre:
            raise ValidationError(f"El Nombre de Usuario \"{nombre_usuario_validar.data}\" ya existe. Elige otro.")

    def validate_email(self, email_validar):
        dir_correo = Usuario.query.filter_by(email=email_validar.data).first()

        if dir_correo:
            raise ValidationError(f"El Correo Electrónico \"{email_validar.data}\" ya existe. Elige otro.")

    nombre_usuario = StringField(label='Nombre de Usuario', validators=[Length(min=5, max=15), DataRequired()],
                                render_kw={'autocomplete': 'off'})
    email = StringField(label='Correo Electrónico', validators=[Email(), DataRequired()],
                                render_kw={'autocomplete': 'off'})
    contrasena = PasswordField(label='Contrasena', validators=[Length(min=6), DataRequired()],
                                render_kw={'autocomplete': 'off'})
    conf_contrasena = PasswordField(label='Confirmar Contrasena', validators=[EqualTo('contrasena'), DataRequired()], 
                                render_kw={'autocomplete': 'off'})
    aceptar = SubmitField(label='Aceptar')

class FormularioAcceso(FlaskForm):
    nombre_usuario = StringField(label='Nombre de Usuario', validators=[DataRequired()], render_kw={'autocomplete': 'off'})
    contrasena = PasswordField(label='Contraseña', validators=[DataRequired()], render_kw={'autocomplete': 'off'})
    aceptar = SubmitField(label='Acceder')