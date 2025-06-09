
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import json

# Cargar estructura desde JSON
with open("data/matricula.json", encoding="utf-8") as f:
    estructura = json.load(f)

main_menu = estructura["main_menu"]
main_menu_submenus = estructura["main_menu_submenus"]
faq_respuestas = estructura["faq_respuestas"]

# Comando /matricula
async def matricula_command(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton(text=v, callback_data=f"mat-{k}")] for k, v in main_menu.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Seleccioná una categoría de matrícula:", reply_markup=reply_markup
    )
    context.user_data["current_menu_matricula"] = None

# Manejo del menú principal
async def handle_main_menu_matricula(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    selection = query.data.replace("mat-", "")

    if selection in main_menu:
        context.user_data["current_menu_matricula"] = selection
        submenu = main_menu_submenus.get(selection, {})
        keyboard = [
            [InlineKeyboardButton(text=v, callback_data=f"mat-{selection}{k}")]
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
async def handle_submenu_matricula(update: Update, context: CallbackContext):
    query = update.callback_query
    selection = query.data.replace("mat-", "")
    user_name = query.from_user.first_name

    menu_key = context.user_data.get("current_menu_matricula")
    response_key = selection

    if menu_key:
        respuesta = faq_respuestas.get(response_key)

        if respuesta:
            text = respuesta["text"].replace("{username}", user_name or "usuario")
            await query.edit_message_text(text, parse_mode="Markdown")
        else:
            await query.edit_message_text("No se encontró una respuesta para esta opción.")
    else:
        await query.edit_message_text("Por favor iniciá con /matricula.")

def get_handlers():
    return [
        CommandHandler("matricula", matricula_command),
        CallbackQueryHandler(handle_main_menu_matricula, pattern=r"^mat-[1-5]$"),
        CallbackQueryHandler(handle_submenu_matricula, pattern=r"^mat-[1-5][a-g]$")
    ]

