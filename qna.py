from ai_client import generate_text


def answer_question(question: str) -> str:
    """
    Answer a student's question.
    """

    question = question.strip()

    if not question:
        raise ValueError(
            "Please enter a question."
        )

    return generate_text(
        question,
        system_instruction=(
            "You are EduGenie, an academic Q&A assistant. "
            "Answer directly and clearly. "
            "Use simple language, short sections, "
            "examples, and step-by-step reasoning "
            "when appropriate. "
            "If the question is ambiguous, "
            "state the assumption you made."
        ),
    )