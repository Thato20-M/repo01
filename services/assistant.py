def generate_llm_prompt(context, question):
    prompt = f"""
You are an academic assistant.

Student: {context['student']}
Programme: {context['programme']}

Predictions:
"""

    for p in context["predictions"]:
        prompt += f"- {p}\n"

    if context["at_risk"]:
        prompt += f"\nModules at risk: {', '.join(context['at_risk'])}\n"

    prompt += f"""
Question: {question}

Give clear, supportive, data-driven advice.
"""
    return prompt
