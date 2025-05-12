from pydantic import BaseModel, Field


class ProductIDModel(BaseModel):
    id: int


class ProductModel(BaseModel):
    name: str = Field(..., min_length=5)
    description: str = Field(..., min_length=5)
    min_packing: str = Field(..., min_length=3)
    price: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    image: str | None = None