import smtplib
import socket
from email.message import EmailMessage
import os

def enviar_parte_pdf(remitente, password, destinatarios, ruta_pdf, fecha_str):
    if not remitente or not password or not destinatarios:
        return "Faltan configurar tus datos de correo o los destinatarios."
    
    try:
        msg = EmailMessage()
        msg['Subject'] = f'Parte Diario de Novedades - Seguridad Loreto ({fecha_str})'
        msg['From'] = remitente
        msg['To'] = ", ".join(destinatarios)
        msg.set_content(f"Buenos días,\n\nSe adjunta el parte de novedades del día {fecha_str}.\n\nUn saludo.")
        
        with open(ruta_pdf, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(ruta_pdf))
            
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=12) as smtp:
            smtp.login(remitente, password)
            smtp.send_message(msg)
        return "EXITO"

    except (socket.gaierror, TimeoutError):
        return "ERROR: No tienes conexión a Internet. Conéctate al Wi-Fi e inténtalo de nuevo."
    except smtplib.SMTPAuthenticationError:
        return "ERROR: La contraseña de aplicación de Google es incorrecta o ha caducado."
    except Exception as e:
        return f"ERROR INESPERADO: {str(e)}"