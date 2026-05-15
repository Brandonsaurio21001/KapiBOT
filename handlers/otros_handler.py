from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import json
import os


# ---------------------------------------------------------
# Función: cargar_estructura(tipo)
# ---------------------------------------------------------
# Propósito:
# Cargar el archivo JSON correspondiente al tipo de estudiante.
#
# En este módulo existen dos archivos:
# - otros_NI.json  -> información para Nuevo Ingreso
# - otros_ER.json  -> información para Estudiante Regular
#
# Esta función recibe el tipo ("NI" o "ER"), construye la ruta
# del archivo y devuelve su contenido como diccionario de Python.
#
# Si el archivo no existe, devuelve None.
# ---------------------------------------------------------
def cargar_estructura(tipo):
    ruta = f"data/otros_{tipo}.json"

    if not os.path.exists(ruta):
        return None

    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------
# Función auxiliar: mostrar_menu_principal(query, context)
# ---------------------------------------------------------
# Propósito:
# Mostrar el menú principal del módulo "otros trámites".
#
# Esta función se reutiliza en dos momentos:
# 1. Después de que la persona selecciona el tipo de estudiante.
# 2. Cuando la persona presiona el botón "Volver".
#
# Ventaja:
# Evita repetir el mismo código en varios lugares.
#
# Qué hace internamente:
# - Recupera la estructura JSON guardada en context.user_data.
# - Construye los botones del menú principal.
# - Reinicia el valor de "otros_current_menu" porque se está
#   regresando al nivel principal de navegación.
# - Edita el mensaje actual para mostrar el menú.
# ---------------------------------------------------------
async def mostrar_menu_principal(query, context):
    estructura = context.user_data.get("estructura_otros")

    if not estructura:
        await query.edit_message_text("Por favor iniciá con /otrostramites.")
        return

    main_menu = estructura["main_menu"]

    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=f"otros_{k}")]
        for k, v in main_menu.items()
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Al volver al menú principal, ya no hay una opción interna activa.
    context.user_data["otros_current_menu"] = None

    await query.edit_message_text(
        "Seleccioná una categoría de otros trámites:",
        reply_markup=reply_markup
    )


# ---------------------------------------------------------
# Paso 1: Comando /otrostramites
# ---------------------------------------------------------
# Propósito:
# Iniciar el flujo del módulo.
#
# Antes de mostrar cualquier contenido, el bot necesita saber
# si la persona es:
# - Nuevo Ingreso
# - Estudiante Regular
#
# Esto se hace porque el contenido cambia según el perfil.
#
# Qué hace:
# - Muestra dos botones.
# - Cada botón lleva un callback_data con prefijo "otros_tipo_"
#   para identificar que pertenece a este módulo.
# ---------------------------------------------------------
async def otros_command(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("🔰 Nuevo Ingreso", callback_data="otros_tipo_NI"),
            InlineKeyboardButton("🎓 Estudiante Regular", callback_data="otros_tipo_ER")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "¿Sos estudiante de nuevo ingreso o estudiante regular?",
        reply_markup=reply_markup
    )


# ---------------------------------------------------------
# Paso 2: Selección del tipo de estudiante
# ---------------------------------------------------------
# Propósito:
# Guardar el tipo de estudiante seleccionado y cargar la
# estructura correcta del JSON.
#
# Qué hace:
# - Lee el callback_data presionado.
# - Extrae "NI" o "ER".
# - Guarda ese valor en context.user_data para mantener el contexto.
# - Carga el JSON correspondiente.
# - Guarda la estructura en memoria.
# - Llama a mostrar_menu_principal para continuar el flujo.
#
# Importante:
# context.user_data funciona como una memoria por usuario,
# permitiendo conservar datos entre una interacción y otra.
# ---------------------------------------------------------
async def seleccionar_tipo_estudiante(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Del callback_data "otros_tipo_NI" o "otros_tipo_ER"
    # se toma únicamente la última parte.
    tipo = query.data.split("_")[-1]

    # Guardamos el tipo seleccionado.
    context.user_data["tipo_estudiante_otros"] = tipo

    estructura = cargar_estructura(tipo)
    if not estructura:
        await query.edit_message_text("Error cargando los datos. Intentá más tarde.")
        return

    # Guardamos toda la estructura del JSON para reutilizarla
    # en los siguientes pasos del flujo.
    context.user_data["estructura_otros"] = estructura

    # Esta variable puede servir para recordar qué opción de menú
    # principal fue seleccionada.
    context.user_data["otros_current_menu"] = None

    # Mostramos el menú principal una vez cargada la estructura.
    await mostrar_menu_principal(query, context)


# ---------------------------------------------------------
# Paso 3: Manejo del menú principal
# ---------------------------------------------------------
# Propósito:
# Mostrar el submenú correspondiente a la opción elegida.
#
# Flujo:
# - La persona ya eligió tipo de estudiante.
# - El bot ya mostró el menú principal.
# - Ahora la persona presiona una opción de ese menú.
#
# Qué hace:
# - Extrae la opción seleccionada del callback_data.
# - Busca esa opción dentro de main_menu.
# - Obtiene el submenú asociado desde main_menu_submenus.
# - Construye los botones del submenú.
# - Agrega un botón "Volver" para regresar al menú principal.
#
# Ejemplo:
# Si la opción principal es "1", las opciones del submenú
# se construyen como:
# - otros_sub_1a
# - otros_sub_1b
# - otros_sub_1c
#
# Esto permite identificar claramente que:
# - pertenece al módulo "otros"
# - es una selección de submenú
# - corresponde a una clave concreta del JSON
# ---------------------------------------------------------
async def handle_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Se elimina el prefijo "otros_" para obtener solo la clave real.
    selection = query.data.replace("otros_", "")

    estructura = context.user_data.get("estructura_otros")
    if not estructura:
        await query.edit_message_text("Por favor iniciá con /otrostramites.")
        return

    main_menu = estructura["main_menu"]
    main_menu_submenus = estructura["main_menu_submenus"]

    if selection in main_menu:
        # Guardamos qué opción principal fue seleccionada.
        context.user_data["otros_current_menu"] = selection

        submenu = main_menu_submenus.get(selection, {})

        keyboard = [
            [InlineKeyboardButton(text=v, callback_data=f"otros_sub_{selection}{k}")]
            for k, v in submenu.items()
        ]

        # Este botón permite regresar al menú principal sin necesidad
        # de escribir nuevamente el comando /otrostramites.
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="otros_back")
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Seleccionaste: {main_menu[selection]}\n\nElegí una opción:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("Opción inválida.")


