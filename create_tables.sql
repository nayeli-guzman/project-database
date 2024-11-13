DROP SCHEMA _1k CASCADE;
CREATE SCHEMA _1k;
set search_path to _1k;

create table Usuario (
	id_u varchar(9) primary key,
	nombre varchar(50) not null,
	apellido varchar(50) not null,
	genero char(1) not null,
	celular varchar(9) not null,
	email varchar(50) not null,
	fecha_naci date not null,
	calificacion double precision not null,
	contrasenia varchar(50),
	check(genero in ('M', 'F'))
);


create table Pasajero(
	id_u varchar(9) primary key,
	foreign key (id_u) references Usuario(id_u)
);


create table Conductor(
	id_u varchar(9) primary key,
	licencia varchar(9) not null,
	num_viajes smallint not null default 0,
	foreign key (id_u) references Usuario(id_u)
);

create table Rutas(
	id_r varchar(10),
	id_u varchar(9),
	capacidad smallint not null,
	pto_partida varchar(50) not null,
	pto_llegada varchar(50) not null,
 	estado char(1) not null,
	primary key (id_r, id_u),
	foreign key (id_u) references Usuario(id_u),
	check(estado in ('A', 'D'))
);

create table Solicitud(
	id_sv varchar(10) primary key,
	Pid_u varchar(9),
	id_r varchar(10),
	Cid_u varchar(9),
	fecha_realizada timestamp not null,
	tiempo_atencion timestamp,
	estado varchar(20) not null,
	foreign key (Pid_u) references Pasajero(id_u),
	foreign key (id_r, Cid_u) references Rutas(id_r, id_u),
	check(estado in ('realizada', 'aceptado', 'cancelado', 'rechazado'))
);

create table Viaje(
 	id_v varchar(10),
 	id_sv varchar(10),
 	distancia double precision not null,
 	fecha  timestamp not null,
	duracion time,
	estado varchar (9) not null,
	destino varchar(50) not null,
	primary key (id_v, id_sv),
	foreign key (id_sv) references Solicitud(id_sv),
	check (estado in ('realizada', 'cancelada', 'enproceso')),
	unique(id_v)
);

create table Calificacion(
	-- id_cal varchar(10),
	id_v varchar(10),
	id_sv varchar(10),
	puntuacion smallint,
	comentario varchar (100),
	tipo varchar(1) not null,
	primary key (tipo, id_v, id_sv),
	foreign key (id_v) references Viaje(id_v),
	foreign key (id_sv) references Solicitud(id_sv),
	check (tipo in ('P', 'C')	),
	check (puntuacion in (0, 1, 2, 3, 4, 5))
);
