import os

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

    @app.get("/ecpay_redirect")
    async def ecpay_redirect(self, request: fastapi.Request) -> fastapi.Response:
        params = dict(request.query_params)
        html = await self.ecpay.create_order(
            total_amount=params["TotalAmount"],
            trade_desc=params["TradeDesc"],
            item_name=params["ItemName"],
            return_url=params["ReturnURL"],
            choose_payment=params["ChoosePayment"],
            custom_field_1=params["CustomField1"],
        )
        return fastapi.Response(content=html, media_type="text/html")
