from pydantic import BaseModel


class ScoreRequest(BaseModel):
    force: bool = False
