# Arquitectura del Sistema: Hotel Alma Blanca – Reservas de Hoteles

## Problema que resuelve

Este proyecto busca permitir a los clientes consultar las habitaciones disponibles en el hotel y realizar reservaciones de una forma intuitiva y sencilla.
El sistema ayuda a gestionar las reservas del hotel, incluyendo la disponibilidad de habitaciones, reservas, pagos y confirmaciones, evitando depender de procesos manuales.

## Objetivo
Permitir a los clientes consultar habitaciones disponibles y realizar reservas de forma intuitiva y sencilla, y dar el primer paso desde la idea del proyecto hacia una solución distribuida contenerizada con Docker.

## Integrantes y roles
| Integrante | Rol |
|---|---|
| Maira Yarlin García Rivera | Líder del proyecto |
| Andrés Casanova Rengifo | Encargado de presentación |
| Yisel Verónica Pajoy Maca | Encargada técnica |
| Danilo Alexander Collazos Alegría | Encargado de documentación |

## Arquitectura

Nuestro proyecto se basa en la arquitectura de **microservicios**. El **Cliente** accede a la aplicación mediante una vista **Home**, desde donde las solicitudes HTTP serán gestionadas por un **API Gateway**. Este se encargará de recibir y enrutar las peticiones hacia los diferentes microservicios del backend mediante comunicación **HTTP/REST utilizando JSON**.

La arquitectura contempla los microservicios de **Usuarios, Habitaciones, Reservas, Pagos y Notificaciones**, cada uno encargado de una funcionalidad específica del sistema. A su vez, cada microservicio cuenta con su **propia base de datos**, manteniendo el aislamiento de la información y evitando que otros servicios accedan directamente a ella.

### Implementación en este avance

En el estado actual, los servicios de Usuarios, Habitaciones y Reservas tienen una aplicación funcional y una base de datos PostgreSQL propia. El API Gateway, Pagos y Notificaciones todavía están declarados como marcadores en Docker Compose y no realizan sus funciones.

La vista Home se comunica directamente con Usuarios, Habitaciones y Reservas.

## Servicios del sistema

* **Servicio de Usuarios:** Gestiona el registro y la información de clientes, recepcionistas y administradores.
* **Servicio de Habitaciones:** Gestiona las habitaciones y su disponibilidad.
* **Servicio de Reservas:** Gestiona las reservas realizadas y consulta la disponibilidad de habitaciones y los datos del cliente.
* **Servicio de Pagos:** Procesa los pagos y verifica la información de la reserva antes de realizar el cobro.
* **Servicio de Notificaciones:** Se encarga del envío de notificaciones relacionadas con los procesos del sistema.

Los servicios pueden trabajar de forma independiente. Entre los procesos independientes se encuentran la autenticación, la disponibilidad de habitaciones y el envío de notificaciones.

### Avance de los servicios

En este avance:
* Usuarios permite consultar, registrar, actualizar y eliminar usuarios.
* Habitaciones permite consultar, registrar, actualizar y eliminar habitaciones.
* Reservas permite consultar, crear, actualizar y eliminar reservas, revisar la disponibilidad y consultar detalles de una reserva.
* Pagos, Notificaciones y el API Gateway siguen pendientes de implementación. Aunque el servicio de Usuarios guarda un rol para cada persona, el inicio de sesión y el control de permisos todavía no están implementados.

## Comunicación entre servicios

Los servicios se comunican entre sí cuando necesitan información para completar un proceso.

* **Reservas → Habitaciones:** Consulta la disponibilidad antes de confirmar una reserva.
* **Reservas → Usuarios:** Solicita los datos del cliente que está realizando la reserva.
* **Pagos → Reservas:** Solicita los datos de la reserva para verificar que exista y conocer el total que debe cobrarse.
* **Habitaciones, Usuarios y Reservas:** Responden a las solicitudes entregando la información correspondiente.

### Comunicación implementada

Los servicios que ya tienen aplicación se comunican mediante solicitudes HTTP y envían o reciben datos en formato JSON. Para crear una reserva, Reservas consulta a Usuarios y Habitaciones para comprobar que existan. También puede consultar la disponibilidad y reunir los datos del usuario y de la habitación para mostrar el detalle de una reserva.

La página Home consulta a Usuarios y Habitaciones, y envía las solicitudes relacionadas con las reservas. En este momento se comunica directamente con esos servicios, no por medio del API Gateway.

