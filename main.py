import os
import requests

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')
    user_id = os.getenv('LINE_USER_ID')

    # 花蓮縣各鄉鎮預報
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}&locationName=瑞穗鄉"
    
    try:
        response = requests.get(url)
        res_data = response.json()
        
        # 這是最穩的安全抓取路徑
        records = res_data.get('records', {})
        locations_list = records.get('locations', [{}])
        location_list = locations_list[0].get('location', [{}])
        location_data = location_list[0]
        
        elements = location_data.get('weatherElement', [])
        
        # 預設值
        desc = "無資料"
        pop = "0"
        temp = "未知"
        
        for elm in elements:
            # Wx: 天氣現象
            if elm['elementName'] == 'Wx':
                desc = elm['time'][0]['elementValue'][0]['value']
            # PoP12h: 12小時降雨機率
            elif elm['elementName'] == 'PoP12h':
                pop = elm['time'][0]['elementValue'][0]['value']
            # T: 平均溫度
            elif elm['elementName'] == 'T':
                temp = elm['time'][0]['elementValue'][0]['value']

        msg = (
            f"🍊 花蓮【瑞穗鄉】詳細預報\n"
            f"-------------------\n"
            f"☁️ 天氣狀況：{desc}\n"
            f"☔ 降雨機率：{pop}%\n"
            f"🌡️ 平均氣溫：{temp}°C\n"
            f"-------------------\n"
            f"祝瑞穗的朋友今天愉快！"
        )
        
        # 使用 push 模式 (最穩定)
        line_url = 'https://api.line.me/v2/bot/message/push'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"to": user_id, "messages": [{"type": "text", "text": msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"發送狀態碼: {r.status_code}")
        if r.status_code != 200:
            print(f"LINE 錯誤訊息: {r.text}")

    except Exception as e:
        print(f"解析失敗，原因：{str(e)}")

if __name__ == "__main__":
    get_weather()