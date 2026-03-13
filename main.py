import os
import requests
import random

def get_weather():
    # 讀取環境變數
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # API 網址 (花蓮縣鄉鎮預報)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}"
    
    try:
        res = requests.get(url).json()
        
        # --- 原理展示：如何從洋蔥裡挖出瑞穗鄉 ---
        # 我們用遞迴或遍歷的方式找尋「瑞穗鄉」
        target_data = None
        
        # 氣象署結構通常是 records -> locations[0] -> location (一個清單)
        locations_container = res.get('records', {}).get('locations', [{}])[0]
        location_list = locations_container.get('location', [])

        for loc in location_list:
            if loc.get('locationName') == '瑞穗鄉':
                target_data = loc
                break
        
        if not target_data:
            print("❌ 慘了！在花蓮縣的資料裡竟然翻不到『瑞穗鄉』。")
            print(f"目前抓到的地名有：{[l.get('locationName') for l in location_list[:5]]}...")
            return

        # --- 抓取早中晚時段 (Wx=天氣, T=氣溫, PoP12h=降雨) ---
        elements = {e['elementName']: e['time'] for e in target_data['weatherElement']}
        
        msg_parts = ["🍊 【瑞穗鄉】今日早中晚天氣預報", "===================="]
        
        # 抓取 3 個時段 (0, 1, 2 分別代表接下來的三個預報點)
        for i in range(3):
            t_info = elements['T'][i]
            wx_info = elements['Wx'][i]
            # 降雨機率通常 12 小時一跳，所以 i=0, 1 用同一個，i=2 用下一個
            pop_info = elements['PoP12h'][0 if i < 2 else 1]
            
            time_str = t_info['startTime'][11:16] # 只取小時分鐘
            temp = t_info['elementValue'][0]['value']
            wx = wx_info['elementValue'][0]['value']
            pop = pop_info['elementValue'][0]['value']
            
            msg_parts.append(f"🕒 時段 {time_str}\n🌡️ {temp}°C | ☁️ {wx} | ☔ {pop}%")

        # --- 隨機趣味提醒 ---
        msg_parts.append("====================")
        
        # 根據天氣狀況選詞
        current_pop = int(elements['PoP12h'][0]['elementValue'][0]['value'])
        current_temp = int(elements['T'][0]['elementValue'][0]['value'])
        
        reminders = []
        if current_pop >= 30:
            reminders.append(random.choice(["外面好像會濕濕的，記得帶傘喔！☔", "降雨機率高，傘是你的本體，別忘了！🌧️"]))
        else:
            reminders.append(random.choice(["天氣乾爽，適合去瑞穗牧場看牛！🐮", "陽光普照，心情也要美美的！☀️"]))

        if current_temp < 18:
            reminders.append(random.choice(["瑞穗風大會冷，穿厚一點，別感冒了！🧣", "穿厚點穿厚點！資工系關心您的體溫！🧥"]))
        elif current_temp > 28:
            reminders.append(random.choice(["熱到快融化了，多喝水，別中暑！🥤", "這天氣適合吃冰，記得補充水分！🍦"]))
        
        msg_parts.append("💡 暖心小語：")
        msg_parts.append("\n".join(reminders))

        # --- 發送廣播 ---
        final_msg = "\n".join(msg_parts)
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": final_msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"✅ 完成！發送結果: {r.status_code}")

    except Exception as e:
        print(f"❌ 程式爆炸了，原因: {e}")

if __name__ == "__main__":
    get_weather()