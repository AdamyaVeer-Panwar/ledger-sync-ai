from enum import Enum

from pydantic import BaseModel, Field, model_validator


class AIResolutionDecision(str, Enum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    AMBIGUOUS = "AMBIGUOUS"


class AIResolution(BaseModel):
    decision: AIResolutionDecision
    candidate_ids: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_codes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_decision_consistency(self):
        if (
        self.decision == AIResolutionDecision.MATCH
        and not self.candidate_ids
        ):
            raise ValueError(
            "candidate_ids is required for MATCH"
            )

        if (
        self.decision == AIResolutionDecision.NO_MATCH
        and self.candidate_ids
        ):
            raise ValueError(
            "candidate_ids must be empty for NO_MATCH"
        )

        return self