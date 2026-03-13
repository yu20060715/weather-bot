import os
import requests
import random

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 使用花蓮縣鄉鎮預報 API (不帶過濾參數，進程式再篩選最穩)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}"
    
    try:
        res = requests.get(url).json()
        
        # 1. 精準鎖定瑞穗鄉資料 (解決 locations/location 報錯)
        locs_container = res.get('records', {}).get('locations', [{}])[0]
        all_locations = locs_container.get('location', [])
        target = next((loc for loc in all_locations if loc['locationName'] == '瑞穗鄉'), None)

        if not target:
            print("❌ 找不到瑞穗鄉，請檢查 API 資料內容")
            return

        # 2. 提取天氣元素
        elements = {e['elementName']: e['time'] for e in target['weatherElement']}
        
        # 3. 準備早、中、晚三個時段 (取未來前三個區間)
        msg_parts = [f"🍊 【花蓮瑞穗】今日天氣特報", "--------------------"]
        
        # 用於判斷提醒語的變數
        max_pop = 0
        all_temps = []

        # 氣象署鄉鎮預報通常 3 小時或 6 小時一跳，我們取前 3 個代表早中晚
        for i in range(3):
            time_label = ["【時段一】", "【時段二】", "【時段三】"][i]
            wx = elements['Wx'][i]['elementValue'][0]['value']
            temp = elements['T'][i]['elementValue'][0]['value']
            pop = elements['PoP12h'][i//2]['elementValue'][0]['value'] # 降雨通常是 12h 一跳
            
            all_temps.append(int(temp))
            max_pop = max(max_pop, int(pop))
            
            msg_parts.append(f"{time_label}\n☁️ 天氣：{wx}\n🌡️ 氣溫：{temp}°C | ☔ 降雨：{pop}%")
        
        msg_parts.append("--------------------")

        # 4. 隨機趣味提醒 (隨機選擇詞語)
        tips = []
        # 下雨判斷
        if max_pop >= 30:
            tips.append(random.choice(["別怪我沒提醒，雨傘帶著保平安！☔", "今天跟雨水有緣，傘一定要帶喔！🌧️", "下雨機率高，不想變落湯雞就帶傘吧！🦆"]))
        else:
            tips.append(random.choice(["天氣穩定，可以不用帶傘，但要帶好心情！☀️", "沒什麼雨，盡情享受瑞穗的陽光吧！😎", "乾乾爽爽的一天，出門去走走吧！✨"]))
        
        # 溫度判斷
        avg_t = sum(all_temps) / len(all_temps)
        if avg_t < 18:
            tips.append(random.choice(["瑞穗有點冷，厚衣服穿起來，別感冒了！🧥", "冷颼颼的，穿厚點才不會抖喔！🧤", "建議穿暖一點，來杯熱咖啡也不錯！☕"]))
        elif avg_t > 28:
            tips.append(random.choice(["今天熱力四射，記得多喝水防中暑！🥤", "氣溫偏高，防曬遮陽一定要做好！🕶️", "有點悶熱，盡量待在通風的地方喔！⛱️"]))
        else:
            tips.append(random.choice(["溫度剛好，多喝水維持體力！🚰", "這種天氣穿件薄長袖最舒服了！🍃", "舒適宜人，記得適時補充水分喔！🥛"]))

        msg_parts.append("💡 暖心小語：\n" + "\n".join(tips))
        final_msg = "\n".join(msg_parts)

        # 5. 發送廣播 (Broadcast)
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": final_msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"✅ 發送成功！狀態碼: {r.status_code}")

    except Exception as e:
        print(f"💥 發生錯誤：{e}")

if __name__ == "__main__":
    get_weather()