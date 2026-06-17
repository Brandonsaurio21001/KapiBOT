from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import json
import os

# Cargar JSON de sedes
def cargar_estructura():
    ruta = "data/comedorInstitucional.json"
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)
    
async def mostrar_menu_principal(query, context):
    estructura = context.user_data.get("estructura_comedorInsti")

    if not estructura:
        await query.edit_message_text("Por favor iniciá con /comedorInsti.")
        return

    main_menu = estructura["main_menu"]

    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=f"comedorInsti_{k}")]
        for k, v in main_menu.items()
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Al volver al menú principal, ya no hay una opción interna activa.
    context.user_data["comedorInsti_current_menu"] = None

    await query.edit_message_text(
        "Seleccioná una categoría de guías de horario:",
        reply_markup=reply_markup
    )

# Paso 1: /comedorInsti → mostrar menú principal
async def comedorInsti_command(update: Update, context: CallbackContext):
    estructura = cargar_estructura()
    if not estructura:
        await update.message.reply_text("Error cargando los datos. Intentá más tarde.")
        return

    context.user_data["estructura_comedorInsti"] = estructura
    context.user_data["comedorInsti_current_menu"] = None

    main_menu = estructura["main_menu"]
    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=f"comedorInsti_{k}")]
        for k, v in main_menu.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Selecciona:",
        reply_markup=reply_markup
    )

# Paso 2: mostrar submenú según sede
async def handle_comedorInsti_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    selection = query.data.replace("comedorInsti_", "")

    estructura = context.user_data.get("estructura_comedorInsti")
    if not estructura:
        await query.edit_message_text("Por favor iniciá con /comedorInsti.")
        return

    main_menu = estructura["main_menu"]
    main_menu_submenus = estructura["main_menu_submenus"]

    if selection in main_menu:
        context.user_data["comedorInsti_current_menu"] = selection
        submenu = main_menu_submenus.get(selection, {})
        keyboard = [
            [InlineKeyboardButton(text=v, callback_data=f"comedorInsti_sub_{selection}{k}")]
            for k, v in submenu.items()
        ]
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="comedorInsti_back")
        ])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Seleccionaste: {main_menu[selection]}\n\nElegí una opción:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("Opción inválida.")

# Paso 3: mostrar respuesta final
async def handle_comedorInsti_submenu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_name = query.from_user.first_name
    selection = query.data.replace("comedorInsti_sub_", "")

    estructura = context.user_data.get("estructura_comedorInsti")
    if not estructura:
        await query.edit_message_text("Por favor iniciá con /comedorInsti.")
        return

    faq_respuestas = estructura["faq_respuestas"]
    respuesta = faq_respuestas.get(selection)

    if respuesta:
        text = respuesta["text"].replace("{username}", user_name or "usuario")
        await query.edit_message_text(text, parse_mode="Markdown")
    else:
        await query.edit_message_text("Esta opción no tiene información disponible.")

async def handle_back(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    await mostrar_menu_principal(query, context)
# Exportar handlers para el main
def get_handlers():
    return [
        CommandHandler("comedorInsti", comedorInsti_command),
        CallbackQueryHandler(handle_comedorInsti_main_menu, pattern=r"^comedorInsti_[1-9]$"),
        CallbackQueryHandler(handle_comedorInsti_submenu, pattern=r"^comedorInsti_sub_[1-9][a-z]$"),
        CallbackQueryHandler(handle_back, pattern=r"^comedorInsti_back$")
    ]
