import os
import requests

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 改用這個網址，我們手動在程式裡篩選瑞穗
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}"
    
    try:
        res = requests.get(url).json()
        
        # 暴力尋找法：遍歷所有可能的層級，找到瑞穗鄉
        target_location = None
        
        # 氣象署結構雜亂，我們用兩個迴圈硬拆
        for locs in res.get('records', {}).get('locations', []):
            for loc in locs.get('location', []):
                if loc.get('locationName') == '瑞穗鄉':
                    target_location = loc
                    break
        
        if not target_location:
            # 備用方案：如果上面找不到，再找另一種可能的結構
            for loc in res.get('records', {}).get('location', []):
                if loc.get('locationName') == '瑞穗鄉':
                    target_location = loc
                    break

        if target_location:
            elements = target_location['weatherElement']
            # 使用更安全的提取方式
            def get_val(name):
                for e in elements:
                    if e['elementName'] == name:
                        return e['time'][0]['elementValue'][0]['value']
                return "無資料"

            desc = get_val('Wx')
            pop = get_val('PoP12h')
            temp = get_val('T')

            msg = f"🍊 瑞穗鄉今日天氣\n---\n☁️ 天氣：{desc}\n☔ 降雨：{pop}%\n🌡️ 氣溫：{temp}°C\n---\n{'出門記得帶傘!' if pop.isdigit() and int(pop) > 30 else '天氣不錯喔!'}"
            
            line_url = 'https://api.line.me/v2/bot/message/broadcast'
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
            payload = {"messages": [{"type": "text", "text": msg}]}
            
            r = requests.post(line_url, headers=headers, json=payload)
            print(f"發送結果: {r.status_code}")
        else:
            print("在 API 中找不到『瑞穗鄉』，請檢查地點名稱是否正確")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    get_weather()