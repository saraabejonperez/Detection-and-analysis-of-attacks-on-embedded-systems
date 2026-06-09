# Trabajo de Fin de Grado: Detección y análisis de ataques en sistemas embebidos

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)
![Flask](https://img.shields.io/badge/flask-backend-green.svg)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-orange.svg)

## Descripción del Proyecto

El objetivo principal de este proyecto es dotar a los dispositivos embebidos de la capacidad de identificar ataques de Denegación de Servicio volumétricos, específicamente *SYNFlood* e *ICMPFlood*, procesando el tráfico de red directamente en el propio dispositivo. Para ello, se emplea un modelo de clasificación binaria basado en el algoritmo **Random Forest**, ejecutado sobre un **M5Stack LLM630 Compute Kit (AX630C)**.

Además del módulo de inferencia en el *hardware*, el proyecto se complementa con una **plataforma web de gestión centralizada**. Esta herramienta cierra el ciclo de vida del sistema, permitiendo orquestar todo el ecosistema de seguridad de manera remota y eficiente.

## Características Principales

* **Detección *On-Edge*:** Procesamiento de paquetes y extracción de características en tiempo real utilizando `NFStream` directamente en el microcontrolador.
* **Despliegue Remoto:** Asignación y envío automático de los clasificadores de inteligencia artificial desde la nube al dispositivo físico.
* **Monitorización y Alertas:** Recepción instantánea de avisos en el panel de control ante la detección de intrusiones, junto con el análisis posterior de *logs* de tráfico.
* **Evaluación de Modelos:** Entorno integrado en la web para testear la precisión de los modelos con datos locales (matrices de confusión, métricas de rendimiento y gráficas).
* **Gestión de Recursos:** Sistema de cuentas de usuario y políticas automatizadas de almacenamiento (borrado automático de modelos tras 40 días de inactividad).

## Tecnologías Utilizadas

* **Hardware:** M5Stack LLM630 Compute Kit (AX630C)
* **Desarrollo y ML:** Python, Scikit-Learn, Pandas, NumPy
* **Análisis de Red:** NFStream
* **Desarrollo Web:** Flask (Backend)
* **Despliegue:** Docker

## Vídeo Demostrativo y Guía de Uso

Para facilitar la comprensión del ecosistema y la puesta en marcha del proyecto, se ha creado un **vídeo demostrativo** que sirve tanto como prueba de concepto del funcionamiento real del sistema, como de **guía funcional para el usuario**. 

Disponible en [este enlace](https://youtu.be/tLlbtdLFYio).

## Instalación y Despliegue

La plataforma web del proyecto está desarrollada para ser desplegada mediante contenedores, evitando conflictos de dependencias.

### Prerrequisitos
* Tener instalado [Docker](https://www.docker.com/) y Docker Compose en la máquina anfitriona.

### Pasos para levantar la plataforma web
1. Clona este repositorio en tu equipo local:
   ```bash
   git clone [https://github.com/saraabejonperez/Detection-and-analysis-of-attacks-on-embedded-systems.git]([https://github.com/tu-usuario/nombre-del-repositorio.git](https://github.com/saraabejonperez/Detection-and-analysis-of-attacks-on-embedded-systems.git))
   cd Detection-and-analysis-of-attacks-on-embedded-systems

2. Construye y levanta los contenedores en segundo plano:
   ```bash
   docker-compose up --build -d

3. Accede a la aplicación web a través del navegador web navegando a **http://{ip_ordenador}:5000**. 

### Autor
Este proyecto fue desarrollado por Sara Abejón Pérez como parte del Trabajo de Fin de Grado en la Universidad de Burgos.

### Tutores
- Jaime Andrés Rincón Arango
- Daniel Urda Muñoz

### Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.
