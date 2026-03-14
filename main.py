import os
import requests
import random
import urllib3
from datetime import datetime

# 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')
    group_id = os.getenv('GROUP_ID')

    # 1. 抓取花蓮精細預報 (F-D0047-041) - 3小時一格
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-041?Authorization={cwa_key}"
    
    try:
        res = requests.get(url, verify=False, timeout=20).json()
        locations = res['records']['Locations'][0]['Location']
        target_loc = next((l for l in locations if l['LocationName'] == '瑞穗鄉'), None)
        
        # 3. 提取天氣元素 (041 API 的 Key 通常是 T, Wx, PoP6h)
        elements = {e['ElementName']: e['Time'] for e in target_loc['WeatherElement']}
        
        # 4. 加強版簡潔提醒語 (a | b | c 組合)
        def get_tips(temp, pop, wx):
            t, p = int(temp), int(pop)
            # a: 天氣感官
            if p >= 70: a = ["大雨預警 ⛈️", "記得帶大傘 ☔", "外頭雨很大 🌧️"]
            elif p >= 30 or "雨" in wx: a = ["帶把小傘 🌂", "偶有陣雨 🌦️", "天空陰陰的 ☁️"]
            else: a = ["天氣晴朗 ✨", "陽光普照 ☀️", "適合出門 🏃"]

            # b: 穿搭
            if t <= 16: b = ["穿厚外套 🧥", "注意保暖 🧤", "冷氣團來襲 ❄️"]
            elif t <= 22: b = ["加件薄長袖 🌸", "涼爽舒適 👕", "微涼好天氣 🧣"]
            else: b = ["短袖出動 👕", "注意防曬 🕶️", "多喝水防暑 🥤"]

            # c: 在地關懷
            c = ["小心小黑蚊 🦟", "加油喔！💪", "瑞穗日常 🍊", "保持好心情 ✨", "一切順利 ✨"]

            return f"💡 {random.choice(a)} | {random.choice(b)} | {random.choice(c)}"

        # 5. 組裝訊息內容
        msg_parts = [f"🍊 【瑞穗鄉】精細預報 (3hr)", "===================="]
        
        # 抓取前 3 個時段
        for i in range(3):
            # 041 的溫度是用 DataTime
            t_data = elements['T'][i]
            dt = t_data['DataTime']
            display_time = f"{dt[5:10].replace('-', '/')} {dt[11:16]}"
            
            temp = t_data['ElementValue'][0]['Temperature']
            wx = elements['Wx'][i]['ElementValue'][0]['Weather']
            # PoP6h 是 6 小時降雨機率，每兩格 3 小時才換一次，我們用 // 2 來對應
            pop = elements['PoP6h'][i // 2]['ElementValue'][0]['ProbabilityOfPrecipitation']
            
            msg_parts.append(f"🕒 {display_time}")
            msg_parts.append(f"☁️ {wx} | 🌡️ {temp}°C | ☔ {pop}%")
            msg_parts.append(get_tips(temp, pop, wx))
            if i < 2: msg_parts.append("-" * 15)

        final_msg = "\n".join(msg_parts)

        # 6. LINE 推播
        line_url = 'https://api.line.me/v2/bot/message/push'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"to": group_id, "messages": [{"type": "text", "text": final_msg}]}
        
        requests.post(line_url, headers=headers, json=payload)
        print("✅ 訊息發送成功！")

    except Exception as e:
        print(f"💥 運行出錯: {e}")

if __name__ == "__main__":
    get_weather()