from app.schemas import DraftResult


async def send_message(draft: DraftResult) -> dict:
    """Stub sender service.

    TODO: integrate platform-specific sender. Never auto-send without explicit approval.
    """
    _ = draft
    return {'status': 'sent', 'provider': 'stub'}
