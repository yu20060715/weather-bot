import os
import requests

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 花蓮縣鄉鎮預報 API (瑞穗鄉)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}&locationName=瑞穗鄉"
    
    try:
        res = requests.get(url).json()
        # 修正路徑解析
        location_data = res['records']['locations'][0]['location'][0]
        elements = location_data['weatherElement']
        
        desc, pop, temp = "無資料", "0", "未知"
        for elm in elements:
            if elm['elementName'] == 'Wx': desc = elm['time'][0]['elementValue'][0]['value']
            elif elm['elementName'] == 'PoP12h': pop = elm['time'][0]['elementValue'][0]['value']
            elif elm['elementName'] == 'T': temp = elm['time'][0]['elementValue'][0]['value']

        msg = (
            f"🍊 瑞穗鄉專屬天氣報\n"
            f"-------------------\n"
            f"☁️ 天氣：{desc}\n"
            f"☔ 降雨機率：{pop}%\n"
            f"🌡️ 氣溫：{temp}°C\n"
            f"-------------------\n"
            f"{'⚠️ 記得帶傘喔！' if int(pop) >= 30 else '☀️ 天氣不錯～'}"
        )
        
        # 改用 broadcast，這樣你就不必煩惱 ID 的問題
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"廣播發送狀態: {r.status_code}")
        if r.status_code != 200:
            print(f"錯誤原因: {r.text}")

    except Exception as e:
        print(f"解析失敗: {e}")

if __name__ == "__main__":
    get_weather()