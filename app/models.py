from pydantic import BaseModel, Field
from typing import Optional, List

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)

class CartItemUpdate(BaseModel):
    product_id: int
    quantity: int = Field(ge=0)

class WishlistToggle(BaseModel):
    product_id: int

class WalletTopUp(BaseModel):
    amount: float = Field(gt=0)
    payment_channel: Optional[str] = "UPI"

class AddressCreate(BaseModel):
    tag: str = "Home"
    address_line: str
    landmark: Optional[str] = None
    city: str = "Bhubaneswar"
    pincode: str = "751001"
    is_default: bool = False

class OrderCreate(BaseModel):
    address_id: Optional[int] = None
    payment_method: str = "wallet" # 'wallet', 'upi', 'card', 'cod'
    tip: float = 0.0
    coupon_code: Optional[str] = None

class UserLogin(BaseModel):
    phone: str
    otp: Optional[str] = "1234"

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
