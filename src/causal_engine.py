# import yaml

# def apply_guardrails(current_temp, current_fan, current_power):
#     # Читаем лимиты
#     with open('config/settings.yaml', 'r') as file:
#         config = yaml.safe_load(file)
        
#     MAX_POWER = config['infrastructure']['max_power_kw']
#     TARGET_TEMP = config['infrastructure']['target_temp_c']
#     ATE_TEMP = config['causal_weights']['ate_temp']
#     ATE_POWER = config['causal_weights']['ate_power']
    
#     # 1. Считаем, сколько энергии еще доступно
#     power_margin = MAX_POWER - current_power
#     max_fan_increase = power_margin / ATE_POWER
#     safe_max_fan = min(100.0, current_fan + max_fan_increase)
    
#     # 2. Считаем идеальную скорость для охлаждения
#     delta_temp = current_temp - TARGET_TEMP
#     ideal_fan = current_fan + (delta_temp / abs(ATE_TEMP))
    
#     # 3. GUARDRAIL: Обрезаем опасные значения
#     final_fan_speed = max(0.0, min(ideal_fan, safe_max_fan))
    
#     # Прогноз
#     expected_temp = current_temp - ((final_fan_speed - current_fan) * abs(ATE_TEMP))
#     expected_power = current_power + ((final_fan_speed - current_fan) * ATE_POWER)
    
#     return final_fan_speed, expected_temp, expected_power, MAX_POWER

import yaml
import os

def load_config():
    """Безопасная загрузка конфига с фоллбэком на случай, если файл не найден"""
    config_path = "settings.yaml"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        # Если YAML недоступен, возвращаем твои доказанные веса напрямую
        return {
            "infrastructure": {
                "max_power_kw": 120.0,
                "target_temp_c": 22.0
            },
            "causal_weights": {
                "ate_cool_A": -0.03540,
                "ate_power": 0.20071,
                "ate_load": 0.06565,
                "ate_weather": 0.14649
            }
        }

def apply_guardrails(current_temp, current_fan, current_power):
    with open('config/settings.yaml', 'r') as file:
        config = yaml.safe_load(file)
 
    MAX_POWER  = config['infrastructure']['max_power_kw']
    TARGET_TEMP = config['infrastructure']['target_temp_c']
    ATE_TEMP   = config['causal_weights']['ate_temp']
    ATE_POWER  = config['causal_weights']['ate_power']
 
    power_margin     = MAX_POWER - current_power
    max_fan_increase = power_margin / ATE_POWER
    safe_max_fan     = min(100.0, current_fan + max_fan_increase)
 
    delta_temp = current_temp - TARGET_TEMP
    ideal_fan  = current_fan + (delta_temp / abs(ATE_TEMP))
 
    final_fan_speed = max(10.0, min(ideal_fan, safe_max_fan))
 
    expected_temp  = current_temp - ((final_fan_speed - current_fan) * abs(ATE_TEMP))
    expected_power = current_power + ((final_fan_speed - current_fan) * ATE_POWER)
 
    return final_fan_speed, expected_temp, expected_power, MAX_POWER
 
 
def find_dominant_cause(t_out, load, fan, weights):
    """
    Считает вклад каждого фактора через ATE-веса.
    Возвращает имя доминантного фактора и словарь всех вкладов.
    """
    contributions = {
        "Нагрузка серверов":       abs(load  * weights['ate_load']),
        "Уличная температура":     abs(t_out * weights['ate_weather']),
        "Охлаждение (вентилятор)": abs(fan   * weights['ate_cool_A']),
    }
    dominant = max(contributions, key=contributions.get)
    return dominant, contributions