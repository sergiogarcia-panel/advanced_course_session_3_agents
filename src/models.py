from pydantic import BaseModel


class UserInfo(BaseModel):
    name: str
    allowed: bool


class CryptoPrice(BaseModel):
    symbol: str
    price: float
    currency: str