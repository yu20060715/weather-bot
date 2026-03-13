import os
import requests
import random
import traceback

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 加上 locationName=瑞穗鄉，讓氣象署只回傳瑞穗的資料，降低結構複雜度
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}&locationName=瑞穗鄉"
    
    try:
        res = requests.get(url).json()
        
        # 【極致防錯解析法】不再硬抓 'locations'，而是用 .get() 柔性讀取
        records = res.get('records', {})
        locations_list = records.get('locations', [])
        
        # 應對氣象署可能將 locations 改名為 location 的情況
        location_list = []
        if locations_list:
            location_list = locations_list[0].get('location', [])
        elif 'location' in records:
            location_list = records.get('location', [])

        if not location_list:
            print("⚠️ API 沒有回傳地點資料！請確認氣象署 Token 是否有效。")
            print(f"API 實際回傳內容: {str(res)[:200]}")
            return

        # 抓取瑞穗鄉
        target_loc = location_list[0] # 因為網址已經指定瑞穗鄉，第一個就是了
        elements = target_loc.get('weatherElement', [])
        
        # 將天氣元素整理成好讀的字典
        weather_data = {e['elementName']: e.get('time', []) for e in elements}
        
        # 準備三個時段的資料
        wx_list = weather_data.get('Wx', [])       # 天氣現象
        pop_list = weather_data.get('PoP12h', [])  # 降雨機率
        t_list = weather_data.get('T', [])         # 溫度
        
        msg_lines = ["🍊 【瑞穗鄉】當日天氣預報 🍊", "===================="]
        
        max_pop = 0
        min_temp = 100
        max_temp = 0
        
        # 取未來三個時段 (通常是早、中/晚、明晨)
        loop_count = min(3, len(wx_list), len(t_list))
        
        for i in range(loop_count):
            # 抓取並格式化時間 (例如把 2024-03-15 06:00:00 變成 03-15 06:00)
            start_time = wx_list[i].get('startTime', '')[5:16]
            desc = wx_list[i]['elementValue'][0]['value']
            temp = t_list[i]['elementValue'][0]['value']
            
            # 降雨機率有時陣列長度不一致，用 try 保護
            try:
                pop = pop_list[i]['elementValue'][0]['value']
                if pop.isdigit():
                    max_pop = max(max_pop, int(pop))
            except:
                pop = "0"
                
            min_temp = min(min_temp, int(temp))
            max_temp = max(max_temp, int(temp))

            msg_lines.append(f"🕒 {start_time}")
            msg_lines.append(f"☁️ 狀況：{desc}")
            msg_lines.append(f"🌡️ 氣溫：{temp}°C | ☔ 降雨：{pop}%")
            msg_lines.append("--------------------")

        # 【趣味提醒邏輯 (亂數)】
        msg_lines.append("💡 【溫馨提醒】")
        
        # 1. 下雨提醒
        rain_phrases = [
            "出門記得帶把傘，別淋成落湯雞啦！☔", 
            "今天可能會下雨，傘是你的好夥伴！☂️", 
            "降雨機率偏高，包包裡塞把傘準沒錯！🌧️"
        ]
        sun_phrases = [
            "今天天氣不錯，適合出門走走！☀️", 
            "降雨機率低，是個乾爽的好日子！😎", 
            "沒什麼雨，盡情享受今天吧！✨"
        ]
        
        if max_pop >= 30:
            msg_lines.append(random.choice(rain_phrases))
        else:
            msg_lines.append(random.choice(sun_phrases))
            
        # 2. 溫度提醒
        cold_phrases = [
            "天氣有點涼，記得多穿件外套保暖喔！🧣", 
            "冷冷的，穿厚點別感冒了！🧥", 
            "氣溫偏低，喝杯熱水暖暖身子吧！☕"
        ]
        hot_phrases = [
            "今天蠻熱的，記得多喝水補充水分！🥤", 
            "氣溫偏高，出門注意防曬喔！🕶️", 
            "有點熱，穿透氣一點比較舒服！👕"
        ]
        nice_phrases = [
            "氣溫很舒適，是很棒的一天！🌸", 
            "不冷不熱，真是個好天氣！🍃"
        ]
        
        if min_temp <= 20:
            msg_lines.append(random.choice(cold_phrases))
        elif max_temp >= 30:
            msg_lines.append(random.choice(hot_phrases))
        else:
            msg_lines.append(random.choice(nice_phrases))

        final_msg = "\n".join(msg_lines)

        # 廣播模式：直接發送到機器人所在的群組
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": final_msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        
        if r.status_code == 200:
            print("✅ 成功發送天氣預報到 LINE 群組！")
        else:
            print(f"❌ LINE 發送失敗: {r.status_code}, {r.text}")

    except Exception as e:
        print("=== 🚨 解析發生嚴重錯誤 ===")
        print(traceback.format_exc())

if __name__ == "__main__":
    get_weather()