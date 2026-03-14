import os, requests, random

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')
    
    # 改用這個網址，直接鎖定瑞穗鄉所在的 043 (花蓮)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-043?Authorization={cwa_key}&locationName=瑞穗鄉"

    try:
        res = requests.get(url).json()
        
        # --- DEBUG 專區：在 Log 裡看清楚到底抓到什麼 ---
        recs = res.get('records', {})
        locs = recs.get('Locations', [{}])[0].get('Location', [{}])
        
        if not locs:
            print("❌ 診斷：API 回傳了空的地點列表。可能是 Token 權限不足或代碼 043 不對。")
            return
            
        target = locs[0]
        elements = target.get('WeatherElement', [])
        print(f"✅ 診斷：成功抓到瑞穗鄉！裡面有 {len(elements)} 個天氣元素。")
        # -------------------------------------------

        # 建立一個「不論大小寫、不論全名簡寫」都能抓的字典
        data_map = {}
        for e in elements:
            name = e['ElementName']
            data_map[name] = e['Time']

        # 嘗試抓取各種可能的標籤名
        wx_list = data_map.get('Wx') or data_map.get('Weather') or []
        t_list = data_map.get('T') or data_map.get('Temperature') or []
        pop_list = data_map.get('PoP12h') or data_map.get('ProbabilityOfPrecipitation') or []

        msg = "🍊 【瑞穗鄉】天氣預報\n"
        # 抓取前兩個時段就好，避免長度不一報錯
        for i in range(2):
            # 取值的邏輯：直接拿 ElementValue 裡面的第一個內容
            get_v = lambda x, idx: list(x[idx]['ElementValue'][0].values())[0] if len(x) > idx else "無資料"
            
            wx = get_v(wx_list, i)
            t = get_v(t_list, i)
            pop = get_v(pop_list, i)
            msg += f"--------------------\n🕒 時段 {i+1}\n☁️ {wx}\n🌡️ {t}°C | ☔ {pop}%\n"

        # 趣味提醒
        tips = ["記得喝水喔！🥤", "瑞穗的朋友加油！💪", "又是美好的一天！✨"]
        msg += f"--------------------\n💡 {random.choice(tips)}"

        # 發送
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"🚀 LINE 發送狀態: {r.status_code}")

    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    get_weather()