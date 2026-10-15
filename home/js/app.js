/* ==========================================================
   1. CONFIGURACIÓN: dirección de cada microservicio
   (puertos publicados en docker-compose.yml)
   ========================================================== */
const API_USUARIOS = "http://localhost:5001";
const API_RESERVAS = "http://localhost:5002";
const API_HABITACIONES = "http://localhost:5003";


/* ==========================================================
   2. ELEMENTOS DEL HTML Y DATOS EN MEMORIA
   ========================================================== */
const formBuscar = document.getElementById("form-buscar");
const selectHabitacion = document.getElementById("habitacion");
const selectUsuario = document.getElementById("usuario");
const mensajeBuscar = document.getElementById("mensaje-buscar");
const btnConfirmar = document.getElementById("btn-confirmar");
const listaHabitaciones = document.getElementById("lista-habitaciones");
const listaReservas = document.getElementById("lista-reservas");
const mensajeReservas = document.getElementById("mensaje-reservas");
const formRegistro = document.getElementById("form-registro");
const mensajeRegistro = document.getElementById("mensaje-registro");

let habitaciones = [];
let usuarios = [];
let reservaPendiente = null;


/* ==========================================================
   3. FUNCIONES DE AYUDA
   ========================================================== */
function mostrarMensaje(elemento, texto, tipo) {
    elemento.textContent = texto;
    elemento.className = "mensaje " + tipo;
}

function formatearFecha(texto) {
    return new Date(texto).toLocaleDateString("es-CO", { timeZone: "UTC" });
}

function formatearPrecio(valor) {
    return "$" + valor.toLocaleString("es-CO");
}

function calcularNoches(entrada, salida) {
    return (new Date(salida) - new Date(entrada)) / (1000 * 60 * 60 * 24);
}

function textoError(error, servicio) {
    if (error instanceof TypeError) {
        return `No se pudo conectar con el servicio de ${servicio}. ¿Está encendido?`;
    }
    return error.message;
}

function buscarPorId(lista, id) {
    return lista.find(function (elemento) {
        return elemento.id === id;
    });
}


/* ==========================================================
   4. SERVICIO HABITACIONES: listar habitaciones (GET)
   ========================================================== */
async function cargarHabitaciones() {
    try {
        const respuesta = await fetch(API_HABITACIONES + "/habitaciones");
        habitaciones = await respuesta.json();
        if (!respuesta.ok) throw new Error(habitaciones.mensaje);

        selectHabitacion.innerHTML = "";
        listaHabitaciones.innerHTML = "";

        habitaciones.forEach(function (habitacion) {
            selectHabitacion.innerHTML += `
                <option value="${habitacion.id}">
                    ${habitacion.numero} - ${habitacion.tipo} (${habitacion.capacidad} pers.)
                </option>`;

            listaHabitaciones.innerHTML += `
                <article class="tarjeta">
                    <p class="tarjeta-tipo">${habitacion.tipo}</p>
                    <h3>Habitación ${habitacion.numero}</h3>
                    <p>${habitacion.descripcion || ""}</p>
                    <p>Capacidad: ${habitacion.capacidad} persona(s)</p>
                    <p class="tarjeta-precio">${formatearPrecio(habitacion.precio_noche)} / noche</p>
                    <span class="estado ${habitacion.estado}">${habitacion.estado}</span>
                </article>`;
        });
    } catch (error) {
        selectHabitacion.innerHTML = '<option value="">Sin conexión</option>';
        listaHabitaciones.innerHTML = `<p class="mensaje error">${textoError(error, "Habitaciones")}</p>`;
    }
}


/* ==========================================================
   5. SERVICIO USUARIOS: listar huéspedes (GET)
   ========================================================== */
async function cargarUsuarios() {
    try {
        const respuesta = await fetch(API_USUARIOS + "/usuarios");
        usuarios = await respuesta.json();
        if (!respuesta.ok) throw new Error(usuarios.mensaje);

        selectUsuario.innerHTML = "";
        usuarios.forEach(function (usuario) {
            selectUsuario.innerHTML += `
                <option value="${usuario.id}">${usuario.nombre} ${usuario.apellido}</option>`;
        });
    } catch (error) {
        selectUsuario.innerHTML = '<option value="">Sin conexión</option>';
    }
}


/* ==========================================================
   6. SERVICIO USUARIOS: registrar un huésped nuevo (POST)
   ========================================================== */
formRegistro.addEventListener("submit", async function (evento) {
    evento.preventDefault();

    const nuevoUsuario = {
        nombre: document.getElementById("nombre").value,
        apellido: document.getElementById("apellido").value,
        documento: document.getElementById("documento").value,
        email: document.getElementById("email").value,
        telefono: document.getElementById("telefono").value,
    };

    try {
        const respuesta = await fetch(API_USUARIOS + "/usuarios", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(nuevoUsuario),
        });
        const resultado = await respuesta.json();

        if (respuesta.status === 201) {
            mostrarMensaje(mensajeRegistro, `¡Bienvenido(a), ${nuevoUsuario.nombre}! Ya puedes hacer tu reserva.`, "ok");
            formRegistro.reset();
            await cargarUsuarios();
            selectUsuario.value = resultado.id;
        } else {
            mostrarMensaje(mensajeRegistro, resultado.mensaje, "error");
        }
    } catch (error) {
        mostrarMensaje(mensajeRegistro, "No se pudo registrar. Revisa que el servicio esté encendido y que el documento o el correo no estén ya registrados.", "error");
    }
});


/* ==========================================================
   7. SERVICIO RESERVAS: consultar disponibilidad (GET)
   ========================================================== */
