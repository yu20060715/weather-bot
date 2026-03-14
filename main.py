import os
import requests
import random
import urllib3

# 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_weather():

    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')
    group_id = os.getenv('GROUP_ID')

    # 1. 抓取花蓮全縣資料 (F-D0047-043)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-043?Authorization={cwa_key}"
    
    try:
        # 這裡加入 verify=False 防止 GitHub 環境報 SSL 錯誤
        res = requests.get(url, verify=False, timeout=20).json()
        
        # 2. 定位瑞穗鄉
        locations = res['records']['Locations'][0]['Location']
        target_loc = next((l for l in locations if l['LocationName'] == '瑞穗鄉'), None)
        
        # 3. 提取天氣元素並轉為中文索引字典
        elements = {e['ElementName']: e['Time'] for e in target_loc['WeatherElement']}
        
        # 4. 提醒語邏輯函數
        def get_tips(temp, pop, weather):
            tips = []
            t, p = int(temp), int(pop)
            if p >= 30 or "雨" in weather:
                tips.append(random.choice(["外面下雨了，記得帶傘以免變落湯雞 ☔", "出門記得帶傘，瑞穗的雨總是來的很突然 🌧️"]))
            elif p >= 10:
                tips.append("天色陰陰的，保險起見帶把摺疊傘吧 🌂")
            
            if t <= 15:
                tips.append(random.choice(["氣溫很低，要穿厚外套喔 🧣", "真的冷，瑞穗的風不是開玩笑的 🧥"]))
            elif t <= 19:
                tips.append("微涼的天氣，穿件薄長袖比較舒服 🌸")
            elif t >= 28:
                tips.append("太陽很大，記得多喝水避免中暑 ☀️")
            
            if not tips: tips.append("天氣很棒，保持心情愉快！✨")
            return "\n 💡 提醒您: " + "\n        ".join(tips)

        # 5. 組裝訊息內容
        raw_date = elements['平均溫度'][0]['StartTime'][:10].replace('-', '/')
        msg_parts = [f"🍊 【瑞穗鄉】({raw_date}) 天氣預報解析", "===================="]

        for i in range(2): # 只取白天、晚上兩個時段
            start_time = elements['平均溫度'][i]['StartTime'][11:16]
            display_time = "06:00 - 18:00 (白天)" if start_time == "06:00" else "18:00 - 06:00 (晚上)"
            
            t = elements['平均溫度'][i]['ElementValue'][0]['Temperature']
            wx = elements['天氣現象'][i]['ElementValue'][0]['Weather']
            pop = elements['12小時降雨機率'][i]['ElementValue'][0]['ProbabilityOfPrecipitation']
            
            msg_parts.append(f"🕒 時段：{display_time}")
            msg_parts.append(f"☁️ 狀況：{wx}")
            msg_parts.append(f"🌡️ 氣溫：{t}°C")
            msg_parts.append(f"☔ 降雨：{pop}%")
            msg_parts.append(get_tips(t, pop, wx))
            if i == 0: msg_parts.append("-" * 20)

        final_msg = "\n".join(msg_parts)

        # 6. LINE 推播 (Broadcast)
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": final_msg}]}
        
        response = requests.post(line_url, headers=headers, json=payload)
        print(f"✅ 發送狀態: {response.status_code}")

    except Exception as e:
        print(f"💥 運行出錯: {e}")

if __name__ == "__main__":
    get_weather()