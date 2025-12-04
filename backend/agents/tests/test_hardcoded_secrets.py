API_KEY = "sk_live_abc1234567890SECRET"

def send_payment(data):
    return requests.post(
        "https://payments.example.com",
        json=data,
        headers={"Authorization": API_KEY}
    )
