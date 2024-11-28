##BOT TELEGRAM DE PPREGUNTAS FRECUENES###
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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, CallbackContext
)
from telegram.ext import MessageHandler, filters

# Cargar las variables del archivo .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TOKEN:
    raise ValueError("No se encontró el TOKEN en el archivo .env")

# Menús principales y submenús

#EL MAIN MENÚ REPRESENTA LOS MÓDULOS O APARTADOS SEGUN LO ESTABLECIMOS EN EL EXCEL
#1. CORRESPONDE A TODAS LAS POSIBLES PREGUNTA SPARA ESA PREGUNTA
#2. EXACTAMENTE LO MISMO Y ASI PARA 3 Y 4
main_menu = {
    "1": "Tengo problemas con mi cuenta @estudiantec",
    "2": "Dónde solicito una reposición de carné",
    "3": "Cambio de información de mi expediente estudiantil",
    "4": "Documentos de primer ingreso"
}

#EL SUBMENÚ ES LO QUE SE DESPLIEGA DE CADA MODULO, EJEMPLO, 1 DEL MAIN MENÚU DESPLIEGA EL SUBMENÚ 1 DE main_menu_submenus
#Las clavves a,b,c,d... son para generar un KEY unico de pregunta y matchearlo conn el key unico de respuestas en el faq respuestas
main_menu_submenus = {
    "1": {
        "a": "No sé cuál es mi cuenta @estudiantec.cr",
        "b": "Olvidé mi contraseña de mi cuenta @estudiantec.cr",
        "c": "No sé cuál es mi correo de recuperación (secundario)",
        "d": "Deseo cambiar mi correo de recuperación (secundario)",
        "e": "Cambiar número telefónico para códigos de verificación",
        "f": "No me llegan los códigos de verificación para ingresar a mi correo",
        "g": "Aparece otro número asociado a mi cuenta Microsoft"
    },
    "2": {
        "a": "Se me venció el carné",
        "b": "Perdí el carné",
        "c": "Deseo cambiar mi foto del carné",
        "d": "Nunca me dieron el carné",
        "e": "Deseo cancelar mi solicitud de reposición de carné"
    },
    "3": {
        "a": "Deseo renovar mi documento identificación TIM por la cédula nacional",
        "b": "Deseo actualizar mi DIMEX, DIDI, pasaporte. Vigente",
        "c": "Deseo renovar la foto de mi expediente estudiantil digital",
        "d": "Cambié mi dirección de residencia temporal o permanente",
        "e": "Cambié mi nombre o apellidos. ¿Dónde lo comunico para efectuar el cambio en sistemas?"
    },
    "4": {
        "a": "¿Qué características debe poseer la fotografía pasaporte?",
        "b": "Soy extranjero. ¿Qué documento de identificación presento?",
        "c": "Me gradué en el extranjero. Requisitos del diploma de Bachillerato en Educación Media",
        "d": "Poseo un Diploma de Bachillerato Internacional. Requisitos a presentar.",
        "e": "¿Quiénes deben presentar la Declaración Jurada para Menor de edad?"
    }
}


##ES EL DICCIONARIO DE RESPUESTAS
##CADA RESPONSE KEY QUE SE CONSTRUYÓ CON EL main_menu y el main_menu_submenu está registrado en este diccionario
##si se seleccionó del main menu 1 y del main submenú a. La response Key es 1a y así para cada uno.

###La llave text indica si la respuesta está compuesta únicamente por texto o media: inidica si lleva una imagen
##Si lleva una imagen, esta la extrae desde google drive ppor medio del id de imagen

