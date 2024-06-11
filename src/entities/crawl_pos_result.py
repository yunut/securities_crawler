from typing import Optional
from pydantic import BaseModel


class CrawlNewPosResult(BaseModel):
    resultCode: str
    resultMessage: str
