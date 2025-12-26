def classify_intent(llm, question: str) -> str:
    prompt = f"""
Classify the academic intent of this question.

Choose ONE:
- framework_overview
- concept_explanation
- comparison
- step_by_step
- example_case
- ethical_reasoning

Question:
"{question}"

Return ONLY the label.
"""
    response = llm.invoke(prompt)
    return response.content.strip().lower()