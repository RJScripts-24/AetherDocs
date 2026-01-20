from pydantic import BaseModel, HttpUrl
from typing import Optional

class UploadBase(BaseModel):
    title: str

class YoutubeURL(UploadBase):
    url: HttpUrl
