/* ==========================================================
   1. CONFIGURACIÓN: dirección de cada microservicio
   (puertos publicados en docker-compose.yml)
   ========================================================== */
const API_USUARIOS = "http://localhost:5001";
const API_RESERVAS = "http://localhost:5002";
const API_HABITACIONES = "http://localhost:5003";
const API_PAGOS = "http://localhost:5004";

const FOTOS_HABITACION = {
    sencilla: "img/habitacion-sencilla.jpg",
    doble: "img/habitacion-doble.jpg",
    suite: "img/habitacion-suite.jpg",
};


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
const avisoCircuitos = document.getElementById("aviso-circuitos");
const formPago = document.getElementById("form-pago");
const selectReservaPago = document.getElementById("reserva-pago");
const mensajePago = document.getElementById("mensaje-pago");
const avisoPagos = document.getElementById("aviso-pagos");

let habitaciones = [];
let usuarios = [];
// null = el servicio de Pagos no respondió; [] = respondió sin pagos
let pagos = null;
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

            // Un tipo nuevo que no esté en FOTOS_HABITACION usa la foto de la doble
            const foto = FOTOS_HABITACION[habitacion.tipo] || FOTOS_HABITACION.doble;
            const enMantenimiento = habitacion.estado === "mantenimiento";
            listaHabitaciones.innerHTML += `
                <article class="tarjeta">
                    <div class="tarjeta-foto">
                        <img src="${foto}" alt="Habitación ${habitacion.tipo}" loading="lazy">
                        <span class="estado ${habitacion.estado}">${habitacion.estado}</span>
                    </div>
                    <div class="tarjeta-cuerpo">
                        <p class="tarjeta-tipo">${habitacion.tipo}</p>
                        <h3>Habitación ${habitacion.numero}</h3>
                        <p>${habitacion.descripcion || ""}</p>
                        <p>Capacidad: ${habitacion.capacidad} persona(s)</p>
                        <div class="tarjeta-pie">
                            <p class="tarjeta-precio">${formatearPrecio(habitacion.precio_noche)} <span>/ noche</span></p>
                            <button class="btn-tarjeta" onclick="elegirHabitacion(${habitacion.id})" ${enMantenimiento ? "disabled" : ""}>
                                ${enMantenimiento ? "No disponible" : "Reservar"}
                            </button>
                        </div>
                    </div>
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
        const usuarioCreado = await respuesta.json();

        if (respuesta.status === 201) {
            mostrarMensaje(mensajeRegistro, `Registro completo. ${nuevoUsuario.nombre} ya aparece como huésped titular en el buscador.`, "ok");
            formRegistro.reset();
            await cargarUsuarios();
            selectUsuario.value = usuarioCreado.id;
        } else {
            mostrarMensaje(mensajeRegistro, usuarioCreado.mensaje, "error");
        }
    } catch (error) {
        mostrarMensaje(mensajeRegistro, textoError(error, "Usuarios"), "error");
    }
});


/* ==========================================================
   7. SERVICIO RESERVAS: consultar disponibilidad (GET)
   ========================================================== */
formBuscar.addEventListener("submit", async function (evento) {
    evento.preventDefault();
    btnConfirmar.hidden = true;

    const consulta = {
        usuario_id: Number(selectUsuario.value),
        habitacion_id: Number(selectHabitacion.value),
        fecha_entrada: document.getElementById("entrada").value,
        fecha_salida: document.getElementById("salida").value,
        huespedes: Number(document.getElementById("huespedes").value),
    };
    const habitacion = buscarPorId(habitaciones, consulta.habitacion_id);

    // Lo que el navegador ya sabe se valida aquí, sin gastar una petición al servicio
    if (!habitacion || !consulta.usuario_id) {
        mostrarMensaje(mensajeBuscar, "Faltan habitaciones o huéspedes. Revisa que los servicios estén encendidos.", "error");
        return;
    }
    if (consulta.fecha_salida <= consulta.fecha_entrada) {
        mostrarMensaje(mensajeBuscar, "La fecha de salida debe ser posterior a la de entrada.", "error");
        return;
    }
    if (consulta.huespedes > habitacion.capacidad) {
        mostrarMensaje(mensajeBuscar, `La habitación ${habitacion.numero} es para máximo ${habitacion.capacidad} persona(s).`, "error");
        return;
    }
    if (habitacion.estado === "mantenimiento") {
        mostrarMensaje(mensajeBuscar, `La habitación ${habitacion.numero} está en mantenimiento.`, "error");
        return;
    }

    try {
        const url = `${API_RESERVAS}/reservas/disponibilidad?habitacion_id=${consulta.habitacion_id}`
            + `&fecha_entrada=${consulta.fecha_entrada}&fecha_salida=${consulta.fecha_salida}`;
        const respuesta = await fetch(url);
        const disponibilidad = await respuesta.json();
        if (!respuesta.ok) throw new Error(disponibilidad.mensaje);

        if (disponibilidad.disponible) {
            const noches = calcularNoches(consulta.fecha_entrada, consulta.fecha_salida);
            const total = noches * habitacion.precio_noche;
            mostrarMensaje(mensajeBuscar, `Habitación ${habitacion.numero} disponible: ${noches} noche(s), total ${formatearPrecio(total)}.`, "ok");
            reservaPendiente = consulta;
            btnConfirmar.hidden = false;
        } else {
            mostrarMensaje(mensajeBuscar, `La habitación ${habitacion.numero} ya está reservada en esas fechas.`, "error");
        }
    } catch (error) {
        mostrarMensaje(mensajeBuscar, textoError(error, "Reservas"), "error");
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
        const reservaCreada = await respuesta.json();

        if (respuesta.status === 201) {
            mostrarMensaje(mensajeBuscar, `Reserva N.º ${reservaCreada.id} creada.`, "ok");
            btnConfirmar.hidden = true;
            cargarReservas();
        } else {
            mostrarMensaje(mensajeBuscar, reservaCreada.mensaje, "error");
        }
    } catch (error) {
        mostrarMensaje(mensajeBuscar, textoError(error, "Reservas"), "error");
    }
    revisarCircuitos();
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
        selectReservaPago.innerHTML = "";
        if (reservas.length === 0) {
            listaReservas.innerHTML = '<tr><td colspan="9">Aún no hay reservas.</td></tr>';
        }

        reservas.forEach(function (reserva) {
            const usuario = buscarPorId(usuarios, reserva.usuario_id);
            const habitacion = buscarPorId(habitaciones, reserva.habitacion_id);
            const numeroHabitacion = habitacion ? habitacion.numero : reserva.habitacion_id;
            const pago = pagos && pagos.find(function (registro) {
                return registro.reserva_id === reserva.id;
            });

            let celdaPago = "Sin conexión";
            if (pago) {
                celdaPago = `<span class="estado ${pago.estado}">${formatearPrecio(pago.monto)} · ${pago.estado}</span>`;
            } else if (pagos) {
                celdaPago = `<button class="btn-pagar" onclick="elegirReservaParaPago(${reserva.id})">Pagar</button>`;
                selectReservaPago.innerHTML += `
                    <option value="${reserva.id}">N.º ${reserva.id} · Habitación ${numeroHabitacion} · ${formatearFecha(reserva.fecha_entrada)}</option>`;
            }

            listaReservas.innerHTML += `
                <tr>
                    <td>${reserva.id}</td>
                    <td>${usuario ? usuario.nombre + " " + usuario.apellido : "Usuario " + reserva.usuario_id}</td>
                    <td>${numeroHabitacion}</td>
                    <td>${formatearFecha(reserva.fecha_entrada)}</td>
                    <td>${formatearFecha(reserva.fecha_salida)}</td>
                    <td>${reserva.huespedes}</td>
                    <td><span class="estado ${reserva.estado}">${reserva.estado}</span></td>
                    <td>${celdaPago}</td>
                    <td><button class="btn-eliminar" onclick="eliminarReserva(${reserva.id})">Eliminar</button></td>
                </tr>`;
        });

        if (!pagos) {
            selectReservaPago.innerHTML = '<option value="">Sin conexión con Pagos</option>';
        } else if (selectReservaPago.options.length === 0) {
            selectReservaPago.innerHTML = '<option value="">No hay reservas por pagar</option>';
        }
    } catch (error) {
        listaReservas.innerHTML = `<tr><td colspan="9">${textoError(error, "Reservas")}</td></tr>`;
        selectReservaPago.innerHTML = '<option value="">Sin conexión con Reservas</option>';
    }
}


/* ==========================================================
   10. SERVICIO RESERVAS: eliminar una reserva (DELETE)
   ========================================================== */
async function eliminarReserva(id) {
    try {
        const respuesta = await fetch(API_RESERVAS + "/reservas/" + id, { method: "DELETE" });
        const confirmacion = await respuesta.json();
        mostrarMensaje(mensajeReservas, confirmacion.mensaje, respuesta.ok ? "ok" : "error");
        cargarReservas();
    } catch (error) {
        mostrarMensaje(mensajeReservas, textoError(error, "Reservas"), "error");
    }
}


/* ==========================================================
   11. RESERVAR DESDE UNA TARJETA: llevar la habitación al buscador
   ========================================================== */
function elegirHabitacion(id) {
    const habitacion = buscarPorId(habitaciones, id);
    const selectHuespedes = document.getElementById("huespedes");

    selectHabitacion.value = id;
    if (Number(selectHuespedes.value) > habitacion.capacidad) {
        selectHuespedes.value = habitacion.capacidad;
    }
    btnConfirmar.hidden = true;
    mostrarMensaje(mensajeBuscar, `Elegiste la habitación ${habitacion.numero}. Indica las fechas y presiona Buscar.`, "ok");

    document.getElementById("buscador").scrollIntoView({ behavior: "smooth" });
    document.getElementById("entrada").focus({ preventScroll: true });
}


/* ==========================================================
   12. CIRCUIT BREAKER: avisos de Reservas y de Pagos (GET)
   ========================================================== */
function mostrarAvisosCircuito(contenedor, circuitos, accion) {
    const avisos = [];
    Object.entries(circuitos).forEach(function ([servicio, circuito]) {
        const nombre = servicio.charAt(0).toUpperCase() + servicio.slice(1);
        if (circuito.estado === "OPEN") {
            avisos.push(`El servicio de ${nombre} no está respondiendo. No se pueden ${accion} por ahora; se volverá a intentar en unos ${circuito.periodo_recuperacion_s} segundos.`);
        } else if (circuito.estado === "HALF-OPEN") {
            avisos.push(`El servicio de ${nombre} se está recuperando. El próximo intento comprobará si ya responde.`);
        }
    });

    contenedor.innerHTML = avisos.map(function (aviso) {
        return `<p>${aviso}</p>`;
    }).join("");
    contenedor.hidden = avisos.length === 0;
}

async function revisarCircuitos() {
    try {
        const respuesta = await fetch(API_RESERVAS + "/reservas/circuito");
        const circuitos = await respuesta.json();
        if (!respuesta.ok) throw new Error(circuitos.mensaje);
        mostrarAvisosCircuito(avisoCircuitos, circuitos, "confirmar reservas");
    } catch (error) {
        // Si Reservas no responde, la tabla de reservas ya muestra ese error
        avisoCircuitos.hidden = true;
    }
}

async function revisarCircuitoPagos() {
    try {
        const respuesta = await fetch(API_PAGOS + "/pagos/circuito");
        const circuito = await respuesta.json();
        if (!respuesta.ok) throw new Error(circuito.mensaje);
        // Pagos responde un solo circuito (el de su llamada a Reservas), sin nombre de servicio
        mostrarAvisosCircuito(avisoPagos, { reservas: circuito }, "registrar pagos");
    } catch (error) {
        // Si Pagos no responde, la lista de reservas por pagar ya lo indica
        avisoPagos.hidden = true;
    }
}


/* ==========================================================
   13. SERVICIO PAGOS: listar pagos (GET)
   ========================================================== */
async function cargarPagos() {
    try {
        const respuesta = await fetch(API_PAGOS + "/pagos");
        pagos = await respuesta.json();
        if (!respuesta.ok) throw new Error(pagos.mensaje);
    } catch (error) {
        pagos = null;
        mostrarMensaje(mensajePago, textoError(error, "Pagos"), "error");
    }
}


/* ==========================================================
   14. SERVICIO PAGOS: registrar el pago de una reserva (POST)
   ========================================================== */
function elegirReservaParaPago(id) {
    selectReservaPago.value = id;
    mostrarMensaje(mensajePago, `Elegiste la reserva N.º ${id}. Escoge el método de pago y presiona Pagar.`, "ok");
    formPago.scrollIntoView({ behavior: "smooth", block: "center" });
    document.getElementById("metodo-pago").focus({ preventScroll: true });
}

formPago.addEventListener("submit", async function (evento) {
    evento.preventDefault();

    const reservaId = Number(selectReservaPago.value);
    if (!reservaId) {
        mostrarMensaje(mensajePago, "No hay una reserva seleccionada para pagar.", "error");
        return;
    }

    try {
        const respuesta = await fetch(API_PAGOS + "/pagos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                reserva_id: reservaId,
                metodo_pago: document.getElementById("metodo-pago").value,
            }),
        });
        const pagoCreado = await respuesta.json();

        if (respuesta.status === 201) {
            mostrarMensaje(mensajePago, `Pago N.º ${pagoCreado.id} de la reserva ${reservaId}: ${formatearPrecio(pagoCreado.monto)}, estado ${pagoCreado.estado}.`, "ok");
            await cargarPagos();
            cargarReservas();
        } else {
            mostrarMensaje(mensajePago, pagoCreado.mensaje, "error");
        }
    } catch (error) {
        mostrarMensaje(mensajePago, textoError(error, "Pagos"), "error");
    }
    revisarCircuitoPagos();
});


/* ==========================================================
   15. INICIO: cargar los datos al abrir la página
   (la tabla de reservas usa habitaciones, usuarios y pagos, por eso van primero)
   ========================================================== */
async function iniciar() {
    await cargarHabitaciones();
    await cargarUsuarios();
    await cargarPagos();
    await cargarReservas();
    revisarCircuitos();
    revisarCircuitoPagos();
}

iniciar();
