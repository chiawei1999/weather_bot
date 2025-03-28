import requests
from dotenv import dotenv_values
from datetime import datetime, timedelta
import json

def fetch_weather(location="淡水區"):
    config = dotenv_values(".env")
    authorization = config.get("Authorization")

    # 判斷台北或新北資料集
    if location in [
        "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區",
        "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"
    ]:
        dataset_id = "F-D0047-061"  # 台北市
        city = "臺北市"
    else:
        dataset_id = "F-D0047-069"  # 新北市
        city = "新北市"

    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{dataset_id}"
    headers = {
        "Authorization": authorization,
        "User-Agent": "Mozilla/5.0"
    }

    # 不使用locationName參數，獲取全部資料
    params = {}

    print(f"[INFO] 正在獲取 {city} {location} 的天氣資料...")

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"[INFO] 錯誤狀態碼 {response.status_code}")
        return None

    try:
        data = response.json()
        
        # 基本API回應檢查
        if not data.get("success") == "true":
            print(f"[INFO] API回應不成功")
            return None
            
        if "records" not in data:
            print(f"[INFO] API回應中沒有records鍵")
            return None
            
        if "Locations" not in data["records"] or not data["records"]["Locations"]:
            print(f"[INFO] records中沒有Locations陣列或為空")
            return None
            
        # 根據API實際結構，獲取第一個Locations項
        locations_container = data["records"]["Locations"][0]
        
        if "Location" not in locations_container:
            print(f"[INFO] Locations[0]中沒有Location鍵")
            return None
            
        # 獲取所有Location(行政區)
        district_list = locations_container["Location"]
        
        # 尋找目標行政區
        target_district = None
        
        # 完全匹配
        for district in district_list:
            if district["LocationName"] == location:
                target_district = district
                break
                
        # 若沒找到，嘗試其他匹配方式
        if not target_district:
            for district in district_list:
                if district["LocationName"].endswith(location):
                    target_district = district
                    break
        
        if not target_district and len(district_list) > 0:
            # 若還是找不到，使用第一個行政區
            target_district = district_list[0]
            
        if not target_district:
            print(f"[INFO] 無法找到任何行政區資料")
            return None
            
        # 轉換為原始代碼預期的格式
        result = {
            "success": "true",
            "records": {
                "location": [target_district]
            }
        }
        return result
            
    except Exception as e:
        print(f"[INFO] 數據處理錯誤: {e}")
        return None

