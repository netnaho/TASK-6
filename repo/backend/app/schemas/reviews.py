from pydantic import BaseModel


class ReviewClaimRequest(BaseModel):
    priority: str | None = None


class ReviewCompleteRequest(BaseModel):
    note: str | None = None
