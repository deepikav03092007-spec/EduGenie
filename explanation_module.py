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
            "Use simple English, examples, and step-by-step "
            "reasoning when appropriate."
        ),
    )


def explain_concept(
    concept: str,
    level: str = "beginner",
) -> str:
    """
    Generate a simple explanation of a concept using Gemini.
    """

    concept = concept.strip()

    if not concept:
        raise ValueError(
            "Please enter a concept."
        )

    prompt = f"""
Explain the following concept to a student.

Concept:
{concept}

Student level:
{level}

Requirements:
- Use simple English.
- Start with a short definition.
- Explain the concept step by step.
- Give a simple real-world example.
- Avoid unnecessary technical jargon.
- Make the answer easy to understand.
- Use clear headings.
"""

    return generate_text(prompt)