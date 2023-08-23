import os
from typing import Dict

import fastapi
from dotenv import load_dotenv

from ecpay import ECPayClient

app = fastapi.FastAPI()


class App(fastapi.FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        load_dotenv()
        merchant_id = os.getenv("MERCHANT_ID")
        hash_key = os.getenv("HASH_KEY")
        hash_iv = os.getenv("HASH_IV")
        if not (merchant_id and hash_key and hash_iv):
            raise RuntimeError("Missing ECPay credentials")

        self.ecpay = ECPayClient(
            merchant_id=merchant_id,
            hash_key=hash_key,
            hash_iv=hash_iv,
            test=True,
        )
        self.mac_id_map: Dict[str, str] = {}

    @app.get("/ecpay_redirect")
    async def ecpay_redirect(self, request: fastapi.Request) -> fastapi.Response:
        params = dict(request.query_params)
        mac_value, html = await self.ecpay.create_order(
            total_amount=params["TotalAmount"],
            trade_desc=params["TradeDesc"],
            item_name=params["ItemName"],
            return_url=params["ReturnURL"],
            custom_field_1=params["CustomField1"],
        )
        self.mac_id_map[params["CustomField1"]] = mac_value
        return fastapi.Response(content=html, media_type="text/html")

    @app.post("/ecpay_return")
    async def ecpay_return(self, request: fastapi.Request) -> fastapi.Response:
        params = dict(await request.form())
        mac_value = params.pop("CheckMacValue")
        if mac_value != self.mac_id_map[params["CustomField1"]]:  # type: ignore
            return fastapi.Response(content="0|Error", status_code=400)
        if params["RtnCode"] == "1":
            # 付款成功
            pass
        return fastapi.Response(content="1|OK")
