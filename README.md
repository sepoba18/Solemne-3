# 🚀 SpaceX Mission Dashboard

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Data-Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/Visualizaci%C3%B3n-Altair-FF6F00?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Altair" />
  <img src="https://img.shields.io/badge/API-SpaceX_v4-005288?style=for-the-badge&logo=spacex&logoColor=white" alt="SpaceX API" />
</p>

Dashboard analítico interactivo desarrollado en **Python** con **Streamlit** para la exploración, telemetría y análisis visual de las misiones y lanzamientos de SpaceX, consumiendo en tiempo real los endpoints de su API REST oficial (v4).

Proyecto desarrollado para la asignatura de **Programación**, Universidad San Sebastián (USS).

---

## 🛰️ Funcionalidades del Dashboard

- 📊 **Telemetría y Métricas en Tiempo Real:**
  - Consumo directo de la API de lanzamientos (`/launches`) y plataformas de despegue (`/launchpads`).
  - Caché de datos optimizado con `@st.cache_data` para cargas fluidas y eficientes.
- 🎯 **Filtros Dinámicos e Interactivos:**
  - Exploración por año, estado de la misión (éxito / fallo) y plataformas de despegue activas.
  - Mapeo mensual estandarizado para series temporales.
- 📈 **Visualizaciones con Altair:**
  - Gráficos interactivos de frecuencia de misiones, tasas de éxito y análisis cronológico de despegues.

---

## 📁 Estructura del Repositorio

```text
Solemne-3/
├── solemne3.py            # Aplicación principal del Dashboard en Streamlit
├── solemne3.ipynb         # Libreta Jupyter con análisis exploratorio de datos (EDA)
├── Informe Solemne 3.docx # Documentación e informe académico formal
└── README.md              # Documentación técnica del proyecto
```

---

## ⚡ Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/sepoba18/Solemne-3.git
cd Solemne-3
```

### 2. Instalar dependencias
```bash
pip install streamlit pandas requests altair
```

### 3. Iniciar la aplicación
```bash
python -m streamlit run solemne3.py
```

La aplicación se abrirá automáticamente en tu navegador web en `http://localhost:8501`.

---

## 👥 Autores
- **Sebastián Orellana** ([@sepoba18](https://github.com/sepoba18))
- **Vicente Araya**
- **Vicente Jiménez**

*Universidad San Sebastián (USS)*
