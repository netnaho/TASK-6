from math import ceil

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, select


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1)
    max_page_size: int = 200

    @model_validator(mode="after")
    def enforce_max_page_size(self):
        if self.page_size > self.max_page_size:
            self.page_size = self.max_page_size
        return self


class PaginatedResult(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int

    @property
    def meta(self) -> dict:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total": self.total,
            "total_pages": self.total_pages,
        }


def page_meta(total: int, page: int, page_size: int) -> dict:
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": ceil(total / page_size) if page_size else 1,
    }


def paginate_query(db, stmt, params: PaginationParams) -> PaginatedResult:
    total = db.execute(select(func.count()).select_from(stmt.order_by(None).subquery())).scalar_one()
    paged_stmt = stmt.offset((params.page - 1) * params.page_size).limit(params.page_size)
    items = list(db.execute(paged_stmt).scalars().all())
    meta = page_meta(total, params.page, params.page_size)
    return PaginatedResult(items=items, total=total, page=meta["page"], page_size=meta["page_size"], total_pages=meta["total_pages"])
