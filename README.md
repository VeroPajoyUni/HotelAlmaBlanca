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
| Andrés Casanova Rengifo | Encargado de frontend |
| Yisel Verónica Pajoy Maca | Encargada técnica |
| Danilo Alexander Collazos Alegría | Encargado de documentación |

## Arquitectura

Nuestro proyecto se basa en la arquitectura de **microservicios**. El **Cliente** accede a la aplicación mediante una vista **Home**, desde donde las solicitudes HTTP serán gestionadas por un **API Gateway**. Este se encargará de recibir y enrutar las peticiones hacia los diferentes microservicios del backend mediante comunicación **HTTP/REST utilizando JSON**.

La arquitectura contempla los microservicios de **Usuarios, Habitaciones, Reservas, Pagos y Notificaciones**, cada uno encargado de una funcionalidad específica del sistema. A su vez, cada microservicio cuenta con su **propia base de datos**, manteniendo el aislamiento de la información y evitando que otros servicios accedan directamente a ella.

### Implementación en este avance

En el estado actual, los servicios de Usuarios, Habitaciones, Reservas y Pagos tienen una aplicación funcional y una base de datos PostgreSQL propia. El API Gateway y Notificaciones todavía están declarados como marcadores en Docker Compose y no realizan sus funciones.

La vista Home se comunica directamente con Usuarios, Habitaciones y Reservas.

## Servicios del sistema

* **Servicio de Usuarios:** Gestiona el registro y la información de clientes, recepcionistas y administradores.
* **Servicio de Habitaciones:** Gestiona las habitaciones y su disponibilidad.
* **Servicio de Reservas:** Gestiona las reservas realizadas y consulta la disponibilidad de habitaciones y los datos del cliente.
* **Servicio de Pagos:** Consulta los detalles de una reserva, calcula el monto según las noches y el precio por noche, y registra el pago con estado inicial `pendiente`. La integración con una pasarela para realizar o confirmar el cobro aún no está implementada.
* **Servicio de Notificaciones:** Se encarga del envío de notificaciones relacionadas con los procesos del sistema.

Los servicios trabajan de forma independiente.

### Avance de los servicios

En este avance:
* Usuarios permite consultar, registrar, actualizar y eliminar usuarios.
* Habitaciones permite consultar, registrar, actualizar y eliminar habitaciones.
* Reservas permite consultar, crear, actualizar y eliminar reservas, revisar la disponibilidad y consultar detalles de una reserva.
* Pagos permite listar y consultar pagos, además de registrar un pago pendiente después de consultar Reservas y calcular el monto.
* Notificaciones y el API Gateway siguen pendientes de implementación. Aunque el servicio de Usuarios guarda un rol para cada persona, el inicio de sesión y el control de permisos todavía no están implementados.

## Endpoints de la API

Las rutas siguientes corresponden a los servicios Flask implementados. Los endpoints reciben o devuelven JSON cuando aplica. `{id}` representa el identificador numérico del recurso.

### Usuarios

Base URL local: `http://localhost:5001`

| Método | Endpoint | Descripción | Entrada principal |
|---|---|---|---|
| `GET` | `/usuarios` | Lista los usuarios. | Ninguna. |
| `GET` | `/usuarios/{id}` | Consulta un usuario por ID. | ID en la URL. |
| `POST` | `/usuarios` | Registra un usuario con rol cliente por defecto. | JSON con `nombre`, `apellido`, `documento`, `email` y `telefono`. |
| `PUT` | `/usuarios/{id}` | Actualiza todos los datos del usuario. | JSON con los campos requeridos del usuario. |
| `PATCH` | `/usuarios/{id}` | Actualiza parcialmente los datos enviados. | JSON con uno o más campos del usuario. |
| `DELETE` | `/usuarios/{id}` | Elimina un usuario. | ID en la URL. |
| `GET` | `/usuarios/{id}/reservas` | Consulta un usuario y solicita sus reservas al servicio Reservas. | ID del usuario en la URL. |
| `GET` | `/usuarios/circuito` | Consulta el estado del circuit breaker hacia Reservas. | Ninguna. |

Ejemplo del cuerpo para `POST /usuarios`:

```json
{
  "nombre": "Marcos",
  "apellido": "Rodriguez",
  "documento": "1001001005",
  "email": "marcos@example.com",
  "telefono": "3097647698"
}
```

