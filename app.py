# import streamlit as st
# import streamlit.components.v1 as components
# import json
# import time
# import numpy as np
# from datetime import datetime
# from pathlib import Path

# from src.causal_engine import apply_guardrails, find_dominant_cause
# from src.llm_agent import get_ai_decision, strategy_to_fan
# import websocket
# import threading

# # ─────────────────────────────────────────────
# # КОНСТАНТЫ
# # ─────────────────────────────────────────────
# CAUSAL_WEIGHTS = {
#     'ate_cool_A': -0.03540,
#     'ate_power':   0.20071,
#     'ate_load':    0.06565,
#     'ate_weather': 0.14649,
# }
# TARGET_TEMP = 22.0

# # ─────────────────────────────────────────────
# # КОНФИГУРАЦИЯ
# # ─────────────────────────────────────────────
# st.set_page_config(layout="wide", page_title="Causal Digital Twin")
# st.markdown("""
# <style>
# .main { background-color: #050505; color: white; }
# .stMetric { background-color: #111; padding: 15px;
#             border-radius: 10px; border: 1px solid #333; }
# [data-testid="stSidebar"] { background-color: #0f0f0f; }
# </style>
# """, unsafe_allow_html=True)

# st.title("🤖 Causal AI: Адаптивный Цифровой Двойник ЦОД")

# # ─────────────────────────────────────────────
# # SESSION STATE
# # ─────────────────────────────────────────────
# if "sim_data" not in st.session_state:
#     st.session_state.sim_data = {
#         "temp":          TARGET_TEMP,
#         "fan":           40.0,
#         "last_temp":     TARGET_TEMP,
#         "last_llm_call": 0.0,
#         "strategy":      "balanced",
#         "reasoning":     "Система готова. Активируйте автономный режим.",
#     }

# # ─────────────────────────────────────────────
# # САЙДБАР
# # ─────────────────────────────────────────────
# with st.sidebar:
#     st.header("⚙️ Управление")
#     t_out         = st.slider("Температура на улице (°C)", 10.0, 45.0, 25.0)
#     load          = st.slider("Нагрузка серверов (кВт)",   20.0, 100.0, 50.0)
    
#     st.divider()
#     api_key       = st.text_input("OpenAI API Key", type="password")
#     is_autonomous = st.toggle("🚀 АВТОНОМНЫЙ РЕЖИМ", value=False)
#     update_speed  = st.slider("Скорость обновления (сек)", 0.5, 3.0, 1.0)
#     st.divider()
#     if st.button("🔄 Сброс системы"):
#         st.session_state.sim_data["temp"] = TARGET_TEMP
#         st.session_state.sim_data["fan"]  = 40.0
#         st.rerun()

# # ─────────────────────────────────────────────
# # ОСНОВНОЙ ИНТЕРФЕЙС
# # ─────────────────────────────────────────────
# col_left, col_right = st.columns([2, 1])

# with col_left:
#     st.subheader("🌐 Мониторинг 3D")
#     try:
#         with open("static/index.html", "r", encoding="utf-8") as f:
#             html_content = f.read()
#         components.html(html_content, height=500)
#     except FileNotFoundError:
#         st.warning("3D модель не найдена в папке /static")

# with col_right:
#     st.subheader("🧠 Causal AI Монитор")
#     metrics_area  = st.empty()
#     cause_area    = st.empty()
#     strategy_area = st.empty()

# # ─────────────────────────────────────────────
# # ФИЗИКА
# # ─────────────────────────────────────────────
# curr_temp = st.session_state.sim_data["temp"]
# curr_fan  = st.session_state.sim_data["fan"]

# eq_temp   = (15.0
#              + load  * CAUSAL_WEIGHTS['ate_load']
#              + t_out * CAUSAL_WEIGHTS['ate_weather']
#              + curr_fan * CAUSAL_WEIGHTS['ate_cool_A'])
# new_temp   = 0.92 * curr_temp + 0.08 * eq_temp + np.random.normal(0, 0.03)
# power_cool = 10.0 + curr_fan * CAUSAL_WEIGHTS['ate_power']
# pue        = (load + power_cool + 20.0) / load

# st.session_state.sim_data["temp"] = new_temp

# dominant_cause, contributions = find_dominant_cause(
#     t_out, load, curr_fan, CAUSAL_WEIGHTS)

