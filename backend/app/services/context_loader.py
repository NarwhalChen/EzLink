from app.dependencies import get_session_context


def load_core_context(session_id: int) -> dict:
    user_goal, experience_markdown = get_session_context(session_id)
    return {
        'user_goal': user_goal,
        'experience_markdown': experience_markdown,
    }
