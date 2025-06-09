# coding=utf-8
# -*- coding: utf-8 -*-

##BOT TELEGRAM DE PPREGUNTAS FRECUENTES###
###DESARROLLADO POR BRANDON BADILLA LEITÓN PARA EL ÁREA DE EXPEDIENTES ESTUDIANTILES
###DEL INSTITUTO TECNOLÓGICO DE COSTA RICA



###MODULO 1 IMPORTACIONES Y DEPENDENCIAS
"""
Para que el bot funcione correctamente es necesario tener instaladas las siguientes librerías:

python-telegram-bot: Es la biblioteca principal que permite interactuar con la API de Telegram, facilitando la creación de bots que responden a mensajes y eventos.
python-dotenv: Se usa para cargar variables de entorno desde un archivo .env, manteniendo seguros datos sensibles como el token del bot.
para efectos de seguridad del bot el token se encuentra en un archivo .env

para instalar las librerías, en cmd:
pip install python-telegram-bot python-dotenv

"""

import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
)
from handlers.admision_handler import get_handlers as admision_handlers
from handlers.guiashorarios_handler import get_handlers as guias_handlers
from handlers.matricula_handler import get_handlers as matricula_handlers
from handlers.expediente_handler import get_handlers as expediente_handlers
from telegram.ext import MessageHandler, filters
# Cargar token desde .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Falta el token en el archivo .env")

# Comando /start con mensaje informativo
async def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"Hola {user_name}, KapiBOT te da la bienvenida \n\n"
        "Estoy aquí para ayudarte con las dudas más frecuentes sobre los procesos institucionales del TEC.\n\n"
        "*Comandos disponibles:*\n"
        "• /start — Mensaje de bienvenida y explicación de comandos\n"
        "• /admision — Preguntas frecuentes sobre el proceso de admisión.\n"
        "• /guiashorarios — Consultas sobre el uso de la guía de horarios.\n"
        "• /matricula — Dudas comunes sobre el sistema de matrícula.\n"
        "• /expediente — Información relacionada al expediente estudiantil.\n\n"
        "Puedes consultar la lista de comandos en el menú de la parte inferior.\n"
        "_Desarrollado por: Ing. Brandon Badilla Leitón_",
        parse_mode="Markdown"
    )

# Handler para cualquier mensaje de texto no comando
async def handle_messages(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    response_text = (
        f"Hola {user_name}, mi configuración actual no me permite responder mensajes directamente.\n"
        "Si necesitás ayuda, usá uno de los comandos disponibles o contactá al área de Expedientes Estudiantiles: "
        "`expedientedigital@itcr.ac.cr`."
    )
    await update.message.reply_text(response_text, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Comando de bienvenida
    app.add_handler(CommandHandler("start", start))

    # Handlers por módulo
    for handler in admision_handlers():
        app.add_handler(handler)

    for handler in guias_handlers():
        app.add_handler(handler)

    for handler in matricula_handlers():
        app.add_handler(handler)

    for handler in expediente_handlers():
        app.add_handler(handler)

    app.add_handler(MessageHandler(filters.TEXT, handle_messages))

    print("KapiBOT está corriendo... esperando interacciones.")
    app.run_polling()

if __name__ == "__main__":
    main()