faq_respuestas = {
    "1a": {
        "text": "Hola {username}, en este caso debes hacer solicitud al correo expedientedigital@itcr.ac.cr. Adjunta la cédula vigente por ambos lados."
    },
    "1b": {
        "text": "Hola {username}, lo que debes hacer es crear una contraseña temporal: [Video explicativo](https://www.youtube.com/watch?v=7txicJVjfMM )"
    },
    "1c": {
        "text": "Hola {username}, en este caso debes ingresar a Mi Cuenta TEC: [Consulte el siguiente link](https://aplics.tec.ac.cr/MiCuentaTEC/)"
    },
    "1d": {
        "text": "Hola {username}, en este caso debes ingresar a Mi Cuenta TEC: [Consulte el siguiente link](https://aplics.tec.ac.cr/MiCuentaTEC/)"
    },
    "1e": {
        "text": "Hola {username}, debes realizar solicitud al correo expedientedigital@itcr.ac.cr, adjuntando tu documento de identificación vigente por ambos lados."
    },
    "1f": {
        "text": "Hola {username}, verifica que el número de celular esté registrado en sistemas DAR al correo expedientedigital@itcr.ac.cr. "
                "Si el problema persiste, comunícate con: [Consulte el siguiente link](https://www.tec.ac.cr/gustavo-bolanos-solano)"
    },
    "1g": {
        "text": "Hola {username}, comunícate con: gbolanoss@tec.ac.cr. Edificio M-2, Campus Tecnológico Central Cartago."
    },
    "2a": {
        "text": "Hola {username}, para renovar un carné vencido, debes hacer solicitud vía web: [Consulte el siguiente link](https://www.tec.ac.cr/form/webform-26454)"
    },
    "2b": {
        "text": "Hola {username}, si perdiste tu carné, debes hacer solicitud vía web: [Consulte el siguiente link](https://www.tec.ac.cr/form/webform-26454)"
    },
    "2c": {
        "text": "Hola {username}, para cambiar la foto de tu carné, debes hacer solicitud vía web: [Consulte el siguiente link](https://www.tec.ac.cr/form/webform-26454)"
    },
    "2d": {
        "text": "Hola {username}, si nunca recibiste el carné, debes hacer solicitud vía web: [Consulte el siguiente link](https://www.tec.ac.cr/form/webform-26454)"
    },
    "2e": {
        "text": "Hola {username}, para cancelar tu solicitud de reposición de carné, envía la solicitud al correo expedientedigital@itcr.ac.cr. "
                "Adjunta la cédula vigente por ambos lados."
    },
    "3a": {
        "text": "Hola {username}, para renovar tu documento TIM por cédula nacional, debes enviar el documento vigente a expedientedigital@itcr.ac.cr."
    },
    "3b": {
        "text": "Hola {username}, si eres extranjero(a), debes hacer solicitud de renovación a expedientedigital@itcr.ac.cr, adjuntando "
                "el documento de identificación vigente o comprobante de solicitud de renovación."
    },
    "3c": {
        "text": "Hola {username}, debes enviar una fotografía formato pasaporte a expedientedigital@itcr.ac.cr con las siguientes características:\n"
                "a. Cara de frente y ojos abiertos.\n"
                "b. Sin gafas de sol, gorras o sombreros.\n"
                "c. Fondo liso, blanco o gris."
    },
    "3d": {
        "text": "Hola {username}, envía tu nueva dirección al correo expedientedigital@itcr.ac.cr. Incluye:\n"
                "a. País, provincia, cantón, distrito, y dirección exacta.\n"
                "b. Adjunta tu cédula vigente por ambos lados."
    },
    "3e": {
        "text": "Hola {username}, si cambiaste tu nombre o apellidos, comunícalo al correo expedientedigital@itcr.ac.cr. "
                "Adjunta la cédula vigente y la anterior por ambos lados."
    },
    "4a": {
        "text": "Hola {username}, puedes tomarte una foto con el celular con las siguientes características: aquí tienes un [video explicativo](https://www.youtube.com/watch?v=kox3VJSfErE) de ejemplo."
    },
    "4b": {
        "text": "Hola {username}, si eres extranjero(a), presenta uno de los siguientes documentos vigentes:\n"
                "- Pasaporte (hoja principal).\n"
                "- Documento de Identidad Migratoria para Extranjeros (DIMEX).\n"
                "- Documento de Identificación Diplomática (DIDI).\n"
                "Si usted tiene alguna situación especial comuníquese al correo electrónico expedientedigital@tec.ac.cr\n\n"
                "[Información de los documentos](https://www.tec.ac.cr/documentos-primer-ingreso#:~:text=Debes%20subir%20los%20documentos%20solicitados%20por%20el%20TEC)\n"
                "[Ver video explicativo](https://www.youtube.com/watch?v=HHWyzOelcpE&t=2s)\n"
    },
    "4c": {
        "text": "Hola {username}, si obtuviste el título de secundaria en el extranjero, presenta:\n"
                "1. Diploma autenticado o apostillado por el Ministerio de Relaciones Exteriores y Culto de Costa Rica.\n"
                "2. Resolución de equiparación o reconocimiento con el título de Bachiller en Educación Media\n"
                "otorgado por la República de Costa Rica emitida por la Dirección de Gestión y Evaluación de la Calidad del Ministerio de Educación Pública (MEP)\n"
                "Para más información diríjase a la Dirección de Gestión y Evaluación de la Calidad Avenida 3, calle 40, San José, Paseo Colón, del Banco de Costa Rica 75 metros al norte\n\n"
                "[Información de documentos](https://www.tec.ac.cr/documentos-primer-ingreso#:~:text=Debes%20subir%20los%20documentos%20solicitados%20por%20el%20TEC)\n"
                "[Ver video explicativo](https://www.youtube.com/watch?v=HHWyzOelcpE&t=2s)\n"
    },
    "4d": {
        "text": "Hola {username}, si tienes un Diploma de Bachillerato Internacional, presenta:\n"
                "1. Diploma de Bachillerato Internacional y resolución de equiparación o reconocimiento con el título de Bachiller en Educación Media\n"
                "otorgado por la República de Costa Rica, emitida por la Dirección de Gestión y Evaluación de la Calidad del Ministerio de Educación Pública (MEP).\n"
                "2. Si no tienes aún el diploma, solicita una certificación de tu colegio que indique cumplimiento con "
                "los artículos 6 y 10 del Decreto Ejecutivo No. 40956-MEP.\n\n"
                "[Información de documentos](https://www.tec.ac.cr/documentos-primer-ingreso#:~:text=Debes%20subir%20los%20documentos%20solicitados%20por%20el%20TEC)\n"
                "[Ver video explicativo](https://www.youtube.com/watch?v=HHWyzOelcpE&t=2s)\n"
    },
    "4e": {
        "text": "Hola {username}, aquí tienes un video explicativo:" 
                "[Ver video](https://youtu.be/uATwLF8PPrE?si=7exgBfwPlDtoyN8C)\n"
                "[Descarga la Declaración Jurada aquí](https://www.tec.ac.cr/sites/default/files/media/doc/declaracion_jurada_para_derecho_de_matricula_en_menores_de_edad-1.pdf)\n"
    }
}



