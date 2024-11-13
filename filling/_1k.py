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

def populateUser(num_records):
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
            """, (id_u, licencia, random.randrange(start=0, step=1, stop=50)))
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

    travels = []
        
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

        if(estado=='aceptado'):
            travels.append(populateTravel(id_sv, tiempo_atencion))

    return travels

def populateTravel(id_sv, tiempo_atencion):

    id_v = fake.unique.bothify(text='T#######')
    distancia = round(random.uniform(5.0, 500.0), 2)  
    fecha = tiempo_atencion + timedelta(hours=random.randint(1, 48))
    
    duracion = timedelta(minutes=random.randint(30, 300))
    estado = random.choice(['realizada', 'cancelada', 'enproceso'])    
    destino = fake.bothify("(#####.##)")
    
    cursor.execute(
        """
        INSERT INTO Viaje (id_v, id_sv, distancia, fecha, duracion, estado, destino)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (id_v, id_sv, distancia, fecha, duracion, estado, destino)
    )
    
    return (id_v, id_sv)

def populateReview(travels):

    for i in range(len(travels)):

        conf = random.choice([0,1])

        if (conf==1):
            id_v, id_sv = travels[i]
            
            puntuacion = random.randint(0, 5)
            comentario = fake.sentence(nb_words=15)[:100]
            tipo = random.choice(['P', 'C'])
            
            cursor.execute(
                """
                INSERT INTO Calificacion(id_v, id_sv, puntuacion, comentario, tipo)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (id_v, id_sv, puntuacion, comentario, tipo)
            )
            conf = random.choice([0,1])
            if (conf==1):
                tipo= (tipo=='P')*'C' + (tipo=='C')*'P' 
                puntuacion = random.randint(0, 5)
                comentario = fake.sentence(nb_words=15)[:100]
                
                cursor.execute(
                    """
                    INSERT INTO Calificacion (id_v, id_sv, puntuacion, comentario, tipo)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (id_v, id_sv, puntuacion, comentario, tipo)
                )

