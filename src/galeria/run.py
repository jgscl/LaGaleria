"""
tuto está en verde porque se reconoce como paquete. Se reconoce como
paquete porque la carpeta "tuto" tiene un archivo __init__.py
"""

from gestion_galeria import app

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True, host="0.0.0.0")