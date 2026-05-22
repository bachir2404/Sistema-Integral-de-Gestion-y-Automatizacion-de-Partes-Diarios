# Sistema Integral de Gestión y Automatización de Partes Diarios

## Descripción del Proyecto
Este proyecto resuelve la problemática de la gestión y distribución de partes de novedades diarios en entornos operativos mediante la automatización de procesos. El software extrae información de planificación desde cuadrantes mensuales en formato PDF, cumplimenta de forma dinámica un formulario PDF estandarizado, integra una interfaz de captura de firma manuscrita y automatiza la distribución del documento final a través del protocolo SMTP de forma segura y asíncrona.

Desarrollado como proyecto personal académico, distribuido en mi entorno laboral y enfocado en la optimización de procesos de administración y seguridad local.

## Características Clave
- **Extracción Automatizada de Datos (ETL):** Procesamiento automático de cuadrantes de guardias en formato PDF mediante `pdfplumber` para la detección y auto-completado del personal de servicio del día en curso.
- **Frontend Dinámico e Inclusivo:** Interfaz gráfica desarrollada con `CustomTkinter` estructurada mediante contenedores independientes de desplazamiento (`CTkScrollableFrame`) para garantizar la total accesibilidad y visualización en pantallas de baja resolución (ej. 1366x768).
- **Módulo de Firma Biométrica:** Captura interactiva de rúbricas mediante un lienzo (`Canvas`) integrado, rasterización con `Pillow` y fusión dinámica sobre el documento final usando `ReportLab`.
- **Persistencia de Datos Local:** Gestión de configuraciones, credenciales codificadas y bases de datos de personal mediante archivos estructurados en formato JSON.
- **Conectividad de Red Asíncrona:** Transmisión segura de correos electrónicos vía protocolo SMTP bajo TLS/SSL (`smtplib`), delegando el proceso de envío a un hilo de ejecución secundario (`threading`) para evitar el bloqueo del hilo principal de la interfaz (GUI).

## Arquitectura del Software
El sistema está modularizado bajo el principio de responsabilidad única:
- `interfaz.py`: Controlador principal de la interfaz gráfica de usuario (GUI) y flujos de ventanas secundarias.
- `config.py`: Gestor del ciclo de vida y lectura/escritura del archivo de configuración local `ajustes.json`.
- `generador_pdf.py`: Motor de manipulación de ficheros PDF, inyección de variables de formulario y superposición de capas gráficas (firmas).
- `enviador_correo.py`: Cliente de red para la autenticación y enrutamiento de correos electrónicos corporativos.

## Tecnologías Utilizadas
- **Lenguaje:** Python 3.10+
- **Librerías de Interfaz:** CustomTkinter, Tkinter
- **Procesamiento de PDF e Imágenes:** PyPDF, ReportLab, pdfplumber, Pillow
- **Protocolos y Redes:** SMTPLib, EmailMessage

## Requisitos e Instalación

1. Clonar el repositorio:
```bash
git clone [https://github.com/bachir2404/Sistema-Integral-de-Gestion-y-Automatizacion-de-Partes-Diarios.git](https://github.com/bachir2404/Sistema-Integral-de-Gestion-y-Automatizacion-de-Partes-Diarios.git)
cd Sistema-Integral-de-Gestion-y-Automatizacion-de-Partes-Diarios