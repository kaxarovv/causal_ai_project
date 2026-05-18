# import json
# from openai import OpenAI

# def get_ai_decision(api_key, final_fan, exp_temp, exp_power, max_power, target_temp):
#     client = OpenAI(api_key=api_key)
    
#     status = "Оптимально" if abs(exp_temp - target_temp) < 0.5 else "Достигнут лимит инфраструктуры!"
    
#     prompt = f"""
#     Система Causal AI рассчитала безопасные параметры:
#     - Скорость вентиляторов: {final_fan:.1f}%
#     - Ожидаемая температура: {exp_temp:.1f}°C
#     - Энергопотребление: {exp_power:.1f} кВт (Лимит: {max_power} кВт)
#     Статус: {status}
    
#     Верни JSON объект: "new_fan_speed" (число), "expected_temp" (число), "reasoning" (строка, объясни ситуацию оператору как профи).
#     """
    
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Ты автономный контроллер ЦОД. Отвечай только в JSON."},
#             {"role": "user", "content": prompt}
#         ],
#         response_format={ "type": "json_object" }
#     )
    
#     return json.loads(response.choices[0].message.content)

# import json
# from openai import OpenAI

# def get_ai_decision(api_key, final_fan, exp_temp, exp_power, max_power, target_temp, t_out, causal_weights):
#     client = OpenAI(api_key=api_key)
    
#     diff = exp_temp - target_temp
#     direction = "ПЕРЕГРЕВ" if diff > 0.5 else ("ПЕРЕОХЛАЖДЕНИЕ" if diff < -0.5 else "СТАБИЛЬНО")

#     # Формируем промпт так, чтобы ИИ не мог ошибиться в ключах
#     prompt = f"""
#     СОСТОЯНИЕ: {direction} (Разница: {diff:.1f}°C)
#     Улица: {t_out:.1f}°C | Стойка: {exp_temp:.1f}°C | Цель: {target_temp}°C
#     Система: {final_fan:.1f}% обдува, {exp_power:.1f}/{max_power} кВт.

#     ЗАДАЧА:
#     Верни JSON с полями:
#     1. "new_fan_speed": число (твое решение по скорости).
#     2. "reasoning": строка (отчет до 25 слов). 
#        Структура отчета: ПРИЧИНА: ... ДЕЙСТВИЕ: ... ПРОГНОЗ: ...
#     """
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "Ты диспетчер ЦОД. Отвечай только в формате JSON. Поле new_fan_speed обязательно."},
#                 {"role": "user", "content": prompt}
#             ],
#             response_format={ "type": "json_object" }
#         )
#         return json.loads(response.choices[0].message.content)
#     except Exception as e:
#         # Если OpenAI упал, возвращаем структуру, которую поймет app.py
#         return {
#             "new_fan_speed": final_fan, 
#             "reasoning": f"Ошибка связи с ИИ: {str(e)}"
        # }

import json
from openai import OpenAI

VALID_STRATEGIES = {"aggressive_cool", "balanced", "energy_save", "hold"}

def get_ai_decision(api_key, current_temp, target_temp,
                    server_load, current_fan, temp_trend, ate_temp,
                    dominant_cause, contributions):
    """
    LLM выбирает СТРАТЕГИЮ (слово), не число.
    Математику делает causal_engine.py
    """
        # Форматируем вклады для промпта
    contrib_text = "\n".join(
        f"  - {k}: {v:.3f} вклад в температуру"
        for k, v in sorted(contributions.items(),
                           key=lambda x: x[1], reverse=True)
    )

    client = OpenAI(api_key=api_key)

    prompt = f"""Ты — стратег системы охлаждения дата-центра.

ТЕКУЩАЯ СИТУАЦИЯ:
- Температура стойки: {current_temp:.1f}°C (цель: {target_temp}°C)
- Отклонение: {current_temp - target_temp:+.1f}°C
- Тренд: {"↑ растёт" if temp_trend > 0.1 else "↓ снижается" if temp_trend < -0.1 else "→ стабильна"}
- Нагрузка серверов: {server_load:.0f}%
- Текущие обороты: {current_fan:.0f}%

КАУЗАЛЬНЫЙ АНАЛИЗ (вклад факторов):
{contrib_text}
⚠ Доминантная причина: {dominant_cause}

ДОСТУПНЫЕ СТРАТЕГИИ:
- "aggressive_cool"  → форсированное охлаждение
- "balanced"         → баланс температуры и энергии
- "energy_save"      → экономия энергии
- "hold"             → ничего не менять

Верни ТОЛЬКО JSON:
{{"strategy": "название", "reasoning": "Объясни оператору причину и решение. Обязательно упомяни {dominant_cause} как главный фактор."}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        decision = json.loads(response.choices[0].message.content)

        # Валидация — если LLM вернула мусор, используем fallback
        if decision.get("strategy") not in VALID_STRATEGIES:
            return {
                "strategy": "balanced",
                "reasoning": "Fallback: LLM вернула неизвестную стратегию. Применён режим по умолчанию."
            }
        return decision

    except json.JSONDecodeError:
        return {
            "strategy": "hold",
            "reasoning": "Fallback: ошибка парсинга ответа LLM. Параметры заморожены."
        }
    except Exception as e:
        return {
            "strategy": "hold",
            "reasoning": f"Fallback: LLM недоступна. Система работает автономно."
        }


def strategy_to_fan(strategy: str, current_fan: float, causal_fan: float) -> float:
    """Переводит стратегию в конкретное число. LLM сюда не допускается."""
    actions = {
        "aggressive_cool": min(100.0, causal_fan + 15),
        "balanced":        causal_fan,
        "energy_save":     max(30.0,  causal_fan - 10),
        "hold":            current_fan,
    }
    return actions.get(strategy, causal_fan)