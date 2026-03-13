import os
import requests

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 改用這組更穩定的鄉鎮 API
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}"
    
    try:
        res = requests.get(url).json()
        # 暴力搜索法：直接在所有地點中找「瑞穗鄉」
        all_locations = res['records']['locations'][0]['location']
        target = next(loc for loc in all_locations if loc['locationName'] == '瑞穗鄉')
        
        elements = target['weatherElement']
        desc = next(e for e in elements if e['elementName'] == 'Wx')['time'][0]['elementValue'][0]['value']
        pop = next(e for e in elements if e['elementName'] == 'PoP12h')['time'][0]['elementValue'][0]['value']
        temp = next(e for e in elements if e['elementName'] == 'T')['time'][0]['elementValue'][0]['value']

        msg = f"🍊 瑞穗鄉今日天氣\n---\n☁️ 天氣：{desc}\n☔ 降雨：{pop}%\n🌡️ 氣溫：{temp}°C\n---\n{'出門記得帶傘!' if int(pop) > 30 else '天氣不錯喔!'}"
        
        # 廣播模式：直接發給群組跟所有人
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"發送結果: {r.status_code}")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    get_weather()