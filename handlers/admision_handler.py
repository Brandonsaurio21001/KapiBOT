from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import json

# Cargar estructura desde JSON
with open("data/admision.json", encoding="utf-8") as f:
    estructura = json.load(f)

main_menu = estructura["main_menu"]
main_menu_submenus = estructura["main_menu_submenus"]
faq_respuestas = estructura["faq_respuestas"]

# Comando /admision
async def admision_command(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=f"admision_{k}")]
        for k, v in main_menu.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Seleccioná una categoría de admisión:", reply_markup=reply_markup
    )
    context.user_data["admision_current_menu"] = None

# Manejo del menú principal
async def handle_admision_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    selection = query.data.replace("admision_", "")

    if selection in main_menu:
        context.user_data["admision_current_menu"] = selection
        submenu = main_menu_submenus.get(selection, {})
        keyboard = [
            [InlineKeyboardButton(text=v, callback_data=f"admision_{selection}{k}")]
            for k, v in submenu.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Seleccionaste: {main_menu[selection]}\n\nElegí una opción:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("Opción inválida.")

# Manejo del submenú
async def handle_admision_submenu(update: Update, context: CallbackContext):
    query = update.callback_query
    selection = query.data.replace("admision_", "")
    user_name = query.from_user.first_name

    if context.user_data.get("admision_current_menu"):
        respuesta = faq_respuestas.get(selection)

        if respuesta:
            text = respuesta["text"].replace("{username}", user_name or "usuario")
            await query.edit_message_text(text, parse_mode="Markdown")
        else:
            await query.edit_message_text("No se encontró una respuesta para esta opción.")
    else:
        await query.edit_message_text("Por favor iniciá con /admision.")

# Registro de handlers
def get_handlers():
    return [
        CommandHandler("admision", admision_command),
        CallbackQueryHandler(handle_admision_main_menu, pattern=r"^admision_[1-9]0?$"),
        CallbackQueryHandler(handle_admision_submenu, pattern=r"^admision_[1-9]0?[a-z]$")
    ]
