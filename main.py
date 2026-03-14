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
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-041?Authorization={cwa_key}"
    
    try:
        # 這裡加入 verify=False 防止 GitHub 環境報 SSL 錯誤
        res = requests.get(url, verify=False, timeout=20).json()
        
        # 2. 定位瑞穗鄉
        locations = res['records']['Locations'][0]['Location']
        target_loc = next((l for l in locations if l['LocationName'] == '瑞穗鄉'), None)
        
        # 3. 提取天氣元素並轉為中文索引字典
        elements = {e['ElementName']: e['Time'] for e in target_loc['WeatherElement']}
        
        # 4. 加強版提醒語邏輯函數 (a + b + c 組合法)
        def get_tips(temp, pop, wx):
            t, p = int(temp), int(pop)
            # a: 天氣短評
            if p >= 70: a = ["大雨預警 ⛈️", "記得帶大傘 ☔", "外頭雨很大 🌧️"]
            elif p >= 30: a = ["帶把小傘 🌂", "偶有陣雨 🌦️", "天空陰陰的 ☁️"]
            else: a = ["天氣晴朗 ✨", "陽光普照 ☀️", "適合出門 🏃"]

            # b: 穿搭建議
            if t <= 16: b = ["穿厚外套 🧥", "注意保暖 🧤", "冷氣團來襲 ❄️"]
            elif t <= 22: b = ["加件薄長袖 🌸", "涼爽舒適 👕", "微涼好天氣 🧣"]
            else: b = ["短袖出動 👕", "注意防曬 🕶️", "多喝水防暑 🥤"]

            # c: 瑞穗小提醒
            c = ["小心小黑蚊 🦟", "加油喔！💪", "瑞穗日常 🍊", "保持好心情 ✨", "一切順利 ✨"]

            return f"💡 {random.choice(a)} | {random.choice(b)} | {random.choice(c)}"
        
        # 5. 組裝訊息內容 (3小時一格版)
        msg_parts = [f"🍊 【瑞穗鄉】天氣預報", "===================="]
        
        # 只取前 3 個時段 (每格 3 小時)
        for i in range(3):
            t_data = elements['溫度'][i] # 這裡標籤名稱可能略有不同，請檢查 API 回傳
            st = t_data['StartTime']
            display_time = f"{st[5:10]} {st[11:16]}"
            
            # 抓取對應數據
            temp = t_data['ElementValue'][0]['Temperature']
            wx = elements['天氣現象'][i]['ElementValue'][0]['Weather']
            pop = elements['降雨機率'][i]['ElementValue'][0]['ProbabilityOfPrecipitation']
            
            msg_parts.append(f"🕒 {display_time}")
            msg_parts.append(f"☁️ {wx} | 🌡️ {temp}°C | ☔ {pop}%")
            msg_parts.append(get_tips(temp, pop, wx))
            if i < 2: msg_parts.append("-" * 15)

        final_msg = "\n".join(msg_parts)

        # 6. LINE 推播 (從 broadcast 改成 push)
        # 網址要改成 push 結尾
        line_url = 'https://api.line.me/v2/bot/message/push'
        
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {line_key}'
        }
        
        # payload 要加入 "to": group_id，指定發給群組
        payload = {
            "to": group_id, 
            "messages": [{"type": "text", "text": final_msg}]
        }
        
        response = requests.post(line_url, headers=headers, json=payload)
        print(f"✅ 群組發送狀態: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ 錯誤原因: {response.text}")

    except Exception as e:
        print(f"💥 運行出錯: {e}")

if __name__ == "__main__":
    get_weather()