def populatePayment(travels):
    for i in range(len(travels)):
        id_v, id_sv = travels[i]
        
        monto = round(random.uniform(0.0, 20.0), 2)        
        metodo = random.choice(['yape', 'plin', 'efectivo'])
        id_p = fake.uuid4()[:10]  # Genera un ID único truncado a 10 caracteres
        
        cursor.execute("""
            INSERT INTO Pago (id_p, id_v, id_sv, monto, metodo)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_p, id_v, id_sv, monto, metodo))

def populateVehicles(drivers):
    for driver in (drivers):
        id_u = driver
        
        placa = fake.license_plate()[:10]  
        modelo = fake.word()[:10]  
        capacidad = random.randint(1, 7) 
        soat = str(random.randint(10000, 99999)) 
        imagen_path = f"images/{fake.word()}.jpg" 
        fecha_registro = fake.date_this_decade()  
        estado = random.choice(['U', 'N'])  
        
        cursor.execute("""
            INSERT INTO Vehiculos (placa, id_u, modelo, capacidad, SOAT, imagen_path, fecha_registro, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (placa, id_u, modelo, capacidad, soat, imagen_path, fecha_registro, estado))

def populateCouponsPassenger(passengers) :
    cp = []
    for i in range (passengers):
        idCp = fake.unique.bothify("CP########") 
        descuento = random.randint(5, 50)
        fecha_caducidad = fake.date_between(start_date=datetime.today(), end_date="+30d")
    
        cursor.execute("""
            INSERT INTO CuponP (idCp, descuento, fechaCaducidad)
            VALUES (%s, %s, %s)
        """, (idCp, descuento, fecha_caducidad))
        cp.append(idCp)
    conn.commit()
    return cp

def populateCouponsDriver(drivers) :
    cd = []
    for i in range (drivers):
        idCp = fake.unique.bothify("CC########") 
        descuento = random.randint(5, 50)
        fecha_caducidad = fake.date_between(start_date=datetime.today(), end_date="+30d")
        descripcion = fake.sentence(nb_words=6)[:50]  
        
        cursor.execute("""
            INSERT INTO CuponC (idCp, descuento, fechaCaducidad, descripcion)
            VALUES (%s, %s, %s, %s)
        """, (idCp, descuento, fecha_caducidad, descripcion))
        cd.append(idCp)
    conn.commit();
    return cd

def populatePenalizacion(users):
    for _ in range(len(users)):
        idPn = fake.unique.bothify("PE########")        
        id_u = random.choice(users)
        
        motivo = fake.sentence(nb_words=6)[:50]
        fecha_inicio = fake.date_between(start_date="-1y", end_date="today")  
        fecha_fin = fecha_inicio + timedelta(days=random.randint(1, 30)) 
        
        cursor.execute("""
            INSERT INTO penalizacion (idPn, id_u, motivo, fechaInicio, fechaFin)
            VALUES (%s, %s, %s, %s, %s)
        """, (idPn, id_u, motivo, fecha_inicio, fecha_fin))

def populateOtorgadoP(coupons, users):
    for i in range(len(coupons)):
        if (random.choice([True, False])):
            id_u =  random.choice(users)
            idCp = coupons[i]
            
            estado = random.choice(['usado', 'no usado'])
            
            fecha_uso = None
            if estado == 'usado':
                fecha_uso = str(fake.date_this_year(before_today=True, after_today=False)) + ' ' + str(fake.time()) 
            
            cursor.execute("""
                INSERT INTO otorgadoP (id_u, idCp, estado, fecha_uso)
                VALUES (%s, %s, %s, %s)
            """, (id_u, idCp, estado, fecha_uso))
    conn.commit();
    
def populateOtorgadoD(coupons, users):
    for i in range(len(coupons)):
        if (random.choice([True, False])):            
            id_u =  random.choice(users)
            idCp = coupons[i]
            
            estado = random.choice(['usado', 'no usado'])
            
            fecha_uso = None
            if estado == 'usado':
                fecha_uso = str(fake.date_this_year(before_today=True, after_today=False)) + ' ' + str(fake.time())  
            
            cursor.execute("""
                INSERT INTO otorgadoD (id_u, idCp, estado, fecha_uso)
                VALUES (%s, %s, %s, %s)
            """, (id_u, idCp, estado, fecha_uso))
    conn.commit();

def populateQueja(passengers, drivers):
    max = len(passengers) + len(drivers)
    for _ in range(max):
        id_uDte = random.choice(passengers)        
        id_uDdo = random.choice(drivers)
        
        motivo = random.choice(['Mal comportamiento', 'Incumplimiento de normas', 'Falta de comunicación'])
        
        fecha = fake.date_this_year(before_today=True, after_today=False)
        
        cursor.execute("""
            INSERT INTO queja (id_uDte, id_uDdo, motivo, fecha)
            VALUES (%s, %s, %s, %s)
        """, (id_uDte, id_uDdo, motivo, fecha))
    
'''  
cursor.execute(
    "delete from calificacion; delete from pago; delete from viaje; delete from solicitud; delete from pasajero; delete from rutas; delete from vehiculos; delete from conductor; delete from otorgadoD;  delete from otorgadop; delete from cuponc; delete from cuponp; delete from penalizacion; delete from queja; delete from usuario;"
)
'''
users = populateUser(20)
[passengers, drivers] = populatePassengerDriver(users)
routes = populateRoutes(drivers)
travels = populateBooking(passengers, routes)
populateReview(travels)
populatePayment(travels)
populateVehicles(drivers)
couponsP = populateCouponsPassenger(len(passengers))
couponsD = populateCouponsDriver(len(drivers))
populatePenalizacion(users)
populateOtorgadoP(couponsP,passengers)
populateOtorgadoD(couponsD,drivers)
populateQueja(passengers,drivers)

# Cerrar la conexión
cursor.close()
conn.close()