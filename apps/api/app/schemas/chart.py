"""Request/response schemas for the chart endpoints."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Gender = Literal["MALE", "FEMALE"]
CalendarType = Literal["SOLAR", "LUNAR"]


class ChartCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subject_name: Annotated[str, Field(min_length=2, max_length=120)]
    gender: Gender
    calendar_type: CalendarType = "SOLAR"

    birth_day: Annotated[int, Field(ge=1, le=31)]
    birth_month: Annotated[int, Field(ge=1, le=12)]
    birth_year: Annotated[int, Field(ge=1900, le=2100)]
    birth_hour: Annotated[int, Field(ge=0, le=23)]
    birth_minute: Annotated[int, Field(ge=0, le=59)] = 0
    is_leap_month: bool = False

    birth_place: Annotated[str | None, Field(max_length=160)] = None
    timezone_name: Annotated[str, Field(max_length=64)] = "Asia/Ho_Chi_Minh"
    tz_offset: Annotated[float, Field(ge=-12, le=14)] = 7.0
    note: Annotated[str | None, Field(max_length=500)] = None
    relationship_label: Annotated[str | None, Field(max_length=60)] = None

    @model_validator(mode="after")
    def _check_calendar_consistency(self) -> ChartCreateRequest:
        if self.is_leap_month and self.calendar_type != "LUNAR":
            raise ValueError("Chỉ ngày âm lịch mới có tháng nhuận")
        if self.calendar_type == "SOLAR":
            try:
                birth = date(self.birth_year, self.birth_month, self.birth_day)
            except ValueError as exc:  # 31/02, 30/02 …
                raise ValueError("Ngày sinh dương lịch không tồn tại") from exc
            if birth > date.today():
                raise ValueError("Ngày sinh không thể ở tương lai")
        elif self.birth_day > 30:
            raise ValueError("Tháng âm lịch chỉ có tối đa 30 ngày")
        return self


class ChartSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_name: str
    relationship_label: str | None
    gender: Gender
    calendar_type: CalendarType
    birth_day: int
    birth_month: int
    birth_year: int
    birth_hour: int
    birth_minute: int
    birth_place: str | None
    engine_stage: str
    engine_version: str
    created_at: datetime


class ChartDetail(ChartSummary):
    note: str | None
    timezone_name: str
    tz_offset: float
    chart: dict[str, Any] = Field(alias="chart_json")
