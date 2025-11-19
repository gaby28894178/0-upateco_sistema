from typing import Optional, List
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    available: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    available: Optional[bool] = None


class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    name: str
    phone: str
    address: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class Customer(CustomerBase):
    id: int

    class Config:
        from_attributes = True


class OrderItemInput(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: int
    notes: Optional[str] = None
    items: List[OrderItemInput]
    driver_id: Optional[int] = None


class Order(BaseModel):
    id: int
    customer_id: int
    status: str
    created_at: str
    notes: Optional[str]
    driver_id: Optional[int] = None


class OrderDetail(BaseModel):
    order: Order
    items: List[dict]
    subtotal: float
    total: float
    impuestos: float
    descuentos: float
    repartidor: Optional[dict] = None


class DriverBase(BaseModel):
    name: str
    phone: Optional[str] = None


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class Driver(DriverBase):
    id: int
    class Config:
        from_attributes = True