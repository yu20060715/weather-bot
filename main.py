import os
import requests
import random

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 使用瑞穗鄉專屬過濾網址
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-043?Authorization={cwa_key}&locationName=瑞穗鄉"

    try:
        res = requests.get(url).json()
        
        # 層層安全提取
        records = res.get('records', {})
        locations = records.get('Locations', [{}])[0]
        location = locations.get('Location', [{}])[0]
        elements = location.get('WeatherElement', [])

        # 1. 建立一個不看標籤名的資料庫
        # 我們把 15 個元素都存進去，並自動適應標籤名
        data_pool = {}
        for e in elements:
            name = e.get('ElementName')
            times = e.get('Time', [])
            data_pool[name] = times

        # 2. 定義「暴力取值」函數：無視內層標籤，直接拔第一個值
        def force_get_val(element_names, time_idx):
            # 支援多個標籤名搜尋 (例如 Wx 或 Weather)
            for name in element_names:
                if name in data_pool:
                    try:
                        # 核心邏輯：取 ElementValue[0] 裡面的第一個內容物
                        val_dict = data_pool[name][time_idx]['ElementValue'][0]
                        return str(list(val_dict.values())[0])
                    except:
                        continue
            return "N/A"

        msg_lines = ["🍊 【瑞穗鄉】天氣報 (Debug 版)", "===================="]
        
        # 3. 抓取三個時段
        temps = []
        max_pop = 0

        for i in range(3):
            # 氣象局 043 的標籤通常是全名，這裡我們全包了
            wx = force_get_val(['Weather', 'Wx'], i)
            temp = force_get_val(['Temperature', 'T'], i)
            pop = force_get_val(['ProbabilityOfPrecipitation', 'PoP12h'], i)
            
            # 記錄數值做提醒判斷
            if temp.isdigit(): temps.append(int(temp))
            if pop.isdigit(): max_pop = max(max_pop, int(pop))

            msg_lines.append(f"🕒 時段 {i+1}\n☁️ 狀況：{wx}\n🌡️ 氣溫：{temp}°C | ☔ 降雨：{pop}%")
            msg_lines.append("--------------------")

        # 4. 隨機趣味提醒語庫
        msg_lines.append("💡 暖心提醒：")
        if max_pop >= 30:
            msg_lines.append(random.choice(["外面濕濕的，帶傘保平安！☔", "降雨機率高，傘要隨身喔！🌧️"]))
        else:
            msg_lines.append(random.choice(["陽光普照，適合出門走走！☀️", "沒什麼雨，心情也要美美的！✨"]))

        if temps and sum(temps)/len(temps) < 18:
            msg_lines.append(random.choice(["瑞穗冷冷的，穿厚點喔！🧣", "多喝熱水，別感冒了！☕"]))
        else:
            msg_lines.append(random.choice(["氣溫舒適，祝你有個美好的一天！🌸", "記得多喝水補充水分！🥤"]))

        final_msg = "\n".join(msg_lines)

        # 5. 發送 (如果群組還是收不到，代表 broadcast 對群組無效)
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": final_msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"✅ 發送狀態: {r.status_code}")
        print(f"發送內容預覽：\n{final_msg}")

    except Exception as e:
        print(f"💥 程式崩潰原因: {e}")

if __name__ == "__main__":
    get_weather()