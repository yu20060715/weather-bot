import os
import requests
import random

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 改用你發現的穩定網址：抓取花蓮全縣 (043)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-043?Authorization={cwa_key}"

    try:
        res = requests.get(url).json()
        
        # 1. 找到「瑞穗鄉」在那一包資料裡
        locations = res.get('records', {}).get('Locations', [{}])[0].get('Location', [])
        target_data = next((loc for loc in locations if loc.get('LocationName') == '瑞穗鄉'), None)

        if not target_data:
            print("❌ 在花蓮縣資料中找不到瑞穗鄉，請檢查 API 回傳內容")
            return

        # 2. 建立資料對照表
        # 我們把 WeatherElement 轉成一個字典，方便後面直接用名字叫它
        elements = {e['ElementName']: e['Time'] for e in target_data['WeatherElement']}

        # 3. 定義取值函數 (對應氣象署奇葩的標籤結構)
        def get_val(element_name, i):
            try:
                # 氣象署邏輯：ElementValue 裡面的 Key 就叫 ElementName
                return str(elements[element_name][i]['ElementValue'][0][element_name])
            except:
                return "無資料"

        msg_parts = ["🍊 【瑞穗鄉】早中晚天氣預報", "===================="]
        temps = []
        max_pop = 0

        # 4. 抓取接下來的三個預報時段 (每 12 小時一跳)
        # i=0 (今日白天/晚上), i=1 (下一個 12 小時), i=2 (再下一個)
        for i in range(3):
            # 抓取時間並格式化
            start_time = elements['Temperature'][i]['StartTime'][11:16]
            
            wx = get_val('Weather', i)
            t = get_val('Temperature', i)
            pop = get_val('ProbabilityOfPrecipitation', i)

            if t.isdigit(): temps.append(int(t))
            if pop.isdigit(): max_pop = max(max_pop, int(pop))

            msg_parts.append(f"🕒 時段 {start_time}")
            msg_parts.append(f"☁️ 天氣：{wx}")
            msg_parts.append(f"🌡️ 溫度：{t}°C | ☔ 降雨：{pop}%")
            msg_parts.append("--------------------")

        # 5. 趣味隨機提醒
        msg_parts.append("💡 暖心小語：")
        
        # 降雨邏輯
        if max_pop >= 30:
            msg_parts.append(random.choice(["☔ 出門記得帶傘，別讓瑞穗的雨淋濕你的心情！", "🌧️ 降雨機率有點高，帶把傘保平安喔！"]))
        else:
            msg_parts.append(random.choice(["☀️ 天氣不錯，適合去瑞穗牧場喝鮮奶！", "✨ 沒什麼雨，盡情享受花蓮的好空氣吧！"]))

        # 溫度邏輯
        if temps and sum(temps)/len(temps) < 18:
            msg_parts.append("🧣 氣溫偏低，提醒您穿厚點，別感冒了！")
        elif temps and sum(temps)/len(temps) > 28:
            msg_parts.append("🥤 天氣悶熱，記得多喝水，別中暑囉！")
        else:
            msg_parts.append("🌸 溫度很舒適，是個適合戶外活動的好日子！")

        # 6. 發送
        final_msg = "\n".join(msg_parts)
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": final_msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"✅ 完成！狀態碼: {r.status_code}")
        print("預覽：\n", final_msg)

    except Exception as e:
        print(f"💥 解析失敗: {e}")

if __name__ == "__main__":
    get_weather()