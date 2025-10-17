from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import json
import os

# Cargar JSON de sedes
def cargar_estructura():
    ruta = "data/sedes.json"
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

# Paso 1: /contactosedes → mostrar menú principal
async def contacto_sedes_command(update: Update, context: CallbackContext):
    estructura = cargar_estructura()
    if not estructura:
        await update.message.reply_text("Error cargando los datos. Intentá más tarde.")
        return

    context.user_data["estructura_sedes"] = estructura
    context.user_data["sedes_current_menu"] = None

    main_menu = estructura["main_menu"]
    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=f"sedes_{k}")]
        for k, v in main_menu.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Selecciona:",
        reply_markup=reply_markup
    )

# Paso 2: mostrar submenú según sede
async def handle_sedes_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    selection = query.data.replace("sedes_", "")

    estructura = context.user_data.get("estructura_sedes")
    if not estructura:
        await query.edit_message_text("Por favor iniciá con /contactosedes.")
        return

    main_menu = estructura["main_menu"]
    main_menu_submenus = estructura["main_menu_submenus"]

    if selection in main_menu:
        context.user_data["sedes_current_menu"] = selection
        submenu = main_menu_submenus.get(selection, {})
        keyboard = [
            [InlineKeyboardButton(text=v, callback_data=f"sedes_sub_{selection}{k}")]
            for k, v in submenu.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Seleccionaste: {main_menu[selection]}\n\nElegí una opción:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("Opción inválida.")

# Paso 3: mostrar respuesta final
async def handle_sedes_submenu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_name = query.from_user.first_name
    selection = query.data.replace("sedes_sub_", "")

    estructura = context.user_data.get("estructura_sedes")
    if not estructura:
        await query.edit_message_text("Por favor iniciá con /contactosedes.")
        return

    faq_respuestas = estructura["faq_respuestas"]
    respuesta = faq_respuestas.get(selection)

    if respuesta:
        text = respuesta["text"].replace("{username}", user_name or "usuario")
        await query.edit_message_text(text, parse_mode="Markdown")
    else:
        await query.edit_message_text("Esta opción no tiene información disponible.")

# Exportar handlers para el main
def get_handlers():
    return [
        CommandHandler("contactosedes", contacto_sedes_command),
        CallbackQueryHandler(handle_sedes_main_menu, pattern=r"^sedes_[1-9]$"),
        CallbackQueryHandler(handle_sedes_submenu, pattern=r"^sedes_sub_[1-9][a-z]$")
    ]
