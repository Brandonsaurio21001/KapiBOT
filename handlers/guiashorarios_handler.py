from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import json

# Cargar estructura desde JSON
with open("data/guias.json", encoding="utf-8") as f:
    estructura = json.load(f)

main_menu = estructura["main_menu"]
main_menu_submenus = estructura["main_menu_submenus"]
faq_respuestas = estructura["faq_respuestas"]

# Comando /guiashorarios
async def guias_command(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=f"guiashorarios_{k}")]
        for k, v in main_menu.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Seleccioná una categoría de guías de horario:", reply_markup=reply_markup
    )
    context.user_data["guiashorarios_current_menu"] = None

# Manejo del menú principal
async def handle_guias_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    selection = query.data.replace("guiashorarios_", "")

    if selection in main_menu:
        context.user_data["guiashorarios_current_menu"] = selection
        submenu = main_menu_submenus.get(selection, {})
        keyboard = [
            [InlineKeyboardButton(text=v, callback_data=f"guiashorarios_{selection}{k}")]
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
async def handle_guias_submenu(update: Update, context: CallbackContext):
    query = update.callback_query
    selection = query.data.replace("guiashorarios_", "")
    user_name = query.from_user.first_name

    if context.user_data.get("guiashorarios_current_menu"):
        respuesta = faq_respuestas.get(selection)

        if respuesta:
            text = respuesta["text"].replace("{username}", user_name or "usuario")
            await query.edit_message_text(text, parse_mode="Markdown")
        else:
            await query.edit_message_text("No se encontró una respuesta para esta opción.")
    else:
        await query.edit_message_text("Por favor iniciá con /guiashorarios.")

def get_handlers():
    return [
        CommandHandler("guiashorarios", guias_command),
        CallbackQueryHandler(handle_guias_main_menu, pattern=r"^guiashorarios_[1]$"),
        CallbackQueryHandler(handle_guias_submenu, pattern=r"^guiashorarios_1[a-i]$")
    ]
