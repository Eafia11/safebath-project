from pydantic import BaseModel
from typing import Any, Optional


class CommonResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any]