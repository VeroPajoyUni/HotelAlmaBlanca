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

