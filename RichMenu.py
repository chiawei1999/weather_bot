from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

RICH_MENU_IMAGE_PATH = "rich_menu_image.jpg"

def create_beautiful_rich_menu():
    # 創建底圖 (2500x1686 是 LINE Rich Menu 的標準尺寸)
    img = Image.new("RGB", (2500, 1686), color=(240, 240, 245))
    draw = ImageDraw.Draw(img)
    
    # 嘗試載入適合的字型
    def find_font(size):
        font_paths = [
            # 中文字型路徑 (Windows, Mac, Linux)
            "C:/Windows/Fonts/msjh.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            # 可以添加更多備選字型路徑
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
                
        # 如果找不到適合字型，返回默認字型
        print("[WARNING] 找不到中文字型，使用預設字體")
        return ImageFont.load_default()
    
    # 載入字型
    title_font = find_font(130)
    subtitle_font = find_font(60)
    
    # 畫分隔線
    draw.line([(1250, 0), (1250, 1686)], fill=(200, 200, 210), width=5)
    
    # 左側 - 台北市
    # 創建漸層背景
    for i in range(1250):
        # 漸變藍色 (從淺到深)
        color = (120 - int(i/12), 180 - int(i/25), 240 - int(i/50))
        draw.line([(i, 0), (i, 1686)], fill=color)
    
    # 天氣圖示 - 太陽
    sun_x, sun_y = 400, 450
    sun_radius = 120
    # 太陽外圈
    draw.ellipse((sun_x-sun_radius, sun_y-sun_radius, sun_x+sun_radius, sun_y+sun_radius), 
                 fill=(255, 215, 0))
    # 太陽內圈
    draw.ellipse((sun_x-sun_radius+20, sun_y-sun_radius+20, sun_x+sun_radius-20, sun_y+sun_radius-20), 
                 fill=(255, 240, 0))
    # 畫太陽光芒
    for angle in range(0, 360, 30):
        import math
        rads = math.radians(angle)
        end_x = sun_x + (sun_radius + 80) * math.cos(rads)
        end_y = sun_y + (sun_radius + 80) * math.sin(rads)
        start_x = sun_x + (sun_radius + 10) * math.cos(rads)
        start_y = sun_y + (sun_radius + 10) * math.sin(rads)
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(255, 200, 0), width=12)
    
    # 建築物剪影 (先繪製，這樣文字會在上層)
    buildings_poly = [
        (50, 1300),   # 左下
        (150, 1300),  # 建築1底部
        (150, 1100),  # 建築1頂部
        (230, 1100),  # 建築1到2
        (230, 1000),  # 建築2頂部
        (350, 1000),  # 建築2到3
        (350, 1150),  # 建築3頂部
        (450, 1150),  # 建築3到4
        (450, 900),   # 建築4頂部 (101大樓)
        (550, 900),   # 建築4到5
        (550, 1050),  # 建築5頂部
        (650, 1050),  # 建築5到6
        (650, 1200),  # 建築6頂部
        (750, 1200),  # 建築6到7
        (750, 1000),  # 建築7頂部
        (850, 1000),  # 建築7到8
        (850, 1150),  # 建築8頂部
        (950, 1150),  # 建築8到9
        (950, 1050),  # 建築9頂部
        (1050, 1050), # 建築9到10
        (1050, 1250), # 建築10頂部
        (1150, 1250), # 建築10到11
        (1150, 1300), # 建築11頂部=底部
        (50, 1300),   # 回到起點
    ]
    draw.polygon(buildings_poly, fill=(30, 30, 70))
    
    # 台北市標題 (文字在建築物之上)
    taipei_title = "台北市"
    title_w, title_h = draw.textsize(taipei_title, font=title_font) if hasattr(draw, 'textsize') else (500, 130)
    draw.text((625-title_w//2, 450), taipei_title, fill=(255, 255, 255), font=title_font)
    
    # 副標題
    subtitle = "天氣查詢"
    subtitle_w = draw.textsize(subtitle, font=subtitle_font)[0] if hasattr(draw, 'textsize') else 300
    draw.text((625-subtitle_w//2, 600), subtitle, fill=(255, 255, 255), font=subtitle_font)
    
    # 右側 - 新北市
    for i in range(1250, 2500):
        # 漸變綠色
        green_val = 120 - int((i-1250)/12)
        color = (100 - int((i-1250)/25), 180 - int((i-1250)/25), green_val)
        draw.line([(i, 0), (i, 1686)], fill=color)
    
    # 雲朵 (用多個圓形組合)
    # 雲朵中心
    cloud_x, cloud_y = 1800, 450
    # 主要雲體
    for offset in [(0, 0), (-120, 20), (120, 30), (-30, -60), (50, -70), (-200, -20), (200, -10)]:
        size = 100 + abs(offset[0]//4)
        draw.ellipse((cloud_x+offset[0]-size, cloud_y+offset[1]-size, 
                     cloud_x+offset[0]+size, cloud_y+offset[1]+size), 
                     fill=(245, 245, 250))
    
    # 新北市標題
    newtaipei_title = "新北市"
    title_w, title_h = draw.textsize(newtaipei_title, font=title_font) if hasattr(draw, 'textsize') else (500, 130)
    draw.text((1875-title_w//2, 750), newtaipei_title, fill=(255, 255, 255), font=title_font)
    
    # 副標題
    subtitle = "天氣查詢"
    subtitle_w = draw.textsize(subtitle, font=subtitle_font)[0] if hasattr(draw, 'textsize') else 300
    draw.text((1875-subtitle_w//2, 900), subtitle, fill=(255, 255, 255), font=subtitle_font)
    
    # 山脈剪影 (新北市)
    mountain_poly = [
        (1250, 1300),   # 左下
        (1400, 1100),   # 山1
        (1500, 1200),   # 山谷1
        (1650, 950),    # 山2 (較高)
        (1750, 1150),   # 山谷2
        (1950, 1000),   # 山3
        (2100, 1200),   # 山谷3
        (2300, 1050),   # 山4
        (2500, 1250),   # 右緣
        (2500, 1300),   # 右下
    ]
    draw.polygon(mountain_poly, fill=(30, 60, 40))
    
    # 加入雨滴
    from random import randint
    for _ in range(40):
        x = randint(1400, 2300)
        y = randint(500, 700)
        length = randint(30, 60)
        draw.line([(x, y), (x-5, y+length)], fill=(220, 240, 255), width=3)
    
    # 套用模糊效果，讓畫面更柔和
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    # 保存圖片
    img.save(RICH_MENU_IMAGE_PATH)
    print(f"[INFO] ✅ 美化版 Rich Menu 已保存至 {RICH_MENU_IMAGE_PATH}")
    
    return RICH_MENU_IMAGE_PATH

# 修改 ensure_rich_menu_image_exists 函數，使用新的美化圖片
def ensure_rich_menu_image_exists():
    if not os.path.exists(RICH_MENU_IMAGE_PATH):
        print("[INFO] 正在建立美化版 rich_menu_image.jpg...")
        create_beautiful_rich_menu()
    else:
        print(f"[INFO] Rich Menu 圖片已存在: {RICH_MENU_IMAGE_PATH}")
def setup_line_rich_menu(line_bot_api):
    """
    設置LINE的Rich Menu，包括創建、上傳圖片和設為默認
    
    Args:
        line_bot_api: LINE Bot SDK的API實例
    """
    from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize, PostbackAction, MessageAction
    import os
    
    # 確保圖片已存在
    ensure_rich_menu_image_exists()
    
    # 創建Rich Menu物件
    # Rich Menu尺寸: 2500x1686 (全屏)
    rich_menu = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=True,  # 默認顯示
        name="Weather Menu",  # 選單名稱
        chat_bar_text="氣象查詢",  # 底部文字
        areas=[
            # 左側區域 - 台北市
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=1250, height=1686),
                action=MessageAction(label="台北市", text="我想要台北的氣象資訊")
            ),
            # 右側區域 - 新北市
            RichMenuArea(
                bounds=RichMenuBounds(x=1250, y=0, width=1250, height=1686),
                action=MessageAction(label="新北市", text="我想要新北的氣象資訊")
            )
        ]
    )
    
    # 創建Rich Menu
    try:
        rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu)
        print(f"[INFO] ✅ 成功創建Rich Menu, ID: {rich_menu_id}")
        
        # 上傳圖片
        with open(RICH_MENU_IMAGE_PATH, 'rb') as f:
            line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg", f)
        print(f"[INFO] ✅ 成功上傳Rich Menu圖片")
        
        # 設為默認
        line_bot_api.set_default_rich_menu(rich_menu_id)
        print(f"[INFO] ✅ 成功設置默認Rich Menu")
        
    except Exception as e:
        print(f"[ERROR] 設置Rich Menu失敗: {e}")
# 如果直接執行此檔案，測試建立圖片
if __name__ == "__main__":
    create_beautiful_rich_menu()