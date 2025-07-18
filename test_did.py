import requests

headers = {
    "Authorization": "Bearer bWFyaXlhLmlueWFrb3ZhQGdtYWlsLmNvbQ:4xlTLfJVGCyVF3ryLGblz",
    "Content-Type": "application/json"
}

response = requests.get("https://api.d-id.com/talks", headers=headers)

print("Status code:", response.status_code)
print("Response:", response.text)