def parse_weather(data, location):
    try:
        if not data or data.get("success") != "true":
            return "API 回應不成功或為空"

        locations = data["records"].get("location", [])
        if not locations:
            return f"在 API 回應中找不到地點資料"
        
        # 使用第一个返回的location
        target_location = locations[0]
        actual_location = target_location.get("LocationName", location)
        print(f"[INFO] 使用地點: {actual_location}")
        
        # 檢查天氣要素
        weather_elements = target_location.get("WeatherElement", [])
        if not weather_elements:
            return f"找不到天氣要素資料"
            
        # 使用天氣現象與綜合描述
        wx_element = None  # 天氣現象
        pop_element = None  # 降雨機率
        ci_element = None  # 舒適度
        temp_element = None  # 溫度
        
        # 尋找各個天氣要素
        for element in weather_elements:
            element_name = element.get("ElementName")
            if element_name == "天氣現象":
                wx_element = element
            elif element_name == "3小時降雨機率":
                pop_element = element
            elif element_name == "舒適度指數":
                ci_element = element
            elif element_name == "溫度":
                temp_element = element
        
        # 獲取最高最低溫度
        min_temp = None
        max_temp = None
        if temp_element and "Time" in temp_element:
            temperature_data = temp_element["Time"]
            if temperature_data:
                temps = []
                for time_point in temperature_data:
                    if "ElementValue" in time_point and time_point["ElementValue"]:
                        for val in time_point["ElementValue"]:
                            if "Temperature" in val:
                                try:
                                    temps.append(int(val["Temperature"]))
                                except:
                                    pass
                if temps:
                    min_temp = min(temps)
                    max_temp = max(temps)
        
        if not wx_element or "Time" not in wx_element or not wx_element["Time"]:
            return f"找不到有效的天氣現象資料"
            
        # 獲取最新的天氣資訊
        current_wx = wx_element["Time"][0]
        current_weather = "未知"
        
        if "ElementValue" in current_wx and current_wx["ElementValue"]:
            for val in current_wx["ElementValue"]:
                if "Weather" in val:
                    current_weather = val["Weather"]
                    break
        
        # 獲取降雨機率
        rain_prob = "未知"
        if pop_element and "Time" in pop_element and pop_element["Time"]:
            current_pop = pop_element["Time"][0]
            if "ElementValue" in current_pop and current_pop["ElementValue"]:
                for val in current_pop["ElementValue"]:
                    if "ProbabilityOfPrecipitation" in val:
                        rain_prob = val["ProbabilityOfPrecipitation"]
                        break
        
        # 獲取舒適度
        comfort = "未知"
        if ci_element and "Time" in ci_element and ci_element["Time"]:
            current_ci = ci_element["Time"][0]
            if "ElementValue" in current_ci and current_ci["ElementValue"]:
                for val in current_ci["ElementValue"]:
                    if "ComfortIndexDescription" in val:
                        comfort = val["ComfortIndexDescription"]
                        break
        
        # 使用現在時間作為資料時間
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 構建摘要資訊
        summary = f"📍 地點：{actual_location}\n"
        summary += f"🕒 資料更新時間：{current_time}\n\n"
        summary += f"🌤 天氣：{current_weather}\n"
        
        if min_temp is not None and max_temp is not None:
            summary += f"🌡 溫度：{min_temp}°C ~ {max_temp}°C\n"
        
        summary += f"💧 降雨機率：{rain_prob}%\n"
        summary += f"😊 舒適度：{comfort}\n"
        
        # 添加未來天氣預報 - 只選擇早上9點的資料
        summary += "\n🔮 未來天氣預報：\n"
        
        # 收集所有時間點
        all_wx_times = []
        if wx_element and "Time" in wx_element:
            for wx_time in wx_element["Time"]:
                start_time = wx_time.get("StartTime", "")
                end_time = wx_time.get("EndTime", "")
                weather = "未知"
                
                # 只尋找包含早上9點的時段
                if "09:00:00" in start_time:
                    if "ElementValue" in wx_time and wx_time["ElementValue"]:
                        for val in wx_time["ElementValue"]:
                            if "Weather" in val:
                                weather = val["Weather"]
                                break
                    
                    # 解析日期以便排序
                    try:
                        start_datetime = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S+08:00")
                        forecast_date = start_datetime.strftime("%m/%d")
                        
                        # 尋找對應的降雨機率
                        rain_prob_for_time = "未知"
                        if pop_element and "Time" in pop_element:
                            for pop_time in pop_element["Time"]:
                                pop_start = pop_time.get("StartTime", "")
                                pop_end = pop_time.get("EndTime", "")
                                
                                # 找出時間範圍包含9點的降雨機率
                                if (pop_start <= start_time <= pop_end or 
                                    pop_start <= end_time <= pop_end or
                                    (start_time <= pop_start and pop_end <= end_time)):
                                    if "ElementValue" in pop_time and pop_time["ElementValue"]:
                                        for val in pop_time["ElementValue"]:
                                            if "ProbabilityOfPrecipitation" in val:
                                                rain_prob_for_time = val["ProbabilityOfPrecipitation"]
                                                break
                                    break
                        
                        # 收集這一天的溫度
                        temp_for_time = "未知"
                        if temp_element and "Time" in temp_element:
                            for temp_time in temp_element["Time"]:
                                temp_datetime = temp_time.get("DataTime", "")
                                if "09:00:00" in temp_datetime and temp_datetime.startswith(start_datetime.strftime("%Y-%m-%d")):
                                    if "ElementValue" in temp_time and temp_time["ElementValue"]:
                                        for val in temp_time["ElementValue"]:
                                            if "Temperature" in val:
                                                temp_for_time = val["Temperature"]
                                                break
                                    break
                        
                        all_wx_times.append({
                            "date": start_datetime,
                            "date_str": forecast_date,
                            "weather": weather,
                            "rain_prob": rain_prob_for_time,
                            "temp": temp_for_time
                        })
                    except Exception as e:
                        pass
        
        # 排序並選取接下來3天
        all_wx_times.sort(key=lambda x: x["date"])
        
        # 只取前3天
        for i, forecast in enumerate(all_wx_times[:3]):
            date_str = forecast["date_str"]
            weather = forecast["weather"]
            rain_prob = forecast["rain_prob"]
            temp = forecast["temp"]
            
            # 添加溫度信息（如果有）
            temp_text = f", 🌡 {temp}°C" if temp != "未知" else ""
            
            summary += f"• {date_str} 上午9點: {weather}{temp_text}, ☔ {rain_prob}%\n"
        
        return summary

    except Exception as e:
        return f"資料解析失敗：{e}"

# 測試用
if __name__ == "__main__":
    location = "樹林區"  # 測試用的行政區
    data = fetch_weather(location)
    if data:
        result = parse_weather(data, location)
        print(result)
    else:
        print(f"無法獲取 {location} 的天氣資料")