### Habitaciones

Base URL local: `http://localhost:5003`

| Método | Endpoint | Descripción | Entrada principal |
|---|---|---|---|
| `GET` | `/health` | Comprueba que el servicio responda. | Ninguna. |
| `GET` | `/habitaciones` | Lista las habitaciones. | Ninguna. |
| `GET` | `/habitaciones/{id}` | Consulta una habitación por ID. | ID en la URL. |
| `POST` | `/habitaciones` | Crea una habitación. | JSON con `numero`, `tipo`, `capacidad`, `precio_noche`, `estado` y, opcionalmente, `descripcion`. |
| `PUT` | `/habitaciones/{id}` | Actualiza los datos de una habitación. | JSON con `numero`, `tipo`, `capacidad`, `precio_noche`, `estado` y, opcionalmente, `descripcion`. |
| `DELETE` | `/habitaciones/{id}` | Elimina una habitación. | ID en la URL. |

Ejemplo del cuerpo para `POST /habitaciones`:

```json
{
  "numero": "401",
  "tipo": "doble",
  "capacidad": 2,
  "precio_noche": 150000,
  "estado": "disponible",
  "descripcion": "Habitación con baño privado"
}
```

### Reservas

Base URL local: `http://localhost:5002`

| Método | Endpoint | Descripción | Entrada principal |
|---|---|---|---|
| `GET` | `/reservas` | Lista las reservas. | Ninguna. |
| `GET` | `/reservas/{id}` | Consulta una reserva por ID. | ID en la URL. |
| `GET` | `/reservas/{id}/detalles` | Consulta la reserva junto con los datos del usuario y la habitación obtenidos de sus servicios. | ID en la URL. |
| `GET` | `/reservas/disponibilidad` | Comprueba disponibilidad para un intervalo. | Query params: `habitacion_id`, `fecha_entrada`, `fecha_salida`. |
| `POST` | `/reservas` | Valida usuario, habitación y disponibilidad antes de crear una reserva. | JSON con `usuario_id`, `habitacion_id`, `fecha_entrada`, `fecha_salida` y `huespedes`. |
| `PUT` | `/reservas/{id}` | Valida referencias y disponibilidad antes de actualizar la reserva. | JSON con los campos requeridos para crear una reserva. |
| `DELETE` | `/reservas/{id}` | Elimina una reserva. | ID en la URL. |
| `GET` | `/reservas/circuito` | Consulta los circuit breakers hacia Usuarios y Habitaciones. | Ninguna. |

Ejemplo del cuerpo para `POST /reservas`:

```json
{
  "usuario_id": 1,
  "habitacion_id": 1,
  "fecha_entrada": "2026-12-20",
  "fecha_salida": "2026-12-23",
  "huespedes": 2
}
```

La disponibilidad se consulta, por ejemplo, con `GET /reservas/disponibilidad?habitacion_id=1&fecha_entrada=2026-12-20&fecha_salida=2026-12-23`.

### Pagos

Base URL local: `http://localhost:5004`

| Método | Endpoint | Descripción | Entrada principal |
|---|---|---|---|
| `GET` | `/pagos` | Lista los pagos registrados. | Ninguna. |
| `GET` | `/pagos/{id}` | Consulta un pago por ID. | ID en la URL. |
| `POST` | `/pagos` | Consulta la reserva, calcula el total y registra un pago en estado `pendiente`. | JSON con `reserva_id` y `metodo_pago`. |
| `GET` | `/pagos/circuito` | Consulta el estado del circuit breaker hacia Reservas. | Ninguna. |

Ejemplo del cuerpo para `POST /pagos`:

```json
{
  "reserva_id": 1,
  "metodo_pago": "tarjeta"
}
```

El monto se calcula con las fechas de entrada y salida de la reserva y el precio por noche de la habitación. El endpoint no procesa el cobro con una entidad financiera ni permite cambiar el estado del pago; los registros quedan `pendiente`.

Notificaciones y API Gateway siguen siendo marcadores y no exponen endpoints de aplicación.

## Comunicación entre servicios

Los servicios se comunican entre sí cuando necesitan información para completar un proceso.

