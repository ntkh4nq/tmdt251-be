from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timedelta, timezone
from app.core.dependencies import get_vnpay_config, get_db, get_current_user
from app.schemas.order import PaymentURLRequest, PaymentUrlOut, OrderOut, OrderCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import select
from app.models.vnpay import vnpay
from app.models.order import Order, Order_Status, OrderItem, Order_Payment_Status
from app.services.utils import commit_to_db
from app.models.cart import Cart, CartItem
from app.models.user import User, Address
from typing import List
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
    #  print(f"DEBUG: url: {url}")
    return PaymentUrlOut.model_validate(payment_url)


@router.get("/payment_return")
async def payment_return(
    request: Request,
    vnpay_config: dict = Depends(get_vnpay_config),
    db: AsyncSession = Depends(get_db)
):
    """
    Payment return URL - validates and updates order status for demo.
    In production, this logic should be in IPN endpoint.
    """
    data = request.query_params
    response = {k: v for k, v in data.items()}
    
    Vnpay = vnpay(
        secret_key=vnpay_config["vnp_HashSecret"],
        vnpay_payment_url=vnpay_config["vnp_Url"],
    )
    
    # Validate signature
    if not Vnpay.validate_response(response):
        return "❌ Thanh toán thất bại - Chữ ký không hợp lệ"
    
    # Extract params
    payment_status = response.get("vnp_ResponseCode")
    txn_ref = response.get("vnp_TxnRef")
    amount = int(response.get("vnp_Amount", 0))
    
    # Parse order_id from txn_ref
    try:
        if txn_ref.startswith("ORDER"):
            order_id = int(txn_ref.replace("ORDER", ""))
        else:
            order_id = int(txn_ref)
    except (ValueError, AttributeError):
        return "❌ Mã giao dịch không hợp lệ"
    
    # Query order
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        return "❌ Không tìm thấy đơn hàng"
    
    # Check amount matches
    expected_amount = int(order.total_amount * 100)
    if amount != expected_amount:
        return f"❌ Số tiền không khớp (Expected: {expected_amount}, Got: {amount})"
    
    # Update order status (idempotent check)
    if order.payment_status != Order_Payment_Status.PAID:
        if payment_status == "00":
            order.status = Order_Status.PAID
            order.payment_status = Order_Payment_Status.PAID
            await commit_to_db(db)
            print(f"✅ [Payment Return] Order #{order_id} marked as PAID")
            return f"✅ Thanh toán thành công! Đơn hàng #{order_id} đã được xác nhận."
        else:
            order.status = Order_Status.CANCELLED
            order.payment_status = Order_Payment_Status.UNPAID
            await commit_to_db(db)
            print(f"❌ [Payment Return] Order #{order_id} payment failed, code: {payment_status}")
            return f"❌ Thanh toán thất bại. Mã lỗi: {payment_status}"
    else:
        return f"✅ Đơn hàng #{order_id} đã được thanh toán trước đó."


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
    
    # Validate request
    if not response:
        return JSONResponse({"RspCode": "99", "Message": "Invalid request"})
    
    if not Vnpay.validate_response(response):
        return JSONResponse({"RspCode": "97", "Message": "Invalid Signature"})

    # Extract params
    payment_status = response.get("vnp_ResponseCode")
    txn_ref = response.get("vnp_TxnRef")  # e.g., "ORDER123" or just order_id
    amount = int(response.get("vnp_Amount", 0))
    
    # Parse order_id from txn_ref
    # Assuming format: "ORDER{order_id}" or just "{order_id}"
    try:
        if txn_ref.startswith("ORDER"):
            order_id = int(txn_ref.replace("ORDER", ""))
        else:
            order_id = int(txn_ref)
    except (ValueError, AttributeError):
        return JSONResponse({"RspCode": "01", "Message": "Invalid TxnRef"})
    
    # Query order
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return JSONResponse({"RspCode": "01", "Message": "Order not found"})
    
    # Check amount matches (VNPay amount is * 100)
    expected_amount = int(order.total_amount * 100)
    if amount != expected_amount:
        return JSONResponse({"RspCode": "04", "Message": "Invalid amount"})
    
    # Check if already updated
    if order.payment_status == Order_Payment_Status.PAID:
        return JSONResponse({"RspCode": "02", "Message": "Order already updated"})
    
    # Update order status based on payment result
    if payment_status == "00":
        # Payment success
        order.status = Order_Status.PAID
        order.payment_status = Order_Payment_Status.PAID
        # Optional: add paid_at timestamp if you have the field
        # order.paid_at = datetime.now(timezone.utc)
        print(f"✅ Payment Success for Order #{order_id}")
    else:
        # Payment failed
        order.status = Order_Status.CANCELLED
        order.payment_status = Order_Payment_Status.UNPAID
        print(f"❌ Payment Failed for Order #{order_id}, Code: {payment_status}")
    
    await commit_to_db(db)
    
    return JSONResponse({"RspCode": "00", "Message": "Confirm Success"})


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
        status=Order_Status.PENDING,
        payment_status=Order_Payment_Status.UNPAID,
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
