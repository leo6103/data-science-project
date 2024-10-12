import requests
import json
import logging
import re
from bs4 import BeautifulSoup

headers = {
    "Pragma": "no-cache",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Linux",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    # "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7",
    "Cache-Control": "no-cache",
    "Cookie": "__uidac=0166e10b24e9c33f51e204c31d3dedbd; __admUTMtime=1726024484; _tt_enable_cookie=1; _ttp=BbfBk5Dudk2tnOvY4mvlTGEXanV; dtdz=9618a77f-28bb-5237-8ad5-099401c5f025; __RC=4; __R=1; __uif=__uid%3A5696027391907961199; __iid=6461; __iid=6461; __su=0; __su=0; _fbp=fb.2.1726024496003.446215731339796127; __tb=0; _hjSessionUser_1708983=eyJpZCI6Ijg0YWVkYzZjLWJkMjItNWQ3NS05MDI1LTVmYzc3MmQ0MDk1ZCIsImNyZWF0ZWQiOjE3MjYwMjQ0ODUxMDEsImV4aXN0aW5nIjp0cnVlfQ==; _gcl_au=1.1.542136691.1726024619; __zi=3000.SSZzejyD6jy_Zl2jp1eKttQU_gxC3nMGTChWuC8NLincmF_oW0L0s26VkVQ1JmJJ89gu_SXC2j5bchZvmKKEqpKq.1; _gcl_gs=2.1.k1$i1726027772; _gac_UA-3729099-1=1.1726027818.CjwKCAjw3P-2BhAEEiwA3yPhwPIfJVIAh_oTTuU5JVjacZqy1ep6HKNLiZRdtRGsdcjpcF_k-aXA3hoCAJ8QAvD_BwE; _gcl_aw=GCL.1726027912.CjwKCAjw3P-2BhAEEiwA3yPhwPIfJVIAh_oTTuU5JVjacZqy1ep6HKNLiZRdtRGsdcjpcF_k-aXA3hoCAJ8QAvD_BwE; PH_ONBOARDING_SESSION=0; _ga=GA1.1.900106895.1726024484; _hjHasCachedUserAttributes=true; onboarding-session-later=2; ajs_anonymous_id=ab0d096b-55d9-4010-9978-69bc341da4cb; .AspNetCore.Antiforgery.VyLW6ORzMgk=CfDJ8MvdDdAAd_FEpUC6C5fc5Cw5NfLQd0OCgPEQRteiI0_uY0pJqnMW5Xby-NAQy1FLXt17_A5fIRSS9yA9EECIgb-LtfBGt-A_x3O73igDFNvv3aNl0msrzj5tfZQN2k4DQuWlMEs73MfBJW5pH32P4rs; __cflb=02DiuD2Xpp2HE9t1eLGErdKsSqKrWmYfh6Gd4gSotei8t; __IP=1952655394; __UF=1%252C6; USER_PRODUCT_SEARCH=38%7C324%7CHN%7C7%7C9448%7C646%7C0%2C40880220; _cfuvid=JZv.biWVOCVwS.EQqj4LJQ79L50gACl_SOpt2Nrmi0A-1726501836662-0.0.1.1-604800000; con.ses.id=1734bfb7-45e4-426a-9d85-39d9659b2a47; con.unl.lat=1726506000; con.unl.sc=4; __gads=ID=6c36510227266d80:T=1726024484:RT=1726533791:S=ALNI_MYpMCLXJkAk4BFZ_Te_dyV4Xg7SWw; __gpi=UID=00000ef886aa4b55:T=1726024484:RT=1726533791:S=ALNI_MbgaJ8sQTI5YdGqDlJVE3OxyGd8Sw; __eoi=ID=0c3e74a94769ca07:T=1726024484:RT=1726533791:S=AA-Afjaeigrg2xUU2_8pOVHQ3zLK; _clck=epcddk%7C2%7Cfp9%7C0%7C1715; cf_clearance=aKm9qRiEmbXBUcfeIn5Qb9voIWGEw_C97Ts6cgUr8dE-1726533793-1.2.1.1-OhNTR1dM7YimAy.cpzu4CqTjypn0EaY6NJH9Xf.JL7DcXfidWkqZvDJ3XyQnFKrVJLjLO1KmTLvAKOMi0w_lNAEMJ3I5zCjjgYWRjiA3zouWaN65mMYoTC_IuKAfft7ArsorjmuHW5jUuphYZa8WzGiymXqEBZ.ZyHg5Lb3YQRaplaxUVm_4mVZegn5315_QNx.mSi6i5OWfjRKpZbrqa4oQvCFxYvuoX9WfWkJv7rs2pxlqycbyJ_AAIMek1d2ZJ78AwNCVuBgO.ZNauZ3pLVoYdsh9myWxCUMmQgaRq4AQudwMKtBcXO3j7uil3L.mdyaU9p7md2hU542KaNM85N6dp8n1aXBZoDdIFLAthDUumr0uFwFzT7EzHGiwdvKJ; _hjSession_1708983=eyJpZCI6IjYxNzc5MTNjLTE0YzYtNDgyMi1iODJmLWZhY2Y1NGJlYWI0ZiIsImMiOjE3MjY1MzM3OTQ5MzAsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=; __adm_upl=eyJ0aW1lIjoxNzI2NTM1NTk0LCJfdXBsIjoiMC01Njk2MDI3MzkxOTA3OTYxMTk5In0=; ab.storage.deviceId.892f88ed-1831-42b9-becb-90a189ce90ad=%7B%22g%22%3A%2258be5d5f-ff16-fc7a-e984-949cca84dbb8%22%2C%22c%22%3A1726024488271%2C%22l%22%3A1726533795280%7D; _ga_HTS298453C=GS1.1.1726533791.11.1.1726533802.49.0.0; con.unl.usr.id=%7B%22key%22%3A%22userId%22%2C%22value%22%3A%22ab0d096b-55d9-4010-9978-69bc341da4cb%22%2C%22expireDate%22%3A%222025-09-17T07%3A43%3A22.0710082Z%22%7D; con.unl.cli.id=%7B%22key%22%3A%22clientId%22%2C%22value%22%3A%223b82a014-dddd-4310-95a1-e15d8650a154%22%2C%22expireDate%22%3A%222025-09-17T07%3A43%3A22.0710813Z%22%7D; _clsk=1bj8ko%7C1726533803451%7C2%7C0%7Cj.clarity.ms%2Fcollect; ab.storage.sessionId.892f88ed-1831-42b9-becb-90a189ce90ad=%7B%22g%22%3A%2210a951d7-2859-1e3e-ac36-1be72744ed46%22%2C%22e%22%3A1726535603867%2C%22c%22%3A1726533795279%2C%22l%22%3A1726533803867%7D"
}


