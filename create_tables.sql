DROP SCHEMA _100k CASCADE;
CREATE SCHEMA _100k;
set search_path to _100k;

create table Usuario (
	id_u varchar(9) primary key,
	nombre varchar(50) not null,
	apellido varchar(50) not null,
	genero char(1) not null,
	celular varchar(9) not null,
	email varchar(50) not null,
	fecha_naci date not null,
	puntaje_acumulado double precision not null,
	cant_calificaciones smallint not null,
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

create table Pago(
	id_p varchar(10) primary key,
	id_v varchar(10),
	id_sv varchar(10),
	monto double precision not null,
	metodo varchar(10) not null,
	foreign key (id_v) references Viaje(id_v),
	foreign key (id_sv) references Solicitud(id_sv),
	check( metodo in('yape', 'plin', 'efectivo'))
);

create table Vehiculos(
	placa varchar(10) primary key,
	id_u varchar(9),
	modelo varchar(10),
	capacidad smallint not null,
	SOAT varchar(5) not null,
	imagen_path varchar(50) not null,
	fecha_registro date not null,
	estado char(1) not null default 'N',
	foreign key (id_u) references Usuario(id_u),
	check(estado in ('U', 'N'))
);

create table CuponP(
	idCp varchar(10) primary key,
	descuento smallint not null,
	fechaCaducidad date not null
);

create table CuponC (
	idCp varchar(10) primary key,
	descuento smallint not null,
	fechaCaducidad date not null,
	descripcion varchar(50) not null
);
 
create table penalizacion (
	idPn varchar(10) primary key,
	id_u varchar(9) not null,
	motivo varchar(50) not null,
	fechaInicio date not null,
	fechaFin date not null,
foreign key(id_u) references usuario(id_u)
);

create table otorgadoP(
	id_u varchar(9) not null,
	idCp varchar(10) not null,
	estado varchar(10) not null,
	fecha_uso timestamp,
primary key(idCp, id_u),
foreign key(id_u) references usuario(id_u),
foreign key(idCp) references cuponP(idCp)
);

create table otorgadoD (
	id_u varchar(9) not null,
	idCp varchar(10) not null,
	estado varchar(10) not null,
	fecha_uso timestamp,
	primary key(idCp, id_u),
	foreign key(id_u) references usuario(id_u),
foreign key(idCp) references cuponC(idCp));

create table queja(
	id_uDte varchar(9) not null,
	id_uDdo varchar(9) not null,
	motivo varchar(50) not null,
	fecha date not null,
	primary key(id_uDte, id_uDdo, fecha),
	foreign key(id_uDte) references usuario(id_u),
	foreign key(id_uDdo) references usuario(id_u)
);

-- constraints

alter table queja
add constraint queja_idudte_fk
foreign key(id_uDte)
references usuario(id_u);

alter table queja
add constraint queja_iduddo_fk
foreign key(id_uDdo)
references usuario(id_u);

ALTER TABLE cuponC
ADD CONSTRAINT cuponc_check_descuento
CHECK (descuento >= 0 AND descuento < 100);

ALTER TABLE otorgadoP
ADD CONSTRAINT otorgadop_check_estado
CHECK (estado IN ('usado', 'no usado'));

ALTER TABLE otorgadoD
ADD CONSTRAINT otorgadoc_check_estado
CHECK (estado IN ('usado', 'no usado'));

create or replace function recal_calificacion()
returns trigger as $$
begin
	if new.tipo = 'P' then
		update Usuario
		set 
puntaje_acumulado = puntaje_acumulado + new.puntuacion,
cant_calificaciones = cant_calificaciones + 1
		where id_u = (
select Cid_u 
from Solicitud
where id_sv = new.id_sv
);
	elsif new.tipo = 'D' then
		update Usuario
		set 
puntaje_acumulado = puntaje_acumulado + new.puntuacion,
cant_calificaciones = cant_calificaciones + 1
			where id_u =  (
select Pid_u 
from Solicitud
where id_sv = new.id_sv
);
	end if;
return new;
end;
$$ language plpgsql;


create or replace trigger trg_recal_calificacion
after insert on calificacion
for each row
execute function recal_calificacion();

