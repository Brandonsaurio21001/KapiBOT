# coding=utf-8
# -*- coding: utf-8 -*-

#----BOT TELEGRAM DE PPREGUNTAS FRECUENTES###
#----DESARROLLADO POR BRANDON BADILLA LEITÓN PARA EL DEPARTAMENTO DE ADMISIÓN Y REGISTRO 
#----INSTITUTO TECNOLÓGICO DE COSTA RICA

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
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
)
from handlers.expediente_handler import get_handlers as expediente_handlers
from handlers.guiashorarios_handler import get_handlers as guias_handlers
from handlers.admision_handler import get_handlers as admision_handlers
from handlers.matricula_handler import get_handlers as matricula_handlers
from handlers.otros_handler import get_handlers as otros_handlers

# Cargar el token desde el .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Falta el token en el archivo .env")

# Comando /start con mensaje informativo
async def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"Hola {user_name}, KapiBOT te da la bienvenida \n\n"
        "Estoy aquí para brindar asistencia con las dudas más frecuentes sobre los procesos institucionales del TEC.\n\n"
        "Podés iniciar dando clic en el comando que mejor se ajuste a tu necesidad.\n"
        "*Comandos disponibles:*\n"
        "• /start — Mensaje de bienvenida y explicación de comandos\n"
        "• /admision — Preguntas frecuentes sobre el proceso de admisión.\n"
        "• /guiashorarios — Consultas sobre el uso de la guía de horarios.\n"
        "• /matricula — Dudas comunes sobre el sistema de matrícula.\n"
        "• /expediente — Información relacionada al expediente estudiantil.\n"
        "• /otrostramites — Consultar otros trámites y servicios.\n\n"
        "Puedes consultar la lista de comandos en el menú de la parte inferior.\n",
        parse_mode="Markdown"
    )

# Handler para cualquier mensaje de texto que no sea un comando
async def handle_messages(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    response_text = (
        f"Hola {user_name}, mi configuración actual no me permite responder mensajes directamente.\n"
        "Si necesitás ayuda, usá uno de los comandos disponibles o contactá al área de Expedientes Estudiantiles: "
        "`expedientedigital@itcr.ac.cr`."
    )
    await update.message.reply_text(response_text, parse_mode="Markdown")



# Función principal
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # Handlers
    for handler in expediente_handlers():
        app.add_handler(handler)
    for handler in guias_handlers():
        app.add_handler(handler)
    for handler in admision_handlers():
        app.add_handler(handler)
    for handler in matricula_handlers():
        app.add_handler(handler) 
    for handler in otros_handlers():
        app.add_handler(handler)
    # Mensaje por defecto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    print("KapiBOT está corriendo... esperando interacciones.")
    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("KapiBOT detenido con Ctrl+C.")

if __name__ == "__main__":
    main()













