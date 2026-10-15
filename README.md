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

## Docker Compose
Para levantar la estructura inicial del proyecto:
```
docker compose up --build
```
Esto construye la imagen de `home` a partir de su Dockerfile y publica la vista en `http://localhost:3000`. El servicio `reservas` se ejecuta con Flask y PostgreSQL; `usuarios`, `habitaciones`, `pagos` y `notificaciones`, además del API Gateway, siguen siendo marcadores de posición.

`reservas-db` inicializa PostgreSQL en su puerto estándar `5432` dentro de Docker y conserva sus datos en el volumen `reservas_data`. Desde el equipo anfitrión se publica en el puerto `5433`, configurado directamente en `docker-compose.yml`. La configuración está en `.env`; usa `.env.example` como plantilla y cambia la contraseña antes de desplegar. `.env` está excluido de Git. Para evitar conflictos, se reservaron los puertos externos `5434` para Usuarios, `5435` para Habitaciones, `5436` para Pagos y `5437` para Notificaciones/Redis, configurados directamente en Compose cuando esos servicios se activen. Dentro de Docker, PostgreSQL usará `5432` en cada servicio y Redis `6379`.

### API de Reservas

El servicio administra las reservas y sus fechas; los datos del huésped y de la habitación pertenecen a sus respectivos microservicios. Queda disponible en `http://localhost:5002` y recibe y responde JSON.

| Método y endpoint | Entrada | Respuesta |
|---|---|---|
| `GET /reservas` | Ninguna | Lista de reservas. |
| `GET /reservas/<id>` | ID en la ruta | Datos de la reserva o `404` si no existe. |
| `GET /reservas/<id>/detalles` | ID en la ruta | Datos de la reserva junto con los datos del usuario y la habitación consultados a sus servicios. |
| `GET /reservas/disponibilidad?habitacion_id=<id>&fecha_entrada=AAAA-MM-DD&fecha_salida=AAAA-MM-DD` | ID de habitación y fechas | `{"disponible": true/false}` según las reservas almacenadas. |
| `POST /reservas` | JSON con los campos indicados abajo | `201` y el ID creado; `404` si no existe el usuario o la habitación; `409` si la habitación ya está reservada en ese intervalo. |
| `PUT /reservas/<id>` | ID en la ruta y JSON completo con los campos indicados abajo | Confirmación de actualización; `404` si no existe el usuario o la habitación; `409` si la habitación ya está reservada en ese intervalo. |
| `DELETE /reservas/<id>` | ID en la ruta | Elimina la reserva de la base de datos. |

El JSON requerido por `POST` y `PUT` tiene esta forma:

```json
{
  "usuario_id": 1,
  "habitacion_id": 101,
  "fecha_entrada": "2026-12-20",
  "fecha_salida": "2026-12-23",
  "huespedes": 2
}
```

La tabla `reservas` almacena `id`, `usuario_id`, `habitacion_id`, `fecha_entrada`, `fecha_salida`, `huespedes` y `estado`. Al iniciar el servicio se agrega una reserva de ejemplo (`usuario_id=1`, `habitacion_id=1`, fechas `2026-12-20` a `2026-12-23`, 2 huéspedes) si ese registro aún no existe. `DELETE` elimina físicamente el registro; los ID de usuario y habitación son referencias a otros servicios, no claves foráneas entre bases de datos. El endpoint consulta las reservas existentes antes de crear o actualizar otra para la misma habitación, pero las fechas no tienen una validación adicional en el código ni una restricción avanzada de solapamiento en PostgreSQL. Si la base ya existía, al iniciar también se quitan las restricciones anteriores de fechas y solapamientos.

Siguiendo el ejemplo de clase, `POST` y `PUT` reciben el JSON directamente y no revisan previamente que tenga todos los campos o que cada valor tenga el formato esperado. Envía el objeto JSON mostrado arriba.

### Variables de entorno de Reservas

El contenedor de Reservas obtiene estas variables de `.env`:

