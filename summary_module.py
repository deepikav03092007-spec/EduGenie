from ai_client import generate_text


def summarize_text(text: str) -> str:
    """
    Summarize educational content.
    """

    text = text.strip()

    if not text:
        raise ValueError(
            "Please enter text to summarize."
        )

    prompt = """
Summarize the following educational text
in simple language.

Requirements:

- Preserve important facts.
- Preserve important ideas.
- Remove repetition.
- Make it useful for student revision.
- Use bullet points where useful.

TEXT:

""" + text

    return generate_text(
        prompt,
        system_instruction=(
            "You are EduGenie, "
            "a concise study-notes generator."
        ),
    )