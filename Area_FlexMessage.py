new_taipei_districts = [
    "板橋區", "三重區", "中和區", "永和區", "新莊區", "新店區", "樹林區", "鶯歌區", "三峽區",
    "淡水區", "汐止區", "瑞芳區", "土城區", "蘆洲區", "五股區", "泰山區", "林口區", "深坑區",
    "石碇區", "坪林區", "三芝區", "石門區", "八里區", "平溪區", "雙溪區", "貢寮區", "金山區",
    "萬里區", "烏來區"
]

taipei_districts = [
    "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區",
    "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"
]

def generate_flex_bubbles(city: str, districts: list):
    """
    生成美觀的行政區選擇 Flex Message
    
    Args:
        city (str): 城市名稱 ('台北' 或 '新北')
        districts (list): 行政區名稱列表
        
    Returns:
        dict: LINE Flex Message Carousel 格式
    """
    from math import ceil
    
    # 定義顏色和風格
    colors = {
        "台北": {
            "header_bg": "#007FFF",  # 深藍色
            "header_text": "#FFFFFF",  # 白色
            "button_color": "#007FFF",  # 深藍色
            "icon": "🏙️"  # 台北市圖標
        },
        "新北": {
            "header_bg": "#4CAF50",  # 綠色
            "header_text": "#FFFFFF",  # 白色
            "button_color": "#2E7D32",  # 深綠色
            "icon": "🌄"  # 新北市圖標
        }
    }
    
    # 計算需要幾頁
    items_per_page = 12  # 每頁 12 個按鈕 (3 x 4)
    total_pages = ceil(len(districts) / items_per_page)
    
    bubbles = []
    for page in range(total_pages):
        # 獲取當前頁的行政區
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(districts))
        current_districts = districts[start_idx:end_idx]
        
        # 創建行
        rows = []
        for i in range(0, len(current_districts), 3):
            row_districts = current_districts[i:i+3]
            
            # 每行最多 3 個按鈕
            row_buttons = []
            for district in row_districts:
                button = {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": district,
                        "text": f"我想要{city}{district}的氣象資訊"
                    },
                    "style": "primary",
                    "color": colors[city]["button_color"],
                    "margin": "sm"
                }
                row_buttons.append(button)
            
            # 如果這行不滿 3 個按鈕，用 filler 填充
            while len(row_buttons) < 3:
                row_buttons.append({"type": "filler"})
            
            # 將這一行添加到內容中
            row = {
                "type": "box",
                "layout": "horizontal",
                "contents": row_buttons,
                "spacing": "md",
                "margin": "md"
            }
            rows.append(row)
        
        # 頁碼提示文字
        page_indicator = {
            "type": "text",
            "text": f"{page+1}/{total_pages}",
            "size": "xs",
            "color": "#888888",
            "align": "center",
            "margin": "md"
        }
        
        # 底部提示文字
        footer_text = "請選擇行政區"
        if total_pages > 1:
            if page == 0:
                footer_text += " (往左滑動查看更多)"
            elif page == total_pages - 1:
                footer_text += " (往右滑動查看前頁)"
            else:
                footer_text += " (左右滑動查看更多)"
        
        # 創建 bubble
        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": colors[city]["icon"],
                                "size": "sm",
                                "weight": "bold",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": f"{city}市氣象查詢",
                                "weight": "bold",
                                "size": "lg",
                                "color": colors[city]["header_text"],
                                "align": "center",
                                "gravity": "center",
                                "flex": 4
                            }
                        ],
                        "backgroundColor": colors[city]["header_bg"],
                        "cornerRadius": "md",
                        "paddingAll": "md"
                    }
                ],
                "paddingAll": "none",
                "backgroundColor": colors[city]["header_bg"]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": rows + [page_indicator],
                "backgroundColor": "#FFFFFF",
                "paddingAll": "md"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": footer_text,
                        "size": "sm",
                        "color": "#888888",
                        "align": "center"
                    }
                ]
            },
            "styles": {
                "header": {
                    "backgroundColor": colors[city]["header_bg"]
                },
                "body": {
                    "backgroundColor": "#FFFFFF"
                },
                "footer": {
                    "backgroundColor": "#F5F5F5"
                }
            }
        }
        
        bubbles.append(bubble)
    
    return {
        "type": "carousel",
        "contents": bubbles
    }

# 測試用（如果直接執行此文件）
if __name__ == "__main__":
    import json
    
    # 測試台北市
    taipei_flex = generate_flex_bubbles("台北", taipei_districts)
    print("台北市 Flex Message 測試:")
    print(json.dumps(taipei_flex, ensure_ascii=False, indent=2)[:200] + "...")
    
    # 測試新北市
    newtaipei_flex = generate_flex_bubbles("新北", new_taipei_districts)
    print("\n新北市 Flex Message 測試:")
    print(json.dumps(newtaipei_flex, ensure_ascii=False, indent=2)[:200] + "...")
    
    print("\n測試完成，Flex Message 格式生成正常")