##esta e sla configuración del comando start que lo que hace es saludar y presentar el main menu por medio de botones

async def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    keyboard = [[InlineKeyboardButton(v, callback_data=k)] for k, v in main_menu.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Hola {user_name}, bienvenido al apartado de preguntas frecuentes del área de expedientes estudiantiles. "
        "Por favor, selecciona una opción del menú:",
        reply_markup=reply_markup
    )
    context.user_data['current_menu'] = None


###Este es el get de la seleccion del main menu donde se construye el primer valor de la responde key (1,2,3,4)
async def handle_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    selection = query.data

    if selection in main_menu:
        context.user_data['current_menu'] = selection
        submenu = main_menu_submenus.get(selection, {})
        keyboard = [[InlineKeyboardButton(v, callback_data=f"{selection}{k}")] for k, v in submenu.items()]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(f"Seleccionaste: {main_menu[selection]}\n\nElige una opción:", reply_markup=reply_markup)
    else:
        await query.edit_message_text("Opción no válida. Por favor, selecciona del menú principal.")

##misma logica para escoger la letra del submenu (a,b,c,d,e..)
async def handle_submenu(update: Update, context: CallbackContext):
    query = update.callback_query
    selection = query.data
    user_name = query.from_user.first_name

    if context.user_data.get('current_menu'):
        response_key = selection

        if response_key in faq_respuestas:
            response = faq_respuestas[response_key]
            # Enviar el mensaje con el parse_mode="Markdown" para interpretar los enlaces
            await query.message.reply_text(response['text'].format(username=user_name), parse_mode="Markdown")

            # Verificar si hay contenido multimedia
            if response.get('media'):
                media_url = response['media']
                if media_url.endswith(('.jpg', '.jpeg', '.png')):
                    await query.message.reply_photo(media_url)
                elif media_url.endswith('.pdf'):
                    await query.message.reply_document(media_url)
                else:
                    await query.message.reply_video(media_url)
        else:
            await query.message.reply_text("Opción no válida.")
    else:
        await query.message.reply_text("Por favor, selecciona una opción del menú principal primero. (/start)")



# Función para manejar cualquier mensaje que no sea un comando
async def handle_messages(update, context):
    user_name = update.message.from_user.first_name
    
    # Si el mensaje no es un comando (no empieza con '/')
    if update.message.text and not update.message.text.startswith('/'):
        response_text = (
            f"Hola {user_name}, mi configuración actual no me permite responder mensajes directamente. "
            "Si necesitas ayuda, puedes ponerte en contacto con el área de Expedientes Estudiantiles al siguiente correo: "
            "expedientedigital@itcr.ac.cr."
        )
        await update.message.reply_text(response_text)


# Función de manejo de errores
async def error_handler(update, context):
    print(f"Ocurrió un error: {context.error}")
    if update:
        await update.message.reply_text("Hubo un problema. Por favor, intenta de nuevo más tarde.")


# Construcción del bot a través del token
def main():
    application = Application.builder().token(TOKEN).build()

    # Agregar los handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern='^[1234]$'))
    application.add_handler(CallbackQueryHandler(handle_submenu, pattern='^[1-4][a-g]$'))
    application.add_error_handler(error_handler)

    # Filtro de mensajes de texto que no sean comandos
    application.add_handler(MessageHandler(filters.TEXT, handle_messages))

    # Mostrar mensaje de estado
    print("El bot está corriendo. Esperando mensajes...")
    application.run_polling()

if __name__ == '__main__':
    main()



