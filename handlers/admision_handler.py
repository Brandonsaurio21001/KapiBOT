from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import json
import os

# Función para cargar el JSON según tipo de estudiante
def cargar_estructura(tipo):
    ruta = f"data/admision_{tipo}.json"
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

async def mostrar_menu_principal(query, context):
    estructura = context.user_data.get("estructura_admision")

    if not estructura:
        await query.edit_message_text("Por favor iniciá con /admision.")
        return

    main_menu = estructura["main_menu"]

    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=f"admision_{k}")]
        for k, v in main_menu.items()
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Al volver al menú principal, ya no hay una opción interna activa.
    context.user_data["admision_current_menu"] = None

    await query.edit_message_text(
        "Seleccioná una categoría de admisión:",
        reply_markup=reply_markup
    )

# Paso 1: /admision → elegir tipo
async def admision_command(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("🔰 Nuevo Ingreso", callback_data="admision_tipo_NI"),
            InlineKeyboardButton("🎓 Estudiante Regular", callback_data="admision_tipo_ER")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "¿Sos estudiante de nuevo ingreso o estudiante regular?",
        reply_markup=reply_markup
    )

# Paso 2: Guardar tipo y mostrar menú principal
async def seleccionar_tipo_estudiante(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    tipo = query.data.split("_")[-1]  # "NI" o "ER" segun el tipo de json
    context.user_data["tipo_estudiante_admision"] = tipo

    estructura = cargar_estructura(tipo)
    if not estructura:
        await query.edit_message_text("Error cargando los datos. Intentá más tarde.")
        return

    context.user_data["estructura_admision"] = estructura
    context.user_data["admision_current_menu"] = None

    main_menu = estructura["main_menu"]
    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=f"admision_{k}")]
        for k, v in main_menu.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "Seleccioná una categoría sobre el proceso de admisión:",
        reply_markup=reply_markup
    )

# Paso 3: Manejo del menú principal
async def handle_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    selection = query.data.replace("admision_", "")

    estructura = context.user_data.get("estructura_admision")
    if not estructura:
        await query.edit_message_text("Por favor iniciá con /admision.")
        return

    main_menu = estructura["main_menu"]
    main_menu_submenus = estructura["main_menu_submenus"]

    if selection in main_menu:
        context.user_data["admision_current_menu"] = selection
        submenu = main_menu_submenus.get(selection, {})
        keyboard = [
            [InlineKeyboardButton(text=v, callback_data=f"admision_{selection}{k}")]
            for k, v in submenu.items()
        ]
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="admision_back")
        ])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Seleccionaste: {main_menu[selection]}\n\nElegí una opción:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("Opción inválida.")

# Paso 4: Manejo del submenú
async def handle_submenu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    selection = query.data.replace("admision_", "")
    user_name = query.from_user.first_name

    estructura = context.user_data.get("estructura_admision")
    if not estructura:
        await query.edit_message_text("Por favor iniciá con /admision.")
        return

    faq_respuestas = estructura["faq_respuestas"]
    respuesta = faq_respuestas.get(selection)

    if respuesta:
        text = respuesta["text"].replace("{username}", user_name or "usuario")
        await query.edit_message_text(text, parse_mode="Markdown")
    else:
        await query.edit_message_text("Esta opción no tiene información disponible para tu tipo de estudiante.")

async def handle_back(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    await mostrar_menu_principal(query, context)

# Registro de handlers
def get_handlers():
    return [
        CommandHandler("admision", admision_command),
        CallbackQueryHandler(seleccionar_tipo_estudiante, pattern=r"^admision_tipo_(NI|ER)$"),
        CallbackQueryHandler(handle_main_menu, pattern=r"^admision_[1-9]$"),
        CallbackQueryHandler(handle_submenu, pattern=r"^admision_[1-9][a-z]$"),
        CallbackQueryHandler(handle_back,pattern=r"^admision_back$")
    ]
