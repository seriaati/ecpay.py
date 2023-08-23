import datetime
import hashlib
import random
import string
import urllib.parse
from typing import Any, Dict, Literal, Optional, Tuple


class ECPayClient:
    """
    綠界科技金流串接端口

    屬性:
        merchant_id: 特店編號
        hash_key: HashKey
        hash_iv: HashIV
        test: 是否為測試模式
    """

    def __init__(
        self, merchant_id: str, hash_key: str, hash_iv: str, *, test: bool
    ) -> None:
        self.test = test
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv

    def _gen_mac_value(self, d: Dict[str, Any]) -> str:
        """
        產生檢查碼, 詳情請參考 https://developers.ecpay.com.tw/?p=2902

        參數:
            d: 用於產生檢查碼的資料
        """
        sorted_items = sorted(d.items())
        combined = "&".join(f"{k}={v}" for k, v in sorted_items)
        combined = f"HashKey={self.hash_key}&{combined}&HashIV={self.hash_iv}"
        encoded = urllib.parse.quote_plus(combined).lower()
        hashed = hashlib.sha256(encoded.encode()).hexdigest().upper()
        return hashed

    def _gen_trade_no(self) -> str:
        """
        隨機產生交易編號

        返回:
            交易編號
        """
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(20))

    def _gen_html_post_form(self, data: Dict[str, Any], url: str) -> str:
        """
        產生 HTML POST 表單

        參數:
            data : 要 POST 的資料
            url : 要 POST 到的網址

        返回:
            HTML 表單
        """
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
        choose_payment: Literal[
            "ALL", "TWQR", "Credit", "WebATM", "ATM", "CVS", "BARCODE", "ApplePay"
        ] = "ALL",
        merchant_trade_no: Optional[str] = None,
        store_id: Optional[str] = None,
        client_back_url: Optional[str] = None,
        item_url: Optional[str] = None,
        remark: Optional[str] = None,
        choose_sub_payment: Optional[str] = None,
        order_result_url: Optional[str] = None,
        need_extra_paid_info: Literal["Y", "N"] = "N",
        ignore_payment: Optional[str] = None,
        platform_id: Optional[str] = None,
        custom_field_1: Optional[str] = None,
        custom_field_2: Optional[str] = None,
        custom_field_3: Optional[str] = None,
        custom_field_4: Optional[str] = None,
        language: Optional[Literal["ENG", "KOR", "JPN", "CHI"]] = None,
    ) -> Tuple[str, str]:
        """
        產生訂單, 參數說明請參考 https://developers.ecpay.com.tw/?p=2862

        參數:
            total_amount: 交易金額
            trade_desc: 交易描述
            item_name: 商品名稱
            return_url: 付款完成通知回傳網址
            choose_payment: 選擇預設付款方式
            merchant_trade_no: 特店訂單編號, 若為空值, 則自動產生
            store_id: 特店旗下店舖代號
            client_back_url: Client 端返回特店的按鈕連結
            item_url: 商品銷售網址
            remark: 備註欄位
            choose_sub_payment: 付款子項目
            order_result_url: Client 端回傳付款結果網址
            need_extra_paid_info: 是否需要額外的付款資訊
            ignore_payment: 隱藏付款方式
            platform_id: 特約合作平台商代號
            custom_field_1: 自訂名稱欄位 1
            custom_field_2: 自訂名稱欄位 2
            custom_field_3: 自訂名稱欄位 3
            custom_field_4: 自訂名稱欄位 4
            language: 語系設定

        返回:
            檢查碼, HTML 表單
        """
        if self.test:
            url = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
        else:
            url = "https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5"

        data = {
            "MerchantID": self.merchant_id,
            "MerchantTradeNo": merchant_trade_no or self._gen_trade_no(),
            "MerchantTradeDate": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "PaymentType": "aio",
            "TotalAmount": total_amount,
            "TradeDesc": trade_desc,
            "ItemName": item_name,
            "ReturnURL": return_url,
            "ChoosePayment": choose_payment,
            "EncryptType": 1,
            "StoreID": store_id or "",
            "ClientBackURL": client_back_url or "",
            "ItemURL": item_url or "",
            "Remark": remark or "",
            "ChooseSubPayment": choose_sub_payment or "",
            "OrderResultURL": order_result_url or "",
            "NeedExtraPaidInfo": need_extra_paid_info or "",
            "IgnorePayment": ignore_payment or "",
            "PlatformID": platform_id or "",
            "CustomField1": custom_field_1 or "",
            "CustomField2": custom_field_2 or "",
            "CustomField3": custom_field_3 or "",
            "CustomField4": custom_field_4 or "",
            "Language": language or "",
        }
        data["CheckMacValue"] = self._gen_mac_value(data)
        return data["CheckMacValue"], self._gen_html_post_form(data, url)
