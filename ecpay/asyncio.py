import datetime
import hashlib
import random
import string
import urllib.parse
from typing import Any, Dict


class ECPayClient:
    def __init__(
        self, merchant_id: str, hash_key: str, hash_iv: str, *, test: bool
    ) -> None:
        self.test = test
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv

    def _get_check_mac(self, d: Dict[str, Any]) -> str:
        sorted_items = sorted(d.items())
        combined = "&".join(f"{k}={v}" for k, v in sorted_items)
        combined = f"HashKey={self.hash_key}&{combined}&HashIV={self.hash_iv}"
        encoded = urllib.parse.quote_plus(combined).lower()
        hashed = hashlib.sha256(encoded.encode()).hexdigest().upper()
        return hashed

    def gen_trade_no(self) -> str:
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(20))

    def gen_html_post_form(self, data: Dict[str, Any], url: str) -> str:
        html = f"""
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            </head>
            <body>
                <form id="ecpay" method="post" action="{url}">
        """
        for k, v in data.items():
            html += f'<input type="hidden" name="{k}" value="{v}">'
        html += """
                </form>
                <script>
                    document.getElementById("ecpay").submit();
                </script>
            </body>
        </html>
        """
        return html

    async def create_order(
        self,
        *,
        total_amount: str,
        trade_desc: str,
        item_name: str,
        return_url: str,
        choose_payment: str,
        custom_field_1: str,
    ) -> str:
        if self.test:
            url = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
        else:
            url = "https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5"

        data = {
            "MerchantID": self.merchant_id,
            "MerchantTradeNo": self.gen_trade_no(),
            "MerchantTradeDate": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "PaymentType": "aio",
            "TotalAmount": int(total_amount),
            "TradeDesc": trade_desc,
            "ItemName": item_name,
            "ReturnURL": return_url,
            "ChoosePayment": choose_payment,
            "EncryptType": 1,
            "CustomField1": custom_field_1,
        }
        data["CheckMacValue"] = self._get_check_mac(data)
        return self.gen_html_post_form(data, url)
