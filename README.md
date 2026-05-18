# 🤖 Causal AI: Автономный адаптивный Цифровой Двойник ЦОД

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://causal-digital-twin.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Этот проект представляет собой **киберфизическую систему**, которая использует **Causal AI** (причинно-следственный ИИ) и **LLM** (языковые модели) для автономной оптимизации систем охлаждения центров обработки данных (ЦОД).

## 🌟 Ключевые особенности

* **🌐 3D Digital Twin:** Реализованная на Three.js визуализация серверной стойки в реальном времени.
* **🧠 Causal Engine:** Использование направленных ациклических графов (DAG) и расчета ATE (Average Treatment Effect) для понимания физики теплообмена.
* **🤖 LLM Agent:** Автономное принятие решений на базе OpenAI API с генерацией текстовых обоснований действий.
* **📊 Live Analytics:** Сравнение текущей эффективности с традиционными системами (Baseline) и расчет экономии энергии в реальном времени.
* **⚡ In-Memory WebSockets:** Мгновенная синхронизация данных между физическим движком на Python и 3D-сценой в браузере.

## 🛠 Технологический стек

* **Frontend:** Streamlit, Three.js (WebGL), HTML/CSS.
* **Backend:** Python 3.x, WebSockets (FastAPI-style routing).
* **AI/ML:** Causal Inference (DAG), OpenAI GPT-4.
* **Data:** Pandas, Numpy, Matplotlib (для аналитики PUE).

## 📂 Структура проекта

```text
├── data/
│   └── history.csv        # Логирование сессий и метрики эффективности
├── src/
│   ├── causal_engine.py   # Расчет доминантных причин и Guardrails
│   └── llm_agent.py       # Логика взаимодействия с ИИ
├── static/
│   ├── assets/            # 3D модели серверов (GLB/GLTF)
│   ├── index.html         # Сцена Three.js
│   └── script.js          # Логика WebSocket-клиента и рендеринга
├── app.py                 # Главное приложение (Streamlit Dashboard)
├── ws_server.py           # Высокопроизводительный WebSocket-роутер
├── requirements.txt       # Список зависимостей
└── .gitignore             # Исключения для Git