* **Reservas → Habitaciones:** Comprueba que la habitación exista y obtiene sus datos. La disponibilidad se valida consultando la base de datos de Reservas, no mediante una llamada de disponibilidad a Habitaciones.
* **Reservas → Usuarios:** Solicita los datos del cliente que está realizando la reserva.
* **Pagos → Reservas:** Consulta los detalles de la reserva para verificarla y calcular el monto que registra como pago pendiente.
* **Habitaciones, Usuarios, Reservas y Pagos:** Responden a las solicitudes entregando la información correspondiente.

### Comunicación implementada

Los servicios que ya tienen aplicación se comunican mediante solicitudes HTTP y envían o reciben datos en formato JSON. Estos son los endpoints que originan llamadas entre servicios:

| Servicio que inicia | Endpoint solicitado | Uso |
|---|---|---|
| Reservas | `GET /usuarios/{id}` | Comprueba que el usuario exista al crear o actualizar una reserva y obtiene sus datos al consultar detalles. |
| Reservas | `GET /habitaciones/{id}` | Comprueba que la habitación exista al crear o actualizar una reserva y obtiene sus datos al consultar detalles. |
| Usuarios | `GET /reservas?usuario_id={id}` | Consulta las reservas desde `GET /usuarios/{id}/reservas`. El endpoint de listado de Reservas actualmente no aplica el filtro `usuario_id`, por lo que responde el listado completo. |
| Pagos | `GET /reservas/{id}/detalles` | Verifica que la reserva exista y obtiene las fechas y el precio de la habitación para calcular el monto. |

Las llamadas de Reservas a Usuarios y Habitaciones se realizan al crear (`POST /reservas`), actualizar (`PUT /reservas/{id}`) o consultar los detalles (`GET /reservas/{id}/detalles`). Pagos consulta a Reservas mediante `GET /reservas/{id}/detalles` al recibir `POST /pagos`. El estado de los circuit breakers puede consultarse en `GET /reservas/circuito`, `GET /usuarios/circuito` y `GET /pagos/circuito`.

El endpoint de detalles de Reservas entrega los datos de la reserva, usuario y habitación. Pagos usa esos datos para calcular el monto a registrar. La página Home todavía no se comunica con Pagos; el flujo de pago no está conectado a la interfaz.

La página Home se comunica directamente con los servicios publicados en los puertos locales `5001` (Usuarios), `5002` (Reservas) y `5003` (Habitaciones), no por medio del API Gateway. Desde la interfaz se usan `GET /habitaciones`, `GET /usuarios`, `POST /usuarios`, `GET /reservas/disponibilidad`, `POST /reservas`, `GET /reservas` y `DELETE /reservas/{id}`.

## Cómo ejecutar el sistema

### Requisitos previos

* Docker instalado y en ejecución.
* Docker Compose disponible como `docker compose`.
* Puertos locales `3000`, `5001`, `5002`, `5003`, `5004`, `5433`, `5434`, `5435` y `5436` disponibles.

### Configuración y arranque

Desde la raíz del repositorio, donde se encuentra `docker-compose.yml`, verifica que exista `.env`. Si aún no existe, puedes crear la configuración local copiando el ejemplo:

```powershell
.env.example → .env
```

Revisa los valores de `.env` para tu entorno local. No publiques credenciales reales ni las incluyas en el repositorio.

Levanta los contenedores con:

```
docker compose up --build
```

El comando construye las imágenes de Home y de los servicios implementados y levanta los contenedores declarados. La página está disponible en `http://localhost:3000`.

### Puertos publicados

| Componente | Dirección local | Puerto del contenedor |
|---|---|---:|
| Home | `http://localhost:3000` | 80 |
| Usuarios | `http://localhost:5001` | 5000 |
| Reservas | `http://localhost:5002` | 5000 |
| Habitaciones | `http://localhost:5003` | 5000 |
| Pagos | `http://localhost:5004` | 5000 |
| Base de datos Reservas | `localhost:5433` | 5432 |
| Base de datos Usuarios | `localhost:5434` | 5432 |
| Base de datos Habitaciones | `localhost:5435` | 5432 |
| Base de datos Pagos | `localhost:5436` | 5432 |

Las bases operativas se conectan por los nombres de servicio dentro de la red de Compose y usan los volúmenes `reservas_data`, `usuarios_data`, `habitaciones_data` y `pagos_data` para conservar datos. `docker compose down` detiene y elimina los contenedores, pero conserva esos volúmenes. No uses `docker compose down -v` a menos que quieras borrar también los datos persistidos.

