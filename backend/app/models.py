import json
from datetime import datetime, UTC


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def to_json(data: dict) -> str:
    return json.dumps(data)


def from_json(raw: str) -> dict:
    return json.loads(raw)