page_limit = 10
base_url = 'https://batdongsan.com.vn/ban-can-ho-chung-cu-ha-noi'
estate_list = []

for i in range(1, page_limit + 1):
    url = f'https://batdongsan.com.vn/ban-can-ho-chung-cu-ha-noi/p{i}'
    print(f'Fetching page {i} from URL: {url}')

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad responses
        if response.status_code == 429:
            print("Too many requests!")
            formatted_headers = json.dumps(dict(response.headers), indent=4)
            print(f"Response headers:\n{formatted_headers}")
            break


        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.find_all(class_='js__product-link-for-product-id')

        for element in elements:
            title = estate_url = None

            try:
                title = element.find(class_="re__card-title").get_text(separator=' ', strip=True)
            except Exception as e:
                print(f'Error fetching title: {e}')

            try:
                raw_location = element.find(class_="re__card-location").get_text(separator=' ', strip=True)
    
                # Làm sạch khoảng trắng dư thừa và ký tự đặc biệt
                cleaned_location = re.sub(r'[^\w\s,]', '', raw_location).strip()

                # Chỉ lấy phần trước dấu phẩy
                location = cleaned_location.split(',')[0].strip()
            except Exception as e:
                print(f'Error fetching location: {e}')

            try:
                estate_url = base_url + element['href']
            except Exception as e:
                print(f'Error fetching url: {e}')

            if estate_url:
                print(f'Fetching details from: {estate_url}')
                try:
                    detail_response = requests.get(estate_url, headers=headers)
                    detail_response.raise_for_status()
                    soup_detail = BeautifulSoup(detail_response.content, 'html.parser')
                    features = {}

                    info_items = soup_detail.find_all(class_='re__pr-specs-content-item')
                    for item in info_items:
                        try:
                            feature_title = item.find(class_='re__pr-specs-content-item-title').get_text(strip=True)
                            feature_value = item.find(class_='re__pr-specs-content-item-value').get_text(strip=True)
                            features[feature_title] = feature_value
                        except Exception as e:
                            logging.error(f"Lỗi khi trích xuất thông tin chi tiết: {e}")

                    estate_info = {
                        'Tên': title,
                        'Url': estate_url,
                        'Vị trí': location
                    }
                    estate_info.update(features)
                    estate_list.append(estate_info)

                except requests.RequestException as e:
                    print(f'Error fetching details from {estate_url}: {e}')

    except requests.RequestException as e:
        print(f'Error fetching page {i}: {e}')

# Lưu dữ liệu vào file general_data.json
if estate_list:
    with open('general_data.json', 'w', encoding='utf-8') as f:
        json.dump(estate_list, f, indent=4, ensure_ascii=False)

    print(f'Data has been successfully saved to general_data.json')
    print('Total:', len(estate_list))
