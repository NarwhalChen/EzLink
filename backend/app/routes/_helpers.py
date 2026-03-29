"""Shared helpers for candidate record serialisation."""

import json
from typing import Any

from app.models import CandidateRecord as CandidateRecordModel
from app.schemas import (
    CandidateProfile,
    CandidateRecord,
    DraftResult,
    EvaluationResult,
)


def _maybe_parse(raw: str | None, model: type) -> Any | None:
    if raw is None:
        return None
    return model(**json.loads(raw))


def deserialise_candidate(record: CandidateRecordModel) -> CandidateRecord:
    return CandidateRecord(
        id=record.id,
        session_id=record.session_id,
        profile_url=record.profile_url,
        profile_data=_maybe_parse(record.profile_data, CandidateProfile),
        evaluation=_maybe_parse(record.evaluation, EvaluationResult),
        draft=_maybe_parse(record.draft, DraftResult),
        approved=record.approved,
        sent=record.sent,
        created_at=record.created_at,
    )