# ---------------------------------------------------------
# Paso 4: Manejo del submenú
# ---------------------------------------------------------
# Propósito:
# Mostrar la respuesta final correspondiente a una opción
# concreta del submenú.
#
# Qué hace:
# - Extrae la clave real quitando el prefijo "otros_sub_".
# - Busca esa clave dentro de faq_respuestas.
# - Si existe, reemplaza {username} por el nombre real del usuario.
# - Muestra la respuesta en formato Markdown.
#
# Ejemplo:
# callback_data recibido: "otros_sub_1a"
# clave buscada en faq_respuestas: "1a"
# ---------------------------------------------------------
async def handle_submenu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_name = query.from_user.first_name

    # Se elimina el prefijo para obtener la clave que sí existe
    # en faq_respuestas dentro del JSON.
    selection = query.data.replace("otros_sub_", "")

    estructura = context.user_data.get("estructura_otros")
    if not estructura:
        await query.edit_message_text("Por favor iniciá con /otrostramites.")
        return

    faq_respuestas = estructura["faq_respuestas"]
    respuesta = faq_respuestas.get(selection)

    if respuesta:
        text = respuesta["text"].replace("{username}", user_name or "usuario")
        await query.edit_message_text(text, parse_mode="Markdown")
    else:
        await query.edit_message_text("Esta opción no tiene información disponible.")


# ---------------------------------------------------------
# Paso 5: Botón "Volver"
# ---------------------------------------------------------
# Propósito:
# Permitir que la persona regrese del submenú al menú principal.
#
# Qué hace:
# - Responde el callback para que Telegram sepa que fue atendido.
# - Llama a la función auxiliar mostrar_menu_principal.
#
# Ventaja:
# La navegación se vuelve más amigable y no obliga al usuario
# a volver a escribir el comando si seleccionó una opción por error.
# ---------------------------------------------------------
async def handle_back(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    await mostrar_menu_principal(query, context)


# ---------------------------------------------------------
# Registro de handlers del módulo
# ---------------------------------------------------------
# Propósito:
# Devolver la lista de handlers que este módulo necesita.
#
# Orden importante:
# - Primero el comando principal.
# - Luego la selección de tipo.
# - Luego el botón volver.
# - Luego el menú principal.
# - Finalmente el submenú.
#
# Cada pattern está diseñado para capturar solo los callbacks
# que pertenecen a este módulo.
# ---------------------------------------------------------
def get_handlers():
    return [
        CommandHandler("otrostramites", otros_command),

        # Captura la selección de tipo de estudiante:
        # otros_tipo_NI o otros_tipo_ER
        CallbackQueryHandler(
            seleccionar_tipo_estudiante,
            pattern=r"^otros_tipo_(NI|ER)$"
        ),

        # Captura el botón "Volver"
        CallbackQueryHandler(
            handle_back,
            pattern=r"^otros_back$"
        ),

        # Captura las opciones del menú principal:
        # otros_1, otros_2, etc.
        CallbackQueryHandler(
            handle_main_menu,
            pattern=r"^otros_[1-9]$"
        ),

        # Captura las opciones del submenú:
        # otros_sub_1a, otros_sub_2b, etc.
        CallbackQueryHandler(
            handle_submenu,
            pattern=r"^otros_sub_[1-9][a-z]$"
        )
    ]