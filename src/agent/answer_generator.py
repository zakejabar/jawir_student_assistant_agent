def generate_answer(question, structured_context):
    context_text = ""

    if structured_context["concepts"]:
        context_text += "Concepts:\n" + ", ".join(structured_context["concepts"]) + "\n\n"

    if structured_context["relationships"]:
        context_text += "Relationships:\n" + "\n".join(structured_context["relationships"]) + "\n\n"

    if structured_context["documents"]:
        context_text += "Documents:\n" + "\n".join(structured_context["documents"])

    prompt = f"""
    You are a university tutor.

    Answer using this structure:
    1. Definition
    2. Objectives
    3. Components / Tools
    4. Integration Levels
    5. Benefits
    6. Example

    ONLY use the context below.

    Context:
    {context_text}

    Question: {question}
    """

    return prompt