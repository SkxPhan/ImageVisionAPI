from pydantic import BaseModel


# -------------- token --------------
class Token(BaseModel):
    """
    Response schema when requesting an token.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Token schema.
    """

    username: str | None = None
