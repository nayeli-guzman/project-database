import psycopg2
import random
from faker import Faker
from datetime import datetime, timedelta

# Crear una instancia de Faker
fake = Faker()

# Conexión a la base de datos
conn = psycopg2.connect(
    dbname='proyecto',
    user='postgres',
    password='postgress',
    host='localhost',
    port='5432'
)
conn.autocommit = True
cursor = conn.cursor()

# Establecer el esquema
cursor.execute('SET search_path TO _1k')

# Funciones para poblar las tablas

def populate_usuario(num_records):
    usuarios = []
    for _ in range(num_records):
        id_u = fake.unique.bothify(text='U????????')
        nombre = fake.first_name()[:50]
        apellido = fake.last_name()[:50]
        genero = random.choice(['M', 'F'])
        celular = fake.phone_number()[:9]  # Tomar solo los primeros 9 dígitos
        email = fake.email()[:50]
        fecha_naci = fake.date_of_birth(minimum_age=18, maximum_age=80)
        contrasenia = fake.password(length=10)
        
        cursor.execute("""
            INSERT INTO Usuario (id_u, nombre, apellido, genero, celular, email, fecha_naci, calificacion, contrasenia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (id_u, nombre, apellido, genero, celular, email, fecha_naci, 0, contrasenia))
        
        usuarios.append(id_u) 
    
    return usuarios  

def populatePassengerDriver(usuarios):
    
    passengers = []
    drivers = []

    for id_u in usuarios:
        es_pasajero = random.choice([True, False])  
        # es_conductor = random.choice([True, False])  
        
        if es_pasajero:
            cursor.execute("""
                INSERT INTO Pasajero (id_u)
                VALUES (%s)
            """, (id_u,))
            passengers.append(id_u)
        else:
            licencia = fake.unique.bothify(text='???-#####')  
            cursor.execute("""
                INSERT INTO Conductor (id_u, licencia, num_viajes)
                VALUES (%s, %s, %s)
            """, (id_u, licencia, 0))
            drivers.append(id_u)
    
    return passengers, drivers

def populateRoutes(drivers):

    routes = []
    
    for i in range(len(drivers)):
        id_r = fake.unique.bothify(text='R???##??#?')
        id_u = random.choice(drivers)

        capacidad = random.randint(1, 7) 
        
        pto_partida = 'UTEC'
        pto_llegada = fake.bothify('(######.##,######.##)')
        
        estado = 'A'
        # estado = random.choice(['A', 'D'])
        
        cursor.execute("""
            INSERT INTO Rutas (id_r, id_u, capacidad, pto_partida, pto_llegada, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_r, id_u, capacidad, pto_partida, pto_llegada, estado))

        routes.append((id_r, id_u))
    return routes

def populateBooking(passengers, routes):
    
    solicitudes = []
    
    for i in range(len(passengers)):
        id_sv = fake.unique.bothify(text='S?????????')
        
        Pid_u = random.choice(passengers)
        
        id_r, Cid_u = random.choice(routes)
        
        fecha_realizada = fake.date_this_month(before_today=True, after_today=False)
        hora = fake.time()
        fecha_realizada = datetime.combine(fecha_realizada, datetime.strptime(hora, "%H:%M:%S").time())
        
        tiempo_atencion = None if random.choice([True, False]) else fecha_realizada + timedelta(hours=random.randint(1, 48))
        estado = 'realizada'
        
        if (tiempo_atencion is not None):
            estado = random.choice(['aceptado', 'cancelado', 'rechazado'])
        
        cursor.execute("""
            INSERT INTO Solicitud (id_sv, Pid_u, id_r, Cid_u, fecha_realizada, tiempo_atencion, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_sv, Pid_u, id_r, Cid_u, fecha_realizada, tiempo_atencion, estado))
        solicitudes.append(id_sv)

    return solicitudes

usuarios = populate_usuario(10)
[passengers, drivers] = populatePassengerDriver(usuarios)
routes = populateRoutes(drivers)
bookings = populateBooking(passengers, routes)

# Cerrar la conexión
cursor.close()
conn.close()