Para consultar los contenedores y sus logs:

```powershell
docker compose ps
docker compose logs -f usuarios reservas habitaciones pagos
```

Para detener el sistema:

```powershell
docker compose down
```

El API Gateway y Notificaciones, junto con la base Redis de Notificaciones, siguen siendo contenedores marcadores: muestran un mensaje y quedan activos, pero no ejecutan la lógica real del sistema. El servicio Pagos y su base PostgreSQL ya son funcionales.

### Variables de entorno

Los servicios implementados leen la configuración desde variables de entorno. `.env.example` documenta los nombres de las variables; `.env` contiene los valores de la instalación local y no debe usarse para publicar contraseñas.

| Grupo | Variables | Uso |
|---|---|---|
| Usuarios DB | `USUARIOS_DB_HOST`, `USUARIOS_DB_PORT`, `USUARIOS_DB_NAME`, `USUARIOS_DB_USER`, `USUARIOS_DB_PASSWORD` | Conexión del servicio Usuarios a PostgreSQL. |
| Habitaciones DB | `HABITACIONES_DB_HOST`, `HABITACIONES_DB_PORT`, `HABITACIONES_DB_NAME`, `HABITACIONES_DB_USER`, `HABITACIONES_DB_PASSWORD` | Conexión del servicio Habitaciones a PostgreSQL. |
| Reservas DB | `RESERVAS_DB_HOST`, `RESERVAS_DB_PORT`, `RESERVAS_DB_NAME`, `RESERVAS_DB_USER`, `RESERVAS_DB_PASSWORD` | Conexión del servicio Reservas a PostgreSQL. |
| Pagos DB | `PAGOS_DB_HOST`, `PAGOS_DB_PORT`, `PAGOS_DB_NAME`, `PAGOS_DB_USER`, `PAGOS_DB_PASSWORD` | Conexión del servicio Pagos a PostgreSQL. |
| Notificaciones DB (previsto) | `NOTIFICACIONES_DB_HOST`, `NOTIFICACIONES_DB_PORT` | Configuración prevista para Redis; el contenedor marcador no inicia Redis. |
| URLs entre servicios | `USUARIOS_URL`, `HABITACIONES_URL`, `RESERVAS_URL` | Direcciones internas usadas por las llamadas HTTP implementadas. |
| URLs planeadas | `PAGOS_URL`, `NOTIFICACIONES_URL` | Direcciones declaradas para esos servicios; Home todavía no consume Pagos y Notificaciones sigue pendiente. |
| Tiempo de espera | `USUARIOS_TIMEOUT`, `HABITACIONES_TIMEOUT`, `RESERVAS_TIMEOUT` | Límites de espera de las llamadas HTTP hacia cada servicio. |
| Circuit breaker | `CB_MAX_FALLOS`, `CB_RECUPERACION` | Umbral de fallos consecutivos y periodo de recuperación, en segundos. |

### Consultar las bases de datos

Las bases de datos PostgreSQL se pueden inspeccionar con el cliente `psql` incluido en sus contenedores. Por ejemplo, para Usuarios:

```powershell
docker compose exec usuarios-db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Ya dentro de `psql`, se pueden consultar las tablas y su estructura:

```sql
\dt
\d usuarios
SELECT * FROM usuarios;
```

Para las otras bases, cambia el contenedor y tabla:

| Base de datos | Contenedor | Tabla |
|---|---|---|
| Habitaciones | `habitaciones-db` | `habitaciones` |
| Reservas | `reservas-db` | `reservas` |
| Pagos | `pagos-db` | `pagos` |

Por ejemplo, `docker compose exec reservas-db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'`. La base de datos se inicializa y carga datos de ejemplo cuando inicia por primera vez el servicio correspondiente.

## Estado actual
- **Diseñado:** Arquitectura de microservicios con los servicios de Usuarios, Habitaciones, Reservas, Pagos y Notificaciones, además de un API Gateway planeado.
- **Configurado:** `docker-compose.yml` define la página, los servicios, las bases de datos y los puertos. También establece las variables de entorno y la conexión de cada base de datos con su servicio.
- **Implementado:** Vista Home contenerizada; servicios funcionales de Usuarios, Habitaciones, Reservas y Pagos; bases PostgreSQL independientes para esos cuatro servicios; comunicación HTTP con JSON, incluida la consulta de Pagos a Reservas; y volúmenes para conservar los datos.
- **Pendiente:** Implementar el API Gateway y conectarlo con la página; implementar Notificaciones; agregar inicio de sesión y control de permisos; y completar pruebas, validaciones y copias de seguridad.

