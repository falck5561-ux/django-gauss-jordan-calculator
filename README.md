## 🧮 Calculadora Gauss-Jordan & Inversa (Django/Python)

Este proyecto implementa una calculadora web que permite resolver sistemas de ecuaciones lineales mediante el método de **Eliminación de Gauss-Jordan** y calcular la **Matriz Inversa** ($\mathbf{A}^{-1}$).

La principal característica es que, en el modo Inversa, realiza la multiplicación automática $\mathbf{x} = \mathbf{A}^{-1}\mathbf{B}$ para demostrar que la solución es idéntica al método directo de Gauss-Jordan.

***

## 🚀 Inicio Rápido: Comandos de Instalación

Sigue estos pasos para **clonar**, **instalar dependencias** y **ejecutar** la aplicación localmente.

### 📋 Prerrequisitos

Necesitas **Python 3.x** y **pip**.

### Comandos Completos para Descarga y Ejecución

Copia y pega la siguiente secuencia de comandos en tu terminal. Recuerda que la URL y el nombre de la carpeta son específicos de tu proyecto.

```bash
# --- 1. DESCARGA Y CONFIGURACIÓN DEL ENTORNO ---
# Clonar el repositorio
git clone [https://github.com/falck5561-ux/django-gauss-jordan-calculator.git](https://github.com/falck5561-ux/django-gauss-jordan-calculator.git)

# Navegar a la carpeta del proyecto
cd django-gauss-jordan-calculator

# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual (Usar la línea correspondiente a tu SO: Windows o Linux/macOS)
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

# Instalar todas las librerías necesarias (Django, NumPy, Pandas, Openpyxl)
pip install django numpy pandas openpyxl


# --- 2. EJECUCIÓN Y ACCESO ---
# Iniciar el servidor de desarrollo de Django
python manage.py runserver

# Abre tu navegador web y navega a:
# [http://127.0.0.1:8000/](http://127.0.0.1:8000/)