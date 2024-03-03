from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RefreshKeySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    exp: datetime
    refresh: str
    sub: str | None = ""
