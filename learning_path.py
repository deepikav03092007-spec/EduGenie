from ai_client import generate_text


def get_learning_recommendations(topic, level="beginner", weeks=4):
    prompt = f"""
Create a personalized learning path for the following topic.

Topic: {topic}
Level: {level}
Duration: {weeks} weeks

Give the response in a simple, structured format.

Include:
1. Learning goals
2. Weekly topics
3. Practice activities
4. Mini projects
5. Final revision plan

Keep it practical and easy for a student to follow.
"""

    return generate_text(prompt)