### Tercer avance

En este avance se cuenta con versiones funcionales de Usuarios, Habitaciones, Reservas y Pagos. Los cuatro servicios guardan información en bases de datos PostgreSQL independientes; Pagos consulta los detalles de Reservas por HTTP/JSON para calcular el monto de un pago pendiente. Docker Compose permite levantarlos junto con la vista Home y los volúmenes conservan los datos de las bases.

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

### Metadata de las bases de datos

Los nombres, usuarios, hosts y puertos se parametrizan mediante variables de entorno; `.env.example` contiene los valores de referencia y `.env` la configuración local. No se documentan contraseñas aquí.

| Servicio | Motor e imagen declarada | Base de datos y usuario (valores de `.env`) | Host interno | Puerto interno | Puerto publicado en el host | Persistencia | Estado |
|---|---|---|---|---:|---:|---|---|
| Usuarios | PostgreSQL (`postgres:16-alpine`) | `USUARIOS_DB_NAME`: `usuarios`; `USUARIOS_DB_USER`: `usuario` | `usuarios-db` | 5432 | 5434 | Volumen `usuarios_data` | Operativa |
| Habitaciones | PostgreSQL (`postgres:16-alpine`) | `HABITACIONES_DB_NAME`: `habitaciones`; `HABITACIONES_DB_USER`: `usuario` | `habitaciones-db` | 5432 | 5435 | Volumen `habitaciones_data` | Operativa |
| Reservas | PostgreSQL (`postgres:16-alpine`) | `RESERVAS_DB_NAME`: `reservas`; `RESERVAS_DB_USER`: `usuario` | `reservas-db` | 5432 | 5433 | Volumen `reservas_data` | Operativa |
| Pagos | PostgreSQL (`postgres:16-alpine`) | `PAGOS_DB_NAME`: `pagos`; `PAGOS_DB_USER`: `usuario` | `pagos-db` | 5432 | 5436 | Volumen `pagos_data` | Operativa |
| Notificaciones | Redis (`redis:alpine`) | Redis no usa nombre de base PostgreSQL ni usuario; `.env.example` define el host y puerto, sin credenciales | `notificaciones-db` | 6379 previsto; Redis no llega a iniciar | No publicado | Sin volumen configurado | Marcador; no almacena datos |

Compose conecta las cuatro bases PostgreSQL operativas a sus servicios por los nombres internos `usuarios-db`, `habitaciones-db`, `reservas-db` y `pagos-db`. Sus volúmenes conservan los datos al detener o recrear contenedores, pero no reemplazan las copias de seguridad. Notificaciones todavía no tiene almacenamiento funcional. El API Gateway no tiene una base de datos declarada.

### Esquema de datos implementado

Cada uno de los servicios operativos crea su tabla principal al iniciar. Usuarios, Habitaciones y Reservas también cargan datos de ejemplo:

* **Usuarios — `usuarios`:** `id`, `nombre`, `apellido`, `documento`, `email`, `telefono`, `rol` y `fecha_registro`. Documento y correo son únicos; los roles admitidos son cliente, recepcionista y administrador.
* **Habitaciones — `habitaciones`:** `id`, `numero`, `tipo`, `capacidad`, `precio_noche`, `estado` y `descripcion`. El número es único y tipo, capacidad, precio y estado tienen restricciones.
* **Reservas — `reservas`:** `id`, `usuario_id`, `habitacion_id`, `fecha_entrada`, `fecha_salida`, `huespedes` y `estado`. Los identificadores de usuario y habitación se guardan como referencias lógicas; el esquema no declara claves foráneas entre bases de microservicios.
* **Pagos — `pagos`:** `id`, `reserva_id`, `monto`, `metodo_pago`, `estado` y `fecha_pago`. El monto debe ser positivo y los estados permitidos son `pendiente`, `pagado` y `rechazado`. `reserva_id` es una referencia lógica; no hay una clave foránea entre las bases. El servicio crea pagos como `pendiente`.
* **Notificaciones:** el modelo y almacenamiento todavía no están implementados; Compose declara Redis como base planeada.

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
