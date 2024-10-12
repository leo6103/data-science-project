# import requests
# from bs4 import BeautifulSoup
# import csv

# # Define the URL of the e-commerce site
# url = 'https://www.thegioididong.com/laptop#c=44&o=17&pi=14'

# response = requests.get(url)

# print(response.te)

from numpy import byte
import requests
from bs4 import BeautifulSoup

# Define the headers
headers = {
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    # "Accept-Encoding": "gzip, deflate, br, zstd",
    # "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    # "Cache-Control": "no-cache",
    # "Connection": "keep-alive",
    # "Cookie": "_gcl_au=1.1.1404682849.1717900743; _ga=GA1.1.904783243.1717900743; _pk_id.7.8f7e=c80dd47415656145.1717900743.; _fbp=fb.1.1717900743392.30340702928242410; _tt_enable_cookie=1; _ttp=X1t7E4Eid9XinCxarHXJUDknjG6; __zi=3000.SSZzejyD3DOkZU2bqmuCtIY7xk_V3mRHPyhpeT4NHOrrmEopamLJcZQVghIMJnUHDvghlzzC6PDocgkxraKTaJKq.1; TBMCookie_3209819802479625248=538270001723806198Nc0Qp1UGL4HsWQGiCUGq2SPFXwc=; ___utmvm=###########; SvID=beline2687|Zr8x+|Zr8x+; ___utmvc=navigator%3Dtrue,navigator.vendor%3DGoogle%20Inc.,navigator.appName%3DNetscape,navigator.plugins.length%3D%3D0%3Dfalse,navigator.platform%3DLinux%20x86_64,navigator.webdriver%3Dfalse,plugin_ext%3Dno%20extention,ActiveXObject%3Dfalse,webkitURL%3Dtrue,_phantom%3Dfalse,callPhantom%3Dfalse,chrome%3Dtrue,yandex%3Dfalse,opera%3Dfalse,opr%3Dfalse,safari%3Dfalse,awesomium%3Dfalse,puffinDevice%3Dfalse,__nightmare%3Dfalse,domAutomation%3Dfalse,domAutomationController%3Dfalse,_Selenium_IDE_Recorder%3Dfalse,document.__webdriver_script_fn%3Dfalse,document.%24cdc_asdjflasutopfhvcZLmcfl_%3Dfalse,process.version%3Dfalse,navigator.cpuClass%3Dfalse,navigator.oscpu%3Dfalse,navigator.connection%3Dtrue,navigator.language%3D%3D'C'%3Dfalse,window.outerWidth%3D%3D0%3Dfalse,window.outerHeight%3D%3D0%3Dfalse,window.WebGLRenderingContext%3Dtrue,document.documentMode%3Dundefined,eval.toString().length%3D33,digest=; _pk_ref.7.8f7e=%5B%22%22%2C%22%22%2C1723806200%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.7.8f7e=1; _ga_TLRZMSX5ME=GS1.1.1723806200.6.0.1723806200.60.0.0; _ce.irv=returning; cebs=1; _ce.clock_event=1; _ce.clock_data=51%2C222.252.31.183%2C1%2C120f067c16b32be659e0180b31e62841%2CChrome%2CVN; cebsp_=1; _ce.s=v~a983c89e3e9eed04fd246cf4be100a90d44b98f2~lcw~1723806205988~lva~1723806201830~vpv~3~v11.cs~127806~v11.s~26ef1aa0-5bbf-11ef-b02f-61b5b4039b04~v11.sla~1723806205988~v11.send~1723806206404~lcw~1723806206404",
    # "Host": "www.thegioididong.com",
    # "Pragma": "no-cache",
    # "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
    # "Sec-Ch-Ua-Mobile": "?0",
    # "Sec-Ch-Ua-Platform": "\"Linux\"",
    # "Sec-Fetch-Dest": "document",
    # "Sec-Fetch-Mode": "navigate",
    # "Sec-Fetch-Site": "none",
    # "Sec-Fetch-User": "?1",
    # "Upgrade-Insecure-Requests": "1",
    "User-Agent": '''sdaf'''
}

# Send a GET request with the headers
response = requests.get('https://www.thegioididong.com/laptop#c=44&o=17&pi=14', headers=headers)

soup = BeautifulSoup(response.content, 'html.parser')

elements_with_data_id = soup.find_all(attrs={'data-productcod': True})

print(soup.prettify())