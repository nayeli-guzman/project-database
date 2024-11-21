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

amount = 100

conn.autocommit = True
cursor = conn.cursor()

# Establecer el esquema
cursor.execute('SET search_path TO _100k')

# Funciones para poblar las tablas
def populateUser(num_records):
    usuarios = []
    passengers = []
    drivers = []
    while True:
        j = True   # Seguirá siendo True hasta que el usuario sea pasajero
        id_u = fake.unique.bothify(text='U????????')
        nombre = fake.first_name()[:50]
        apellido = fake.last_name()[:50]
        genero = random.choice(['M', 'F'])
        celular = fake.phone_number()[:9]  # Tomar solo los primeros 9 dígitos
        email = fake.email()[:50]
        fecha_naci = fake.date_of_birth(minimum_age=18, maximum_age=80)
        contrasenia = fake.password(length=10)
        cursor.execute("""
            INSERT INTO Usuario (id_u, nombre, apellido, genero, celular, email, fecha_naci, puntaje_acumulado, cant_calificaciones , contrasenia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (id_u, nombre, apellido, genero, celular, email, fecha_naci, 0.0, 0, contrasenia))
        
        usuarios.append(id_u) 

        # Asignar como pasajero solo si no se completó la cantidad de pasajeros = num_records
        if (len(passengers)<num_records):
            cursor.execute("""
                INSERT INTO Pasajero (id_u)
                VALUES (%s)
            """, (id_u,))
            passengers.append(id_u)

        # Asignar como Conductor solo si no se completó la cantidad de conductores = num_records
        if (random.choice([True, True, False]) and (num_records > len(drivers))):
            licencia = fake.unique.bothify(text='???-#####')  
            cursor.execute("""
                INSERT INTO Conductor (id_u, licencia, num_viajes)
                VALUES (%s, %s, %s)
            """, (id_u, licencia, 0))
            drivers.append(id_u)

        if (num_records <= len(drivers) and num_records <= len(passengers)):
            break
    return usuarios, passengers, drivers

def populateRoutes(drivers):

    routes = []
    
    for i in range(amount):
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
    count = 0
    travels = []
        
    for i in range(amount):
        
        Pid_u = random.choice(passengers)
        
        id_r, Cid_u = random.choice(routes)
        if Pid_u != Cid_u:
            for j in range(random.randrange(start=0, step=1,stop=10)):

                id_sv = fake.unique.bothify(text='S?????????')
                fecha_realizada = fake.date_this_month(before_today=True, after_today=False)
                hora = fake.time()
                fecha_realizada = datetime.combine(fecha_realizada, datetime.strptime(hora, "%H:%M:%S").time())
                
                #tiempo_atencion = None if random.choice([True, False]) else fecha_realizada + timedelta(hours=random.randint(1, 48))
                tiempo_atencion = fecha_realizada + timedelta(hours=random.randint(1, 48))
            
                estado = 'aceptado'
                
                #if (tiempo_atencion is not None):
                #    estado = random.choice(['aceptado', 'aceptado', 'aceptado', 'aceptado', 'cancelado', 'rechazado'])

                cursor.execute("""
                    INSERT INTO Solicitud (id_sv, Pid_u, id_r, Cid_u, fecha_realizada, tiempo_atencion, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (id_sv, Pid_u, id_r, Cid_u, fecha_realizada, tiempo_atencion, estado))

                if(estado=='aceptado'):
                    travels.append(populateTravel(id_sv, tiempo_atencion, Pid_u))
                
                count+= 1
            if count >= amount:
                    break
    return travels

def populateTravel(id_sv, tiempo_atencion, Pid_u):

    id_v = fake.unique.bothify(text='T#######')
    distancia = round(random.uniform(5.0, 500.0), 2)  
    fecha = tiempo_atencion + timedelta(minutes=random.randint(10, 48*60))
    
    duracion = (fecha + timedelta(minutes=random.randint(10, 300))).time()
    estado = random.choice(['realizada', 'cancelada', 'enproceso'])    
    destino = fake.bothify("(#####.##)")
    
    cursor.execute(
        """
        INSERT INTO Viaje (id_v, id_sv, distancia, fecha, duracion, estado, destino)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (id_v, id_sv, distancia, fecha, duracion, estado, destino)
    )
    
    return (Pid_u, id_v, id_sv, fecha)

def populateReview(travels):

    c=0

    for i in range(len(travels)):

        Pid_u,id_v, id_sv,fecha = travels[i]
           
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
        c=c+1
        conf = random.choice([0,1])
        if ( c==amount ):
            break
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
            c=c+1

def populatePayment(travels):
    for i in range(len(travels)):
        Pid_u,id_v, id_sv,fecha = travels[i]
        
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
        
        placa = fake.unique.license_plate()[:10]  
        modelo = fake.word()[:10]  
        capacidad = random.randint(1, 7) 
        soat = str(random.randint(10000, 99999)) 
        imagen_path = f"images/{fake.word()}.jpg" 
        fecha_registro = fake.date_this_decade()  
        estado = 'N' # ['U', 'N']
        
        cursor.execute("""
            INSERT INTO Vehiculos (placa, id_u, modelo, capacidad, SOAT, imagen_path, fecha_registro, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (placa, id_u, modelo, capacidad, soat, imagen_path, fecha_registro, estado))

def populateCouponsPassenger(passengers) :
    cp = []
    for i in range (amount):
        idCp = fake.unique.bothify("CP########") 
        descuento = random.randint(5, 50)
        fecha_caducidad = fake.date_between(start_date=datetime.today(), end_date="+30d")
    
        cursor.execute("""
            INSERT INTO CuponP (idCp, descuento, fechaCaducidad)
            VALUES (%s, %s, %s)
        """, (idCp, descuento, fecha_caducidad))
        cp.append((idCp, fecha_caducidad))
    conn.commit()
    return cp

def populateCouponsDriver(drivers) :
    cd = []
    for i in range (amount):
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
    for _ in range(amount):
        idPn = fake.unique.bothify("PE########")        
        id_u = random.choice(users)
            
        motivo = fake.sentence(nb_words=6)[:50]
        fecha_inicio = fake.date_between(start_date="-1y", end_date="today")  
        fecha_fin = fecha_inicio + timedelta(days=random.randint(1, 30)) 
        
        cursor.execute("""
            INSERT INTO penalizacion (idPn, id_u, motivo, fechaInicio, fechaFin)
            VALUES (%s, %s, %s, %s, %s)
        """, (idPn, id_u, motivo, fecha_inicio, fecha_fin))

def populateOtorgadoP(coupons, passengers, travels):
    cupones_otorgados = set()  # Para evitar otorgar el mismo cupón a un usuario más de una vez
    viajes_usados = set()  # Para evitar que un cupón se use más de una vez en el mismo viaje
    count = 0
    for coupon in coupons:
        # Recupera el idCp y la fecha de caducidad del cupón
        idCp, fecha_caducidad = coupon
        # Decide si el cupón será otorgado a algún usuario
        if (random.choice([False, False, True])):

            # Otorga una cantidad aleatoria de cupones a los pasajeros
            for passenger in random.sample(passengers,random.randrange(start=1,step=1, stop=int(len(passengers)/2))):
                
                    # Decide si el cupón será "usado" o "no usado"
                    estado = random.choice(['usado', 'no usado'])

                    # Si el cupón es "usado", asignamos la fecha de un viaje específico del usuario, 
                    if estado == 'usado':
                        # Definir contador para saber si ya todos los viajes tienen un cupón asignado
                        i = 0
                        j = False
                        # Recorrer todos los viajes del pasajero para poder asignarle a alguno un cupón 
                        for travel in travels:
                            i = i + 1   # Incrementar los viajes
                            id_u, id_v, id_sv, fecha_viaje  = travel
                            # Verificar si en el viaje no se usó un cupón y si el viaje le pertenece al pasajero
                            if (passenger == id_u) and (id_v not in viajes_usados):
                                # Verificar la fecha de caduciada del cupón
                                if fecha_caducidad > fecha_viaje.date():
                                    fecha_uso = fecha_viaje  # La fecha de uso es la del viaje
                                    viajes_usados.add(id_v)  # Marca el viaje como usado para este cupón
                                    j = True
                        
                        # En caso ya se hayan usado cupones en todos sus viajes se pasa su estado a no usado
                        if i == len(travels) and j == False:
                            estado = 'no usado'
                            fecha_uso = None
                    else:
                        fecha_uso = None  # Si el cupón no es "usado", la fecha_uso es None

                    # Inserta el cupón en la base de datos (simulado con una instrucción de cursor)
                    cursor.execute("""
                        INSERT INTO otorgadoP (id_u, idCp, estado, fecha_uso)
                        VALUES (%s, %s, %s, %s)
                    """, (passenger, idCp, estado, fecha_uso))
                    count += 1
                    if (count == amount):
                        break

    conn.commit()
    
def populateOtorgadoD(coupons, users):
    for i in range(amount):
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
    conn.commit()

def populateQueja(passengers, drivers):
    max =int ( (len(passengers) + len(drivers)))
    for _ in range(amount):
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
    "delete from calificacion; delete from pago; delete from viaje; delete from solicitud; delete from pasajero; delete from rutas; delete from vehiculos; delete from conductor; delete from otorgadoc;  delete from otorgadop; delete from cuponc; delete from cuponp; delete from penalizacion; delete from queja; delete from usuario;"
)
'''

users, passengers, drivers = populateUser(amount)
# [passengers, drivers] = populatePassengerDriver(users)
routes = populateRoutes(drivers)
travels = populateBooking(passengers, routes)
populateReview(travels)
populatePayment(travels)
populateVehicles(drivers)
couponsP = populateCouponsPassenger(len(passengers))
couponsD = populateCouponsDriver(len(drivers))
populatePenalizacion(users)
populateOtorgadoP(couponsP,passengers, travels)
populateOtorgadoD(couponsD,drivers)
populateQueja(passengers,drivers)

# Cerrar la conexión
cursor.close()
conn.close()