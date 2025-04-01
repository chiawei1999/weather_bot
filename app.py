from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, QuickReply, QuickReplyButton, MessageAction

from weather_request import fetch_weather, parse_weather
from Area_FlexMessage import generate_flex_bubbles, taipei_districts, new_taipei_districts
from RichMenu import setup_line_rich_menu, ensure_rich_menu_image_exists

from dotenv import dotenv_values
from contextlib import asynccontextmanager
import uvicorn
import logging
import time

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("weather-bot")

# 常量定義
MESSAGES = {
    "DEFAULT": "請使用 LINE Rich Menu 點選城市來查詢天氣資訊！",
    "SEARCHING": "正在查詢中，請稍候...",
    "ERROR_FETCH": "取得 {} 的氣象資料失敗，請稍後再試。",
    "ERROR_DISTRICT": "無法識別行政區「{}」，請使用選單選擇有效的行政區。"
}

# 載入環境變數
config = dotenv_values(".env")
LINE_CHANNEL_ACCESS_TOKEN = config["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = config["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# FastAPI 應用與 lifespan：初始化 Rich Menu
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("正在啟動應用程序...")
    ensure_rich_menu_image_exists()
    setup_line_rich_menu(line_bot_api)
    yield
    logger.info("應用程序關閉中...")

app = FastAPI(lifespan=lifespan)

# Webhook 接收端點
@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_text = body.decode("utf-8")

    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        logger.error("無效的簽名")
        return JSONResponse(content={"message": "Invalid signature."}, status_code=400)
    except Exception as e:
        logger.error(f"處理webhook時發生錯誤: {e}")
        return JSONResponse(content={"message": f"Error: {str(e)}"}, status_code=500)

    return JSONResponse(content={"message": "OK"}, status_code=200)

# 處理訊息事件
@handler.add(MessageEvent)
def handle_message(event):
    if not isinstance(event.message, TextMessage):
        return

    user_text = event.message.text.strip()
    logger.info(f"收到用戶訊息: {user_text}")

    try:
        # 使用者查詢城市行政區
        if user_text == "我想要台北的氣象資訊":
            flex = generate_flex_bubbles("台北", taipei_districts)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage("請選擇台北市的行政區", flex))
            return

        if user_text == "我想要新北的氣象資訊":
            flex = generate_flex_bubbles("新北", new_taipei_districts)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage("請選擇新北市的行政區", flex))
            return

        # 使用者點選行政區 - 台北市
        if user_text.startswith("我想要台北") and user_text.endswith("的氣象資訊"):
            district = user_text.replace("我想要台北", "").replace("的氣象資訊", "")
            if district in taipei_districts:
                # 先回覆「正在查詢中」，提高用戶體驗
                try:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text=MESSAGES["SEARCHING"],
                            quick_reply=QuickReply(items=[
                                QuickReplyButton(action=MessageAction(label="回到台北市", text="我想要台北的氣象資訊"))
                            ])
                        )
                    )
                    
                    # 獲取天氣數據
                    _push_weather(event.source.user_id, district)
                except LineBotApiError:
                    # 如果回覆token已使用，則直接推送天氣
                    _push_weather(event.source.user_id, district)
            else:
                _reply_invalid_district(event.reply_token, district)
            return

        # 使用者點選行政區 - 新北市
        if user_text.startswith("我想要新北") and user_text.endswith("的氣象資訊"):
            district = user_text.replace("我想要新北", "").replace("的氣象資訊", "")
            if district in new_taipei_districts:
                # 先回覆「正在查詢中」，提高用戶體驗
                try:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text=MESSAGES["SEARCHING"],
                            quick_reply=QuickReply(items=[
                                QuickReplyButton(action=MessageAction(label="回到新北市", text="我想要新北的氣象資訊"))
                            ])
                        )
                    )
                    
                    # 獲取天氣數據
                    _push_weather(event.source.user_id, district)
                except LineBotApiError:
                    # 如果回覆token已使用，則直接推送天氣
                    _push_weather(event.source.user_id, district)
            else:
                _reply_invalid_district(event.reply_token, district)
            return

        # 未知指令
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(
                text=MESSAGES["DEFAULT"],
                quick_reply=QuickReply(items=[
                    QuickReplyButton(action=MessageAction(label="台北市", text="我想要台北的氣象資訊")),
                    QuickReplyButton(action=MessageAction(label="新北市", text="我想要新北的氣象資訊"))
                ])
            )
        )
    except Exception as e:
        logger.error(f"處理訊息時發生錯誤: {e}")
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(f"發生錯誤，請稍後再試: {str(e)[:30]}...")
        )

# 推送天氣資訊
def _push_weather(user_id, location):
    start_time = time.time()
    
    logger.info(f"正在查詢 {location} 的天氣")
    data = fetch_weather(location)
    
    if data:
        result = parse_weather(data, location)
        
        # 添加快速回覆按鈕，讓用戶更容易操作
        is_taipei = location in taipei_districts
        city_text = "我想要台北的氣象資訊" if is_taipei else "我想要新北的氣象資訊"
        
        line_bot_api.push_message(
            user_id, 
            TextSendMessage(text=result)
        )
        
        logger.info(f"成功發送 {location} 的天氣資訊，耗時: {time.time() - start_time:.2f}秒")
    else:
        line_bot_api.push_message(
            user_id, 
            TextSendMessage(MESSAGES["ERROR_FETCH"].format(location))
        )
        logger.error(f"獲取 {location} 的氣象資料失敗")

# 回傳天氣資訊 (使用reply_token的版本)
def _reply_weather(reply_token, location):
    data = fetch_weather(location)
    if data:
        result = parse_weather(data, location)
        line_bot_api.reply_message(reply_token, TextSendMessage(result))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(MESSAGES["ERROR_FETCH"].format(location)))

# 回傳行政區錯誤
def _reply_invalid_district(reply_token, district):
    line_bot_api.reply_message(reply_token, TextSendMessage(MESSAGES["ERROR_DISTRICT"].format(district)))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)