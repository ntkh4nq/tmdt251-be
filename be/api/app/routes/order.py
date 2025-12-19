from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timedelta, timezone
from app.core.dependencies import get_vnpay_config, get_db, get_current_user
from app.schemas.order import PaymentURLRequest, PaymentUrlOut, OrderOut, OrderCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.vnpay import vnpay
from app.models.order import Order, OrderItem
from app.models.cart import Cart, CartItem
from app.models.user import User, Address
from typing import List

router = APIRouter(prefix="/order", tags=["Order"])


@router.post("/payment_url", response_model=PaymentUrlOut)
def payment_url(
    data: PaymentURLRequest, vnpay_config: dict = Depends(get_vnpay_config)
):
    Vnpay = vnpay(
        secret_key=vnpay_config["vnp_HashSecret"],
        vnpay_payment_url=vnpay_config["vnp_Url"],
    )
    created_date = data.vnp_CreateDate.astimezone(timezone(timedelta(hours=7)))
    req = {
        "vnp_Version": data.vnp_Version,
        "vnp_Command": data.vnp_Command,
        "vnp_TmnCode": vnpay_config["vnp_TmnCode"].strip(),
        "vnp_Amount": data.vnp_Amount,
        "vnp_CreateDate": created_date.strftime("%Y%m%d%H%M%S"),
        "vnp_CurrCode": data.vnp_CurrCode,
        "vnp_IpAddr": data.vnp_IpAddr,
        "vnp_Locale": data.vnp_Locale,
        "vnp_OrderInfo": data.vnp_OrderInfo,
        "vnp_OrderType": data.vnp_OrderType,
        "vnp_ReturnUrl": data.vnp_ReturnUrl,
        "vnp_TxnRef": data.vnp_TxnRef,
    }

    if data.vnp_BankCode and data.vnp_BankCode.strip():
        req["vnp_BankCode"] = data.vnp_BankCode
    # req["vnp_ExpireDate"] = (created_date + timedelta(minutes=int(vnpay_config["vnp_ExpiredDate"]))).strftime('%Y%m%d%H%M%S')

    payment_url = Vnpay.get_payment_url(req)
    print(f"debug: request goc: {req}")
    # print(f"DEBUG: url: {url}")
    return PaymentUrlOut.model_validate(payment_url)


@router.get("/payment_return")
def read_item(request: Request, vnpay_config: dict = Depends(get_vnpay_config)):
    data = request.query_params.items()
    response = {}
    Vnpay = vnpay(
        secret_key=vnpay_config["vnp_HashSecret"],
        vnpay_payment_url=vnpay_config["vnp_Url"],
    )
    for i in data:
        response[i[0]] = i[1]
    if Vnpay.validate_response(response):
        return "Thành công"
    else:
        return "Thất bại"


@router.get("/ipn")
async def payment_ipn(
    request: Request,
    vnpay_config: dict = Depends(get_vnpay_config),
    db: AsyncSession = Depends(get_db),
):
    data = request.query_params
    response = {k: v for k, v in data.items()}

    Vnpay = vnpay(
        secret_key=vnpay_config["vnp_HashSecret"],
        vnpay_payment_url=vnpay_config["vnp_Url"],
    )
    if not response:
        return JSONResponse({"RspCode": "99", "Message": "Invalid request"})
    if not Vnpay.validate_response(response):
        return JSONResponse({"RspCode": "97", "Message": "Invalid Signature"})

    payment_status = response.get("vnp_ResponseCode")
    order_id = response.get("vnp_TxnRef")
    amount = response.get("vnp_Amount")
    # method, paid_at...

    first_time_update = True  # query db de check
    total_amount_matches = True  # query db de check
    if total_amount_matches:
        if first_time_update:
            if payment_status == "00":
                print("Payment Success")
                # update orders.status= paid
            else:
                print("Payment Error")
                # update orders.status = failed/cancelled

            return JSONResponse({"RspCode": "00", "Message": "Confirm Success"})
        else:
            return JSONResponse({"RspCode": "02", "Message": "Order Already Update"})
    else:
        return JSONResponse({"RspCode": "04", "Message": "invalid amount"})


@router.get("", response_model=List[OrderOut])
async def get_my_orders(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{id}", response_model=OrderOut)
async def get_order_details(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order).where(Order.id == id, Order.user_id == current_user.id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=OrderOut)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Get Cart
    cart_result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = cart_result.scalar_one_or_none()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # 2. Check Address
    # (Optional: Validate address_id belongs to user)

    # 3. Calculate Total
    subtotal = 0.0
    for item in cart.items:
        # Assuming product loaded in cart items. If not, might need join.
        # But lazy="selectin" in models helps.
        # NOTE: item.product might rely on async loading if not careful.
        # With selectin, it should be fine if committed.
        if item.product:
            subtotal += item.quantity * item.product.price
        else:
            # Should fetch product price
            pass

    total_amount = subtotal  # + shipping fee logic?

    # 4. Create Order
    new_order = Order(
        user_id=current_user.id,
        address_id=data.address_id,
        subtotal=subtotal,
        total_amount=total_amount,
        status="pending",
    )
    db.add(new_order)
    await db.flush()  # get ID

    # 5. Move items
    for item in cart.items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            custom_configuration=item.custom_configuration,
        )
        db.add(order_item)

    # 6. Clear Cart
    for item in cart.items:
        await db.delete(item)

    await commit_to_db(db)
    await db.refresh(new_order)
    return new_order
