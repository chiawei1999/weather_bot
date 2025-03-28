from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, MessageAction
from PIL import Image, ImageDraw
import os

RICH_MENU_IMAGE_PATH = "rich_menu_image.jpg"

def ensure_rich_menu_image_exists():
    from PIL import ImageFont
    import platform

    def find_font():
        sys = platform.system()
        font_path = None
        if sys == "Windows":
            font_path = "C:/Windows/Fonts/msjh.ttc"
        elif sys == "Darwin":
            font_path = "/System/Library/Fonts/PingFang.ttc"
        elif sys == "Linux":
            font_path = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"

        if font_path and os.path.exists(font_path):
            return ImageFont.truetype(font_path, 120)
        else:
            print("[WARNING] 找不到中文字型，使用預設字體，中文字可能無法顯示")
            return ImageFont.load_default()

    if not os.path.exists(RICH_MENU_IMAGE_PATH):
        print("[INFO] 重新建立 rich_menu_image.jpg 並使用中文字型")
        img = Image.new("RGB", (2500, 1686), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        font = find_font()

        # 中央左右位置
        draw.text((500, 750), "台北市", fill=(0, 0, 0), font=font)
        draw.text((1550, 750), "新北市", fill=(0, 0, 0), font=font)

        img.save(RICH_MENU_IMAGE_PATH)

def setup_line_rich_menu(line_bot_api: LineBotApi):
    # 刪除所有舊的 Rich Menu（避免重複）
    menus_to_delete = line_bot_api.get_rich_menu_list()
    for menu in menus_to_delete:
        print(f"[INFO] 刪除舊 Rich Menu: {menu.name} ({menu.rich_menu_id})")
        line_bot_api.delete_rich_menu(menu.rich_menu_id)

    print("[INFO] 設定 LINE Rich Menu 中...")

    new_menu = RichMenu(
        size={"width": 2500, "height": 1686},
        selected=True,
        name="Weather Menu",
        chat_bar_text="點我查天氣",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=1250, height=1686),
                action=MessageAction(label="台北市", text="我想要台北的氣象資訊")
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1251, y=0, width=1250, height=1686),
                action=MessageAction(label="新北市", text="我想要新北的氣象資訊")
            )
        ]
    )

    menu_id = line_bot_api.create_rich_menu(new_menu)
    print(f"[INFO] ✅ Rich Menu 建立成功：{menu_id}")

    try:
        with open(RICH_MENU_IMAGE_PATH, 'rb') as f:
            line_bot_api.set_rich_menu_image(menu_id, 'image/jpeg', f)
        print("[INFO] ✅ 圖片上傳成功")
    except Exception as e:
        print(f"[ERROR] 圖片上傳失敗: {e}")

    line_bot_api.set_default_rich_menu(menu_id)
    print("[INFO] ✅ 已設為預設 Rich Menu")

if __name__ == "__main__":
    ensure_rich_menu_image_exists()