# # ─────────────────────────────────────────────
# # GUARDRAILS + LLM
# # ─────────────────────────────────────────────
# if is_autonomous:
#     final_fan, exp_temp, exp_power, max_power = apply_guardrails(
#         new_temp, curr_fan, load)

#     curr_time      = time.time()
#     temp_trend     = new_temp - st.session_state.sim_data["last_temp"]
#     time_since_llm = curr_time - st.session_state.sim_data["last_llm_call"]

#     if api_key and (time_since_llm > 30 or abs(temp_trend) > 2.0):
#         decision = get_ai_decision(
#             api_key,
#             current_temp=new_temp,
#             target_temp=TARGET_TEMP,
#             server_load=load,
#             current_fan=curr_fan,
#             temp_trend=temp_trend,
#             ate_temp=CAUSAL_WEIGHTS['ate_cool_A'],
#             dominant_cause=dominant_cause,
#             contributions=contributions,
#         )
#         strategy  = decision["strategy"]
#         reasoning = decision["reasoning"]
#         final_fan_adj = strategy_to_fan(strategy, curr_fan, final_fan)

#         st.session_state.sim_data.update({
#             "fan":           final_fan_adj,
#             "strategy":      strategy,
#             "reasoning":     reasoning,
#             "last_llm_call": curr_time,
#             "last_temp":     new_temp,
#         })
#     else:
#         st.session_state.sim_data["fan"] = final_fan

# # ─────────────────────────────────────────────
# # STATE.JSON ДЛЯ 3D
# # ─────────────────────────────────────────────
# with open("state.json", "w") as f:
#     json.dump({
#         "server_load": round(load, 1),
#         "fan_speed":   round(float(st.session_state.sim_data["fan"]), 1),
#         "rack_temp":   round(new_temp, 1),
#         "t_out":       round(t_out, 1),
#     }, f)

# # ─────────────────────────────────────────────
# # ОБНОВЛЕНИЕ UI
# # ─────────────────────────────────────────────
# with metrics_area.container():
#     m1, m2, m3, m4 = st.columns(4)
#     m1.metric("Температура", f"{new_temp:.1f} °C",
#                       delta=f"{new_temp - TARGET_TEMP:.1f}",
#                       delta_color="inverse")
#     m2.metric("PUE", f"{pue:.2f}")
#     m3.metric("Обдув", f"{st.session_state.sim_data['fan']:.1f}%")
#     m4.metric("Мощность", f"{load + power_cool + 20:.0f} кВт")

# with cause_area.container():
#     c_icons = {
#         "Нагрузка серверов":       "💻",
#         "Уличная температура":     "🌡️",
#         "Охлаждение (вентилятор)": "🌀",
#     }
#     ci = c_icons.get(dominant_cause, "⚠️")
#     st.caption(f"{ci} Доминантная причина: **{dominant_cause}**")

# with strategy_area.container():
#     strat = st.session_state.sim_data.get("strategy", "—")
#     s_icons = {
#         "aggressive_cool": "🔴",
#         "balanced":        "🟡",
#         "energy_save":     "🟢",
#         "hold":            "⚪",
#     }
#     si = s_icons.get(strat, "⚪")
#     if is_autonomous:
#         st.info(f"{si} **Стратегия: {strat}**\n\n"
#                 f"{st.session_state.sim_data['reasoning']}")
#     else:
#         st.info("Включите автономный режим для запуска LLM-агента.")

#     if new_temp > 35:
#         st.error("🚨 Перегрев! Температура критически высокая.")
#     elif new_temp < TARGET_TEMP - 2:
#         st.warning("❄️ Переохлаждение — снизьте обороты.")

# # ─────────────────────────────────────────────
# # ЦИКЛ ОБНОВЛЕНИЯ
# # ─────────────────────────────────────────────
# if is_autonomous:
#     time.sleep(update_speed)
#     st.rerun()

import streamlit as st
import streamlit.components.v1 as components
import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path

from src.causal_engine import apply_guardrails, find_dominant_cause
from src.llm_agent import get_ai_decision, strategy_to_fan

# ─────────────────────────────────────────────
# КОНСТАНТЫ
# ─────────────────────────────────────────────
CAUSAL_WEIGHTS = {
    'ate_cool_A': -0.03540,
    'ate_power':   0.20071,
    'ate_load':    0.06565,
    'ate_weather': 0.14649,
}
TARGET_TEMP = 22.0

