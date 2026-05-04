from app import app


def expect_ok(label, response):
    status = response.status_code
    print(f"{label}: {status}")
    if status >= 400:
        print(response.get_data(as_text=True))
        raise SystemExit(1)
    return response.get_json()


client = app.test_client()

print("--- APP VERIFICATION ---")
expect_ok("GET /", client.get("/"))
expect_ok("GET /dashboard", client.get("/dashboard"))

login = expect_ok(
    "POST /api/login",
    client.post("/api/login", json={"username": "parent1", "password": "pass123"}),
)
print(f"Logged in parent: {login['user']['name']}")

dashboard = expect_ok("GET /api/dashboard", client.get("/api/dashboard?user=parent1&lang=en"))
print(f"Student: {dashboard['student']['name']}")
print(f"First notification: {dashboard['notifications'][0]['message']}")

prediction = expect_ok(
    "POST /api/predict",
    client.post("/api/predict", json={"past_marks": [70, 75, 80, 85]}),
)
print(f"Predicted mark: {prediction['predicted_mark']} ({prediction['trend']})")

chat = expect_ok(
    "POST /api/chat",
    client.post("/api/chat", json={"message": "How are the marks?", "user": "parent1", "lang": "en"}),
)
print(f"Chat response: {chat['response']}")

bad_login = client.post("/api/login", json={"username": "parent1", "password": "wrong"})
print(f"Bad login rejected: {bad_login.status_code == 401}")
if bad_login.status_code != 401:
    raise SystemExit(1)

bad_json = client.post("/api/chat", data="not json", content_type="text/plain")
print(f"Bad chat request rejected: {bad_json.status_code == 400}")
if bad_json.status_code != 400:
    raise SystemExit(1)

print("Verification complete.")