| Variable | Uso |
|---|---|
| `RESERVAS_DB_HOST` | Nombre del contenedor de PostgreSQL (`reservas-db`). |
| `RESERVAS_DB_PORT` | Puerto PostgreSQL de Reservas dentro de Compose (`5432`). |
| `RESERVAS_DB_USER` | Usuario de la base de datos de Reservas. |
| `RESERVAS_DB_PASSWORD` | Contraseña de ese usuario. |
| `RESERVAS_DB_NAME` | Nombre de la base de datos (`reservas`). |
| `HABITACIONES_URL` | URL interna del servicio Habitaciones (`http://habitaciones:5000`). |
| `USUARIOS_URL` | URL interna del servicio Usuarios (`http://usuarios:5000`). |

### Comunicación con otros servicios

Reservas consulta por HTTP los endpoints `GET /habitaciones/<id>` y `GET /usuarios/<id>` al mostrar detalles y antes de crear o actualizar una reserva. Si el servicio correspondiente responde `404`, Reservas devuelve `404`; si responde con otro código distinto de `200`, devuelve `503`. Las solicitudes tienen un tiempo máximo de espera de cinco segundos.

Habitaciones todavía no ofrece un endpoint de disponibilidad por fechas. Por eso, Reservas valida los solapamientos consultando las reservas almacenadas en su propia base de datos y consulta a Habitaciones para confirmar que la habitación exista. La consulta local de disponibilidad no protege contra solicitudes concurrentes.

| Solicitante | Servicio que responde | Endpoint previsto | Información enviada | Información requerida |
|---|---|---|---|---|
| Reservas | Habitaciones | `GET /habitaciones/<habitacion_id>` | ID de habitación. | Confirma que la habitación exista y obtiene sus datos. |
| Reservas | Usuarios | `GET /usuarios/<usuario_id>` | ID de usuario. | Confirma que el usuario exista y obtiene sus datos. |
| Pagos (futuro consumidor) | Reservas | `GET /reservas/<id>` | ID de reserva. | Datos actuales de la reserva; hoy no incluyen el valor total. |

Para integrar Pagos aún debe definirse de dónde sale el precio total y cómo se expondrá.

### Ejecución y verificación

Desde la raíz del repositorio, ejecutar `docker compose up --build`. La página Home queda en `http://localhost:3000` y la API de Reservas en `http://localhost:5002`. Compose inicia `reservas-db` y monta `reservas_data` para persistir la información. Los demás servicios siguen siendo marcadores de posición.

Se puede probar `GET http://localhost:5002/reservas` para listar reservas y enviar el JSON anterior con `POST http://localhost:5002/reservas` para crear una. También se puede comprobar `GET /reservas/disponibilidad` usando los parámetros indicados en la tabla.

## Estado actual
- **Diseñado:** Arquitectura completa de microservicios (5 servicios y API Gateway), roles de usuario, comunicación entre servicios.
- **Configurado:** `docker-compose.yml` con los servicios de la arquitectura declarados; PostgreSQL real y volumen están habilitados para Reservas.
- **Implementado:** Vista Home contenerizada y funcionando (`Dockerfile` e `index.html`).
- **Implementado:** Servicio de Reservas con persistencia PostgreSQL, API REST básica y control de solapamientos.
- **Pendiente:** Integraciones HTTP de Reservas con Usuarios y Habitaciones, servicios restantes, API Gateway, autenticación, pagos y notificaciones reales.

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

## Riesgos y fallas posibles

* **Falla del servicio de pagos:** El usuario podría ver su pago rechazado, lo que generaría frustración e incertidumbre. Para mitigarlo, se debe enviar una notificación clara explicando el problema e invitarlo a intentar el pago nuevamente.

* **Falla de la base de datos:** No sería posible consultar ni almacenar nueva información, lo que afectando el funcionamiento general de la plataforma. Como medida preventiva, es fundamental contar con copias de seguridad que permitan recuperar los datos y restablecer el servicio.

* **Falla del servidor principal:** La pagina web dejaria de estar disponible y los usuarios no podrán acceder a su contenido. Una posible solución es disponer de un servidor de respaldo que tome el control automáticamente o restaurar el servicio principal en el menor tiempo posible.
