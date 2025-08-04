
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import json
import os

# Función para cargar el JSON según tipo de estudiante
def cargar_estructura(tipo):
    ruta = f"data/expediente_{tipo}.json"
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

# Paso 1: /expediente → elegir tipo
async def expediente_command(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("🔰 Nuevo Ingreso", callback_data="expediente_tipo_NI"),
            InlineKeyboardButton("🎓 Estudiante Regular", callback_data="expediente_tipo_ER")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "¿Sos estudiante de nuevo ingreso o estudiante regular?",
        reply_markup=reply_markup
    )

#Paso 2: Seleccionar tipo → mostrar menú
async def seleccionar_tipo_estudiante(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    tipo = query.data.split("_")[-1]  # "NI" o "ER"
    context.user_data["tipo_estudiante"] = tipo

    estructura = cargar_estructura(tipo)
    if not estructura:
        await query.edit_message_text("Error cargando los datos. Intentá más tarde.")
        return

    context.user_data["estructura"] = estructura
    context.user_data["current_menu"] = None

    main_menu = estructura["main_menu"]
    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=k)] for k, v in main_menu.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "Seleccioná una categoría de expediente:",
        reply_markup=reply_markup
    )

#Paso 3: Elegir categoría → mostrar submenú
async def handle_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    selection = query.data

    estructura = context.user_data.get("estructura")
    if not estructura:
        await query.edit_message_text("Por favor iniciá con /expediente.")
        return

    main_menu = estructura["main_menu"]
    main_menu_submenus = estructura["main_menu_submenus"]

    if selection in main_menu:
        context.user_data["current_menu"] = selection
        submenu = main_menu_submenus.get(selection, {})
        keyboard = [
            [InlineKeyboardButton(text=v, callback_data=f"{selection}{k}")]
            for k, v in submenu.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Seleccionaste: {main_menu[selection]}\n\nElegí una opción:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("Opción inválida.")

# Paso 4: Mostrar respuesta final
async def handle_submenu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    selection = query.data
    user_name = query.from_user.first_name

    estructura = context.user_data.get("estructura")
    if not estructura:
        await query.edit_message_text("Por favor iniciá con /expediente.")
        return

    faq_respuestas = estructura["faq_respuestas"]
    respuesta = faq_respuestas.get(selection)

    if respuesta:
        text = respuesta["text"].replace("{username}", user_name or "usuario")
        await query.edit_message_text(text, parse_mode="Markdown")
    else:
        await query.edit_message_text("Esta opción no tiene información disponible para tu tipo de estudiante.")

# Registro de handlers
def get_handlers():
    return [
        CommandHandler("expediente", expediente_command),
        CallbackQueryHandler(seleccionar_tipo_estudiante, pattern=r"^expediente_tipo_(NI|ER)$"),
        CallbackQueryHandler(handle_main_menu, pattern=r"^[1-9]$"),
        CallbackQueryHandler(handle_submenu, pattern=r"^[1-9][a-z]$")
    ]