# ─────────────────────────────────────────────
# КОНФИГУРАЦИЯ
# ─────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="Causal Digital Twin")
st.markdown("""
<style>
.main { background-color: #050505; color: white; }
.stMetric { background-color: #111; padding: 15px;
            border-radius: 10px; border: 1px solid #333; }
[data-testid="stSidebar"] { background-color: #0f0f0f; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Causal AI: Адаптивный Цифровой Двойник ЦОД")

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "sim_data" not in st.session_state:
    st.session_state.sim_data = {
        "temp":          TARGET_TEMP,
        "fan":           40.0,
        "last_temp":     TARGET_TEMP,
        "last_llm_call": 0.0,
        "strategy":      "balanced",
        "reasoning":     "Система готова. Активируйте автономный режим.",
    }

# ─────────────────────────────────────────────
# САЙДБАР
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Управление")
    t_out         = st.slider("Температура на улице (°C)", 10.0, 45.0, 25.0)
    load          = st.slider("Нагрузка серверов (кВт)",   20.0, 100.0, 50.0)

    st.divider()
    api_key       = st.text_input("OpenAI API Key", type="password")
    is_autonomous = st.toggle("🚀 АВТОНОМНЫЙ РЕЖИМ", value=False)
    update_speed  = st.slider("Скорость обновления (сек)", 0.5, 3.0, 1.0)

    st.divider()
    if st.button("🔄 Сброс системы"):
        st.session_state.sim_data["temp"] = TARGET_TEMP
        st.session_state.sim_data["fan"]  = 40.0
        st.rerun()

    # ─────────────────────────────────────────
    # COUNTERFACTUAL ПАНЕЛЬ "ЧТО ЕСЛИ?"
    # ─────────────────────────────────────────
    st.divider()
    st.subheader("🔮 Что если?")
    st.caption("Прогноз do(X) без изменения реальной системы")

    hyp_load = st.slider(
        "Гипотетическая нагрузка (кВт)", 20.0, 100.0, load,
        key="hyp_load"
    )
    hyp_tout = st.slider(
        "Гипотетическая улица (°C)", 10.0, 45.0, t_out,
        key="hyp_tout"
    )

    # do-calculus: считаем прогноз при do(load=hyp_load, t_out=hyp_tout)
    # Вентилятор берём текущий — меняем только входные условия
    curr_fan_cf = st.session_state.sim_data["fan"]
    curr_temp_cf = st.session_state.sim_data["temp"]

    hyp_eq  = (15.0
               + hyp_load * CAUSAL_WEIGHTS['ate_load']
               + hyp_tout * CAUSAL_WEIGHTS['ate_weather']
               + curr_fan_cf * CAUSAL_WEIGHTS['ate_cool_A'])
    hyp_temp = round(0.92 * curr_temp_cf + 0.08 * hyp_eq, 1)
    hyp_pwr  = round(hyp_load + (10.0 + curr_fan_cf * CAUSAL_WEIGHTS['ate_power']) + 20.0, 1)
    hyp_pue  = round(hyp_pwr / hyp_load, 3) if hyp_load > 0 else 0

    cf1, cf2 = st.columns(2)
    cf1.metric(
        "Прогноз темп.",
        f"{hyp_temp:.1f} °C",
        delta=f"{hyp_temp - TARGET_TEMP:.1f}",
        delta_color="inverse"
    )
    cf2.metric(
        "Прогноз мощн.",
        f"{hyp_pwr:.0f} кВт",
        delta=f"{hyp_pwr - (load + (10.0 + curr_fan_cf * CAUSAL_WEIGHTS['ate_power']) + 20.0):.1f}",
    )
    st.metric("Прогноз PUE", f"{hyp_pue:.3f}")

    # Предупреждение если гипотетический сценарий опасен
    if hyp_temp > 35:
        st.error("⚠️ При таких условиях — перегрев!")
    elif hyp_temp > TARGET_TEMP + 3:
        st.warning("⚠️ Температура выйдет за допустимый предел")
    else:
        st.success("✅ Условия в норме")

# ─────────────────────────────────────────────
# ОСНОВНОЙ ИНТЕРФЕЙС
# ─────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🌐 Мониторинг 3D")
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=500)
    except FileNotFoundError:
        st.warning("3D модель не найдена в папке /static")

with col_right:
    st.subheader("🧠 Causal AI Монитор")
    metrics_area  = st.empty()
    cause_area    = st.empty()
    strategy_area = st.empty()

# ─────────────────────────────────────────────
# ФИЗИКА
# ─────────────────────────────────────────────
curr_temp = st.session_state.sim_data["temp"]
curr_fan  = st.session_state.sim_data["fan"]

eq_temp   = (15.0
             + load  * CAUSAL_WEIGHTS['ate_load']
             + t_out * CAUSAL_WEIGHTS['ate_weather']
             + curr_fan * CAUSAL_WEIGHTS['ate_cool_A'])
new_temp   = 0.92 * curr_temp + 0.08 * eq_temp + np.random.normal(0, 0.03)
power_cool = 10.0 + curr_fan * CAUSAL_WEIGHTS['ate_power']
pue        = (load + power_cool + 20.0) / load

st.session_state.sim_data["temp"] = new_temp

dominant_cause, contributions = find_dominant_cause(
    t_out, load, curr_fan, CAUSAL_WEIGHTS)

# ─────────────────────────────────────────────
# GUARDRAILS + LLM
# ─────────────────────────────────────────────
if is_autonomous:
    final_fan, exp_temp, exp_power, max_power = apply_guardrails(
        new_temp, curr_fan, load)

    curr_time      = time.time()
    temp_trend     = new_temp - st.session_state.sim_data["last_temp"]
    time_since_llm = curr_time - st.session_state.sim_data["last_llm_call"]

    if api_key and (time_since_llm > 30 or abs(temp_trend) > 2.0):
        decision = get_ai_decision(
            api_key,
            current_temp=new_temp,
            target_temp=TARGET_TEMP,
            server_load=load,
            current_fan=curr_fan,
            temp_trend=temp_trend,
            ate_temp=CAUSAL_WEIGHTS['ate_cool_A'],
            dominant_cause=dominant_cause,
            contributions=contributions,
        )
        strategy  = decision["strategy"]
        reasoning = decision["reasoning"]
        final_fan_adj = strategy_to_fan(strategy, curr_fan, final_fan)

        st.session_state.sim_data.update({
            "fan":           final_fan_adj,
            "strategy":      strategy,
            "reasoning":     reasoning,
            "last_llm_call": curr_time,
            "last_temp":     new_temp,
        })
    else:
        st.session_state.sim_data["fan"] = final_fan

# ─────────────────────────────────────────────
# STATE.JSON ДЛЯ 3D
# ─────────────────────────────────────────────
with open("state.json", "w") as f:
    json.dump({
        "server_load": round(load, 1),
        "fan_speed":   round(float(st.session_state.sim_data["fan"]), 1),
        "rack_temp":   round(new_temp, 1),
        "t_out":       round(t_out, 1),
    }, f)

# ─────────────────────────────────────────────
# ОБНОВЛЕНИЕ UI
# ─────────────────────────────────────────────
with metrics_area.container():
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Температура", f"{new_temp:.1f} °C",
              delta=f"{new_temp - TARGET_TEMP:.1f}",
              delta_color="inverse")
    m2.metric("PUE", f"{pue:.2f}")
    m3.metric("Обдув", f"{st.session_state.sim_data['fan']:.1f}%")
    m4.metric("Мощность", f"{load + power_cool + 20:.0f} кВт")

with cause_area.container():
    c_icons = {
        "Нагрузка серверов":       "💻",
        "Уличная температура":     "🌡️",
        "Охлаждение (вентилятор)": "🌀",
    }
    ci = c_icons.get(dominant_cause, "⚠️")
    st.caption(f"{ci} Доминантная причина: **{dominant_cause}**")

with strategy_area.container():
    strat = st.session_state.sim_data.get("strategy", "—")
    s_icons = {
        "aggressive_cool": "🔴",
        "balanced":        "🟡",
        "energy_save":     "🟢",
        "hold":            "⚪",
    }
    si = s_icons.get(strat, "⚪")
    if is_autonomous:
        st.info(f"{si} **Стратегия: {strat}**\n\n"
                f"{st.session_state.sim_data['reasoning']}")
    else:
        st.info("Включите автономный режим для запуска LLM-агента.")

    if new_temp > 35:
        st.error("🚨 Перегрев! Температура критически высокая.")
    elif new_temp < TARGET_TEMP - 2:
        st.warning("❄️ Переохлаждение — снизьте обороты.")

# ─────────────────────────────────────────────
# ЦИКЛ ОБНОВЛЕНИЯ
# ─────────────────────────────────────────────
if is_autonomous:
    time.sleep(update_speed)
    st.rerun()
