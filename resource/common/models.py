from pydantic import BaseModel
#  common
class LinkResponse(BaseModel):
    href: str
    rel: str
    type: str