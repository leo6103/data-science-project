import requests

proxy = {
    "https": "https://pia100311:Pr1244@123.21.157.28:30000"
}

url = "http://ident.me/"

response = requests.get(url, proxies=proxy)
ip_address = response.text

print("Your new IP address is:", ip_address)
