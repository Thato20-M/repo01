def build_llm_context(profile, predictions, achievements, events):
    context = {
        "student": profile.get("name"),
        "programme": profile.get("programme"),
        "predictions": [],
        "at_risk": [],
        "events": events[:3],
        "achievements": achievements
    }

    for module, p in predictions.items():
        context["predictions"].append(
            f"{module}: next mark {p['next_mark']:.1f}%, risk {p['risk_prob']:.0%}"
        )
        if p["risk_prob"] > 0.6:
            context["at_risk"].append(module)

    return context
