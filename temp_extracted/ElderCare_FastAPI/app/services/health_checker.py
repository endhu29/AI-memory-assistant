THRESHOLDS = {
    "bp_systolic":      {"min": 90,   "max": 140, "unit": "mmHg",  "label": "Blood Pressure (Systolic)"},
    "bp_diastolic":     {"min": 60,   "max": 90,  "unit": "mmHg",  "label": "Blood Pressure (Diastolic)"},
    "blood_sugar_mgdl": {"min": 70,   "max": 180, "unit": "mg/dL", "label": "Blood Sugar"},
    "heart_rate_bpm":   {"min": 50,   "max": 100, "unit": "bpm",   "label": "Heart Rate"},
    "spo2_pct":         {"min": 95,   "max": 100, "unit": "%",     "label": "Oxygen Saturation (SpO2)"},
    "temperature_c":    {"min": 35.0, "max": 37.5,"unit": "°C",    "label": "Body Temperature"},
}


def check_health_log(log) -> list:
    violations = []
    for field, rules in THRESHOLDS.items():
        value = getattr(log, field, None)
        if value is None:
            continue
        if value < rules["min"] or value > rules["max"]:
            direction = "low" if value < rules["min"] else "high"
            violations.append({
                "metric":    rules["label"],
                "value":     f"{value} {rules['unit']}",
                "threshold": f"{rules['min']}–{rules['max']} {rules['unit']}",
                "message":   f"{rules['label']} is too {direction}",
            })
    if log.health_feeling is not None and log.health_feeling < 2:
        violations.append({
            "metric": "Self-reported Feeling", "value": f"{log.health_feeling}/5",
            "threshold": "≥ 2/5", "message": "Elderly person reported feeling very unwell",
        })
    return violations


def check_weight_change(new_log, prev_log) -> list:
    if new_log.weight_kg and prev_log and prev_log.weight_kg:
        diff = abs(new_log.weight_kg - prev_log.weight_kg)
        if diff > 2.0:
            return [{"metric": "Weight",
                     "value": f"{new_log.weight_kg} kg (was {prev_log.weight_kg} kg)",
                     "threshold": "Change ≤ 2 kg/day",
                     "message": f"Significant weight change of {diff:.1f} kg in 24 hours"}]
    return []