## Docker Compose
Para levantar la estructura del proyecto:
```
docker compose up --build
```
El comando construye las imágenes que tienen un Dockerfile y levanta los contenedores definidos en `docker-compose.yml`. La vista Home está disponible en `http://localhost:3000`. Los servicios de Usuarios, Habitaciones y Reservas son aplicaciones Python y se publican, respectivamente, en los puertos `5001`, `5003` y `5002`.

Las bases de datos PostgreSQL de Usuarios, Habitaciones y Reservas se publican en los puertos `5434`, `5435` y `5433`. Docker Compose las conecta con sus servicios y usa volúmenes para guardar sus datos: `usuarios_data`, `habitaciones_data` y `reservas_data`. Estos volúmenes ayudan a conservar los datos cuando los contenedores se detienen o se vuelven a crear. No se deben borrar los volúmenes si se quiere conservar esa información.

El API Gateway, Pagos y Notificaciones, junto con sus bases de datos, siguen siendo contenedores marcadores: muestran un mensaje y quedan activos, pero todavía no ejecutan la lógica real del sistema.

### Variables de entorno

Los servicios leen la configuración de sus bases de datos y las direcciones de otros servicios desde variables de entorno. El archivo `.env.example` muestra los nombres de las variables necesarias; `.env` contiene la configuración local.

## Estado actual
- **Diseñado:** Arquitectura de microservicios con los servicios de Usuarios, Habitaciones, Reservas, Pagos y Notificaciones, además de un API Gateway planeado.
- **Configurado:** `docker-compose.yml` define la página, los servicios, las bases de datos y los puertos. También establece las variables de entorno y la conexión de cada base de datos con su servicio.
- **Implementado:** Vista Home contenerizada; servicios funcionales de Usuarios, Habitaciones y Reservas; bases PostgreSQL independientes para esos tres servicios; comunicación HTTP con JSON; y volúmenes para conservar los datos de esas bases.
- **Pendiente:** Implementar el API Gateway y conectarlo con la página; desarrollar Pagos y Notificaciones con bases de datos reales; agregar inicio de sesión y control de permisos; y completar pruebas, validaciones y copias de seguridad.

### Segundo avance

En este avance se pasó del diseño inicial a una primera versión funcional de Usuarios, Habitaciones y Reservas. Los servicios guardan información en sus propias bases de datos PostgreSQL, se comunican entre sí por HTTP y JSON cuando necesitan datos, y Docker Compose permite levantarlos junto con la vista Home. Los volúmenes aplican lo visto en clase sobre guardar la información de forma persistente, en lugar de dejarla solo en la memoria del programa.

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

### Bases de datos y volúmenes implementados

En este avance, Usuarios, Habitaciones y Reservas usan bases PostgreSQL independientes. Al iniciar, cada servicio prepara sus tablas si todavía no existen y carga algunos datos de ejemplo.

Docker Compose configura un volumen para cada una de esas bases: `usuarios_data`, `habitaciones_data` y `reservas_data`. El volumen conserva los archivos de la base de datos aunque se detenga o se vuelva a crear el contenedor. Los volúmenes no reemplazan las copias de seguridad.

Las bases de datos de Pagos y Notificaciones todavía son marcadores y no guardan información real.

## Usuarios del sistema

El sistema tendrá tres tipos principales de usuarios:

* **Usuario Cliente / Huésped:** Puede consultar habitaciones, buscar disponibilidad, realizar reservas, efectuar pagos y gestionar sus propias reservas.
* **Usuario Administrador:** Gestiona permisos y perfiles, además de administrar tarifas, habitaciones y reportes.
* **Usuario Recepcionista:** Consulta y administra reservas, gestiona reservas presenciales y realiza procesos de `check-in` y `check-out`.

Cada tipo de usuario tendrá permisos diferentes de acuerdo con sus responsabilidades dentro del sistema.

## Riesgos y fallas posibles

* **Falla del servicio de pagos:** El usuario podría ver su pago rechazado, lo que generaría frustración e incertidumbre. Para mitigarlo, se debe enviar una notificación clara explicando el problema e invitarlo a intentar el pago nuevamente.

* **Falla de la base de datos:** No sería posible consultar ni almacenar nueva información, lo que afectando el funcionamiento general de la plataforma. Como medida preventiva, es fundamental contar con copias de seguridad que permitan recuperar los datos y restablecer el servicio.

* **Falla del servidor principal:** La pagina web dejaria de estar disponible y los usuarios no podrán acceder a su contenido. Una posible solución es disponer de un servidor de respaldo que tome el control automáticamente o restaurar el servicio principal en el menor tiempo posible.
