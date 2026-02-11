# IoT-GPS-Tracker: Monitoreo en Tiempo Real 🚗🛰️

Este proyecto es un sistema de rastreo satelital de extremo a extremo (End-to-End). Utiliza el protocolo de comunicación de **Traccar Client** para convertir un smartphone en un seguidor GPS, procesa los datos mediante un servidor Python y los visualiza en un Dashboard web interactivo.

## 🚀 Características
- **Recepción de Datos IoT**: Servidor basado en Sockets que interpreta peticiones HTTP/JSON desde dispositivos móviles.
- **Base de Datos Relacional**: Almacenamiento normalizado en MySQL/MariaDB para asegurar la integridad de los datos.
- **Dashboard Web**: Interfaz construida con Flask y Leaflet.js para mapeo dinámico.
- **Filtrado Inteligente**: Algoritmo en Python para calcular velocidad, estado de movimiento y filtrado de ruido de señal GPS.
- **Acceso Remoto**: Configurado para operar mediante túneles con **Ngrok**.


## 🛠️ Stack Tecnológico
- **Backend:** Python (Flask, Sockets, MySQL Connector)
- **Frontend:** HTML5, CSS3 (Bootstrap), JavaScript (Leaflet.js)
- **Base de Datos:** MySQL / MariaDB
- **Herramientas:** Traccar Client (Android/iOS), Ngrok

## 📋 Requisitos
Para ejecutar este proyecto localmente, necesitarás:
- Python 3.8 o superior
- MySQL Server
- Ngrok (para exposición a internet)
- Traccar Client instalado en tu dispositivo móvil

## 🔧 Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
   cd nombre-del-repo
