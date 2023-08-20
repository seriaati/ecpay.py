# ecpay.py
Python 非阻塞式綠界支付 API 串接
# 前言
花了老半天時間終於弄懂綠界 API 怎麼搞，網路上查的大部分 guide 要馬是太舊不然就都是 php 的，所以在這裡放個 package 方便後來的開發者使用。  
綠界自己也有 SDK 但不是 asyncio 而且也不是一個套件 😠 只好自己寫一個。  
沒有 python 辦不到的事情好嗎 👍👍
# 安裝
```
pip install git+https://github.com/seriaati/ecpay.py
```
# 範例
位於 `/examples` 資料夾
# 綠界 API 的大致流程
## 要求
- 首先需要一個伺服器（來佈署你的 API）
- 你還需要一個能讓其他人存取的網址，我自己用的是 ngrok，設定快速方便
## 過程
首先，帶著你想要的參數，然後用 POST 請求呼叫綠界產生訂單的 API（AIOCheckOut）。  
跟目前常見的 API 不同，在呼叫綠界產生訂單的 API（AIOCheckOut）的時候，它不會回傳任何東西。  
但現在問題來了，一般的使用者用一般的瀏覽器要怎麼自己去發 POST 請求？  
沒錯，所以你需要自己架好一個 GET 請求的 API，把參數打包進去，請求自己的 GET API，然後讓 GET API 回傳一個會發送 POST 請求的 HTML 表單，之後它才會把使用者重新導向到綠界的支付頁面。  
這樣才能達成我要的效果，使用者點擊一個連結之後自動達到付款頁面。  
這個 GET 的連結你可以自己用程式碼生成，讓使用者點擊後觸發自己寫的 API 。
# 其他資源
強烈建議要去官方文檔看「產生訂單」頁面了解參數的限制跟意義：  
- [綠界官方 API 文檔](https://developers.ecpay.com.tw/?p=2509)  
- [綠界自己的 Python SDK](https://github.com/ECPay/ECPayAIO_Python)  
- [網路上找到的 Flask 教學](https://www.maxlist.xyz/2020/02/14/python-ecpay/)  
# 聯絡
有疑問可以加我 Discord：[@seria_ati](https://discord.com/users/410036441129943050)