formBuscar.addEventListener("submit", async function (evento) {
    evento.preventDefault();
    btnConfirmar.hidden = true;

    const datos = {
        usuario_id: Number(selectUsuario.value),
        habitacion_id: Number(selectHabitacion.value),
        fecha_entrada: document.getElementById("entrada").value,
        fecha_salida: document.getElementById("salida").value,
        huespedes: Number(document.getElementById("huespedes").value),
    };
    const habitacion = buscarPorId(habitaciones, datos.habitacion_id);

    // Validaciones en el navegador antes de llamar al servicio
    if (!habitacion || !datos.usuario_id) {
        mostrarMensaje(mensajeBuscar, "Faltan habitaciones o huéspedes. Revisa que los servicios estén encendidos.", "error");
        return;
    }
    if (datos.fecha_salida <= datos.fecha_entrada) {
        mostrarMensaje(mensajeBuscar, "La fecha de salida debe ser posterior a la de entrada.", "error");
        return;
    }
    if (datos.huespedes > habitacion.capacidad) {
        mostrarMensaje(mensajeBuscar, `La habitación ${habitacion.numero} es para máximo ${habitacion.capacidad} persona(s).`, "error");
        return;
    }
    if (habitacion.estado === "mantenimiento") {
        mostrarMensaje(mensajeBuscar, `La habitación ${habitacion.numero} está en mantenimiento.`, "error");
        return;
    }

    try {
        const url = `${API_RESERVAS}/reservas/disponibilidad?habitacion_id=${datos.habitacion_id}`
            + `&fecha_entrada=${datos.fecha_entrada}&fecha_salida=${datos.fecha_salida}`;
        const respuesta = await fetch(url);
        const resultado = await respuesta.json();

        if (resultado.disponible) {
            const noches = calcularNoches(datos.fecha_entrada, datos.fecha_salida);
            const total = noches * habitacion.precio_noche;
            mostrarMensaje(mensajeBuscar, `¡Habitación ${habitacion.numero} disponible! ${noches} noche(s) por un total de ${formatearPrecio(total)}.`, "ok");
            reservaPendiente = datos;
            btnConfirmar.hidden = false;
        } else {
            mostrarMensaje(mensajeBuscar, `La habitación ${habitacion.numero} ya está reservada en esas fechas.`, "error");
        }
    } catch (error) {
        mostrarMensaje(mensajeBuscar, "No se pudo conectar con el servicio de Reservas.", "error");
    }
});

formBuscar.addEventListener("input", function () {
    btnConfirmar.hidden = true;
});


/* ==========================================================
   8. SERVICIO RESERVAS: crear la reserva (POST)
   ========================================================== */
btnConfirmar.addEventListener("click", async function () {
    try {
        const respuesta = await fetch(API_RESERVAS + "/reservas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(reservaPendiente),
        });
        const resultado = await respuesta.json();

        if (respuesta.status === 201) {
            mostrarMensaje(mensajeBuscar, `Reserva N.º ${resultado.id} creada correctamente.`, "ok");
            btnConfirmar.hidden = true;
            cargarReservas();
        } else {
            mostrarMensaje(mensajeBuscar, resultado.mensaje, "error");
        }
    } catch (error) {
        mostrarMensaje(mensajeBuscar, "No se pudo conectar con el servicio de Reservas.", "error");
    }
});


/* ==========================================================
   9. SERVICIO RESERVAS: listar reservas (GET)
   ========================================================== */
async function cargarReservas() {
    try {
        const respuesta = await fetch(API_RESERVAS + "/reservas");
        const reservas = await respuesta.json();
        if (!respuesta.ok) throw new Error(reservas.mensaje);

        listaReservas.innerHTML = "";
        if (reservas.length === 0) {
            listaReservas.innerHTML = '<tr><td colspan="8">Aún no hay reservas.</td></tr>';
            return;
        }

        reservas.forEach(function (reserva) {
            const usuario = buscarPorId(usuarios, reserva.usuario_id);
            const habitacion = buscarPorId(habitaciones, reserva.habitacion_id);

            listaReservas.innerHTML += `
                <tr>
                    <td>${reserva.id}</td>
                    <td>${usuario ? usuario.nombre + " " + usuario.apellido : "Usuario " + reserva.usuario_id}</td>
                    <td>${habitacion ? habitacion.numero : reserva.habitacion_id}</td>
                    <td>${formatearFecha(reserva.fecha_entrada)}</td>
                    <td>${formatearFecha(reserva.fecha_salida)}</td>
                    <td>${reserva.huespedes}</td>
                    <td><span class="estado ${reserva.estado}">${reserva.estado}</span></td>
                    <td><button class="btn-eliminar" onclick="eliminarReserva(${reserva.id})">Eliminar</button></td>
                </tr>`;
        });
    } catch (error) {
        listaReservas.innerHTML = `<tr><td colspan="8">${textoError(error, "Reservas")}</td></tr>`;
    }
}


/* ==========================================================
   10. SERVICIO RESERVAS: eliminar una reserva (DELETE)
   ========================================================== */
async function eliminarReserva(id) {
    try {
        const respuesta = await fetch(API_RESERVAS + "/reservas/" + id, { method: "DELETE" });
        const resultado = await respuesta.json();
        mostrarMensaje(mensajeReservas, resultado.mensaje, respuesta.ok ? "ok" : "error");
        cargarReservas();
    } catch (error) {
        mostrarMensaje(mensajeReservas, "No se pudo conectar con el servicio de Reservas.", "error");
    }
}


/* ==========================================================
   11. INICIO: cargar los datos al abrir la página
   (primero habitaciones y usuarios, porque la tabla de reservas los usa)
   ========================================================== */
async function iniciar() {
    await cargarHabitaciones();
    await cargarUsuarios();
    await cargarReservas();
}

iniciar();
