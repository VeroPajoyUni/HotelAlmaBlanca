# Arquitectura del Sistema: Hotel Alma Blanca – Reservas de Hoteles

## Problema que resuelve

Este proyecto busca permitir a los clientes consultar las habitaciones disponibles en el hotel y realizar reservaciones de una forma intuitiva y sencilla.
El sistema ayuda a gestionar las reservas del hotel, incluyendo la disponibilidad de habitaciones, reservas, pagos y confirmaciones, evitando depender de procesos manuales.

## Servicios del sistema

* **Servicio de Usuarios:** Gestiona el registro y la información de clientes, recepcionistas y administradores.
* **Servicio de Habitaciones:** Gestiona las habitaciones y su disponibilidad.
* **Servicio de Reservas:** Gestiona las reservas realizadas y consulta la disponibilidad de habitaciones y los datos del cliente.
* **Servicio de Pagos:** Procesa los pagos y verifica la información de la reserva antes de realizar el cobro.
* **Servicio de Notificaciones:** Se encarga del envío de notificaciones relacionadas con los procesos del sistema.

Los servicios pueden trabajar de forma independiente. Entre los procesos independientes se encuentran la autenticación, la disponibilidad de habitaciones y el envío de notificaciones.

## Comunicación entre servicios

Los servicios se comunican entre sí cuando necesitan información para completar un proceso.

* **Reservas → Habitaciones:** Consulta la disponibilidad antes de confirmar una reserva.
* **Reservas → Usuarios:** Solicita los datos del cliente que está realizando la reserva.
* **Pagos → Reservas:** Solicita los datos de la reserva para verificar que exista y conocer el total que debe cobrarse.
* **Habitaciones, Usuarios y Reservas:** Responden a las solicitudes entregando la información correspondiente.

## Tipo de arquitectura

**Arquitectura de Microservicios**

Se eligió una arquitectura basada en microservicios porque permite dividir el sistema del Hotel Alma Blanca en servicios independientes.

Cada servicio puede manejar diferentes cargas y crecer de acuerdo con su propia demanda. Además, permite actualizar o ampliar los servicios de manera independiente conforme aumente el tamaño del hotel.

El sistema inicialmente es pequeño, pero está diseñado pensando en un crecimiento a largo plazo. Se espera un flujo moderado de clientes, con posibilidad de incremento durante temporadas altas, especialmente en los servicios de reservas y pagos.

## Base de datos

Cada servicio tendrá **su propia base de datos**, siguiendo el principio de independencia de los microservicios.

La información que debe almacenarse incluye:

* Datos de los usuarios: clientes, recepcionistas y administradores.
* Información de las habitaciones.
* Disponibilidad de las habitaciones.
* Reservas realizadas.
* Pagos procesados.
* Historial de transacciones.

Los datos más críticos son los relacionados con **reservas y pagos**, ya que permiten conocer qué habitaciones están ocupadas y cuáles han sido pagadas.

La pérdida de esta información podría generar problemas como pérdida de reservas, errores en el registro de habitaciones ocupadas o cobradas, sobreventa y reclamos por parte de los clientes.

## Usuarios del sistema

El sistema tendrá tres tipos principales de usuarios:

* **Usuario Cliente / Huésped:** Puede consultar habitaciones, buscar disponibilidad, realizar reservas, efectuar pagos y gestionar sus propias reservas.
* **Usuario Administrador:** Gestiona permisos y perfiles, además de administrar tarifas, habitaciones y reportes.
* **Usuario Recepcionista:** Consulta y administra reservas, gestiona reservas presenciales y realiza procesos de `check-in` y `check-out`.

Cada tipo de usuario tendrá permisos diferentes de acuerdo con sus responsabilidades dentro del sistema.

