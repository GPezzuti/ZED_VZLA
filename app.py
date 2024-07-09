import datetime
import MySQLdb
from flask import Flask, request, jsonify
from models import db, Saludo

# Configuración de la aplicación
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:12345678@host.docker.internal:3306/zed_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Crear la base de datos si no existe
def create_database():
    connection = MySQLdb.connect(
        host="host.docker.internal",
        user="admin",
        passwd="12345678"
    )
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS zed_db;")
    cursor.close()
    connection.close()


# Llamar a la función para crear la base de datos
create_database()

# Inicializar SQLAlchemy
db.init_app(app)


# Rutas de la API
@app.route('/saludos', methods=['GET'])
def get_saludos():
    saludos = Saludo.query.all()
    return jsonify(
        [{'id': saludo.id, 'mensaje': saludo.mensaje, 'fecha_creacion': saludo.fecha_creacion} for saludo in saludos])


@app.route('/saludos', methods=['POST'])
def add_saludo():
    data = request.get_json()
    nuevo_saludo = Saludo(mensaje=data['mensaje'])
    db.session.add(nuevo_saludo)
    db.session.commit()
    return jsonify(
        {'id': nuevo_saludo.id, 'mensaje': nuevo_saludo.mensaje, 'fecha_creacion': nuevo_saludo.fecha_creacion}), 201


@app.route('/saludos/<int:id>', methods=['GET'])
def get_saludo(id):
    saludo = Saludo.query.get_or_404(id)
    return jsonify({'id': saludo.id, 'mensaje': saludo.mensaje, 'fecha_creacion': saludo.fecha_creacion})


@app.route('/saludos/buscar', methods=['GET'])
def buscar_saludos():
    query = request.args.get('q', '')
    saludos = Saludo.query.filter(Saludo.mensaje.like(f'%{query}%')).all()
    return jsonify(
        [{'id': saludo.id, 'mensaje': saludo.mensaje, 'fecha_creacion': saludo.fecha_creacion} for saludo in saludos])


@app.route('/saludos/filtrar', methods=['GET'])
def filtrar_saludos():
    fecha = request.args.get('fecha', '')
    try:
        fecha_creacion = datetime.strptime(fecha, '%Y-%m-%d')
        saludos = Saludo.query.filter(Saludo.fecha_creacion >= fecha_creacion).all()
        return jsonify(
            [{'id': saludo.id, 'mensaje': saludo.mensaje, 'fecha_creacion': saludo.fecha_creacion} for saludo in
             saludos])
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD.'}), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear las tablas si no existen
    app.run(host='0.0.0.0', port=5000)
