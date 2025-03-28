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
    # LINE 每個 bubble 最多 12 個按鈕，所以我們分頁處理
    from math import ceil
    bubbles = []
    for i in range(0, len(districts), 12):
        contents = [
            {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": district,
                    "text": f"我想要{city}{district}的氣象資訊"
                }
            } for district in districts[i:i+12]
        ]

        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [{"type": "text", "text": f"{city}行政區選擇", "weight": "bold", "size": "lg"}]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": contents
            }
        }
        bubbles.append(bubble)

    return {
        "type": "carousel",
        "contents": bubbles
    }
