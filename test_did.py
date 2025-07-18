import requests

headers = {
    "Authorization": "Bearer bWFyaXlhLmlueWFrb3ZhQGdtYWlsLmNvbQ:8IFGVdfhq8DM-b9PI9uBx",
    "Content-Type": "application/json"
}

response = requests.get("https://api.d-id.com/talks", headers=headers)
print(response.status_code)
print(response.text)
