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
        # 定位瑞穗鄉
        target_loc = next((l for l in locations if l['LocationName'] == '瑞穗鄉'), None)
        
        # 3. 提取天氣元素 (根據你的氣象.txt，Key 是中文)
        # 我們將 ElementName 對應到其 Time 列表
        elements = {e['ElementName']: e['Time'] for e in target_loc['WeatherElement']}
        
        # 4. 提醒語邏輯 (a | b | c 組合)
        def get_tips(temp, pop, wx):
            t, p = int(temp), int(pop)
            # a: 天氣狀況
            if p >= 70: a = ["大雨預警 ⛈️", "記得帶大傘 ☔", "外頭雨很大 🌧️"]
            elif p >= 30 or "雨" in wx: a = ["帶把小傘 🌂", "偶有陣雨 🌦️", "天空陰陰的 ☁️"]
            else: a = ["天氣晴朗 ✨", "陽光普照 ☀️", "適合出門 🏃"]

            # b: 穿衣建議
            if t <= 16: b = ["穿厚外套 🧥", "注意保暖 🧤", "冷氣團來襲 ❄️"]
            elif t <= 22: b = ["加件薄長袖 🌸", "涼爽舒適 👕", "微涼好天氣 🧣"]
            else: b = ["短袖出動 👕", "注意防曬 🕶️", "多喝水防暑 🥤"]

            # c: 瑞穗特色提醒
            c = ["小心小黑蚊 🦟", "加油喔！💪", "瑞穗日常 🍊", "保持好心情 ✨", "一切順利 ✨"]

            return f"💡 {random.choice(a)} | {random.choice(b)} | {random.choice(c)}"

        # 5. 組裝訊息
        msg_parts = [f"🍊 【瑞穗鄉】精細預報 (3hr)", "===================="]
        
        # 抓取接下來的三個時段 (i=0, 1, 2)
        for i in range(3):
            # 根據 041 規格，溫度是每 3 小時一筆，時間欄位是 DataTime
            t_data = elements['溫度'][i]
            dt = t_data['DataTime']
            # 格式化時間：03/15 12:00
            display_time = f"{dt[5:10].replace('-', '/')} {dt[11:16]}"
            
            # 提取數值
            temp = t_data['ElementValue'][0]['Temperature']
            wx = elements['天氣現象'][i]['ElementValue'][0]['Weather']
            
            # 💡 技術重點：降雨機率在 041 API 中通常是 6 小時一格
            # 所以溫度的第 0, 1 格對應降雨的第 0 格；第 2, 3 格對應第 1 格 (使用 i // 2)
            pop = elements['降雨機率'][i // 2]['ElementValue'][0]['ProbabilityOfPrecipitation']
            
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
        print("✅ 成功發送三小時精細預報！")

    except Exception as e:
        print(f"💥 運行出錯: {e}")

if __name__ == "__main__":
    get_weather()