from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta, timezone
from app.core.dependencies import get_vnpay_config
from app.schemas.order import PaymentURLRequest
from app.models.vnpay import vnpay

router = APIRouter(prefix="/order", tags=["Order"])

@router.post("/payment_url")
def payment_url(
    data: PaymentURLRequest,
    vnpay_config: dict = Depends(get_vnpay_config)
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
        "vnp_BankCode": data.vnp_BankCode,
        "vnp_CreateDate": created_date.strftime('%Y%m%d%H%M%S'),
        "vnp_CurrCode": data.vnp_CurrCode,
        "vnp_IpAddr": data.vnp_IpAddr,
        "vnp_Locale": data.vnp_Locale,
        "vnp_OrderInfo": data.vnp_OrderInfo,
        "vnp_OrderType": data.vnp_OrderType,
        "vnp_ExpireDate": (created_date + timedelta(minutes=int(vnpay_config["vnp_ExpiredDate"]))).strftime('%Y%m%d%H%M%S'),
        "vnp_ReturnUrl": data.vnp_ReturnUrl,
        "vnp_TxnRef": data.vnp_TxnRef,
    }
    url = Vnpay.get_payment_url(req)
    print(f"request goc: {req}")
    print(f"url: {url}")
    return RedirectResponse(url)

@router.get("/payment_return")
def read_item(request:Request):
    data = request.query_params.items()
    response={}
    for i in data:
        response[i[0]] = i[1]
    if vnpay.validate_response(response):
        return "Thành công"
    else:
        return "Thất bại"