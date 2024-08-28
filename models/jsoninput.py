from pydantic import BaseModel, HttpUrl


class JSONInput(BaseModel):
    json_to_convert: dict
    return_endpoint: HttpUrl
    