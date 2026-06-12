import requests

url = "http://localhost:8000/ask"
headers = {
    "X-API-Key": "dev-key-change-me-in-production",
    "Content-Type": "application/json"
}
data = {
    "question": "Thời tiết ở Đà Nẵng đang thế nào vậy?"
}

print("Đang gửi yêu cầu đến Agent...")
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("\n✅ THÀNH CÔNG! Câu trả lời của Agent:")
    print("--------------------------------------------------")
    print(response.json()["answer"])
    print("--------------------------------------------------")
else:
    print(f"\n❌ LỖI: {response.status_code}")
    print(response.text)
