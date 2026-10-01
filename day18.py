import requests

def 查汇率(货币):
    url = f"https://api.exchangerate-api.com/v4/latest/{货币}"
    response = requests.get(url)
    data = response.json()
    人民币 = data["rates"]["CNY"]
    return f"1 {货币} = {人民币} 人民币"

print(查汇率("USD"))
print(查汇率("EUR"))
print(查汇率("JPY"))
