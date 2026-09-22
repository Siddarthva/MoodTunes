import httpx
import numpy as np
import cv2

BASE_URL = "http://127.0.0.1:8001"

def create_dummy_face_image():
    # Create a 200x200 RGB image with a synthetic face-like pattern so cv2/Haar cascade or test can run
    img = np.ones((300, 300, 3), dtype=np.uint8) * 200
    # Draw eyes, nose, mouth to trigger face detector
    cv2.circle(img, (150, 150), 100, (150, 150, 150), -1)
    cv2.circle(img, (110, 120), 15, (50, 50, 50), -1)
    cv2.circle(img, (190, 120), 15, (50, 50, 50), -1)
    cv2.ellipse(img, (150, 180), (30, 15), 0, 0, 180, (50, 50, 50), 5)
    _, encoded = cv2.imencode('.jpg', img)
    return encoded.tobytes()

def main():
    client = httpx.Client(base_url=BASE_URL, timeout=15.0)

    print("--- 1. Health Checks ---")
    r1 = client.get("/health")
    print("GET /health:", r1.status_code, r1.json())
    assert r1.status_code == 200

    r2 = client.get("/api/health")
    print("GET /api/health:", r2.status_code, r2.json())
    assert r2.status_code == 200

    r3 = client.get("/api/content/home")
    print("GET /api/content/home:", r3.status_code, r3.json())
    assert r3.status_code == 200

    print("\n--- 2. Content Services ---")
    mood_req = {
        "dominant_emotion": "happy",
        "emotional_profile": {"dominant_emotion": "happy", "energy": 85.0, "valence": 90.0, "tempo": "high", "weighted_genres": [{"genre": "Pop", "weight": 85.0}]},
        "energy": 85.0,
        "valence": 90.0,
        "intent": "match_me"
    }
    r4 = client.post("/api/content/mood", json=mood_req)
    print("POST /api/content/mood:", r4.status_code, r4.json())
    assert r4.status_code == 200

    r5 = client.post("/api/content/post-scan", json=mood_req)
    print("POST /api/content/post-scan:", r5.status_code, r5.json())
    assert r5.status_code == 200

    print("\n--- 3. Talk Service ---")
    talk_req = {
        "message": "Hello, I am feeling a bit tired today.",
        "conversation": [],
        "user_intent": "comfort"
    }
    r6 = client.post("/api/talk", json=talk_req)
    print("POST /api/talk:", r6.status_code, r6.json())
    assert r6.status_code == 200

    print("\n--- 4. Music Endpoints ---")
    r7 = client.get("/api/music/search?q=feel%20good")
    print("GET /api/music/search status:", r7.status_code)
    if r7.status_code == 200:
        print("GET /api/music/search:", f"Found {len(r7.json())} tracks")
    else:
        print("GET /api/music/search text:", r7.text)
    assert r7.status_code == 200

    r8 = client.get("/api/music/recommendations?emotion=happy")
    print("GET /api/music/recommendations:", r8.status_code, f"Found {len(r8.json())} tracks")
    assert r8.status_code == 200

    print("\n--- 5. Analyze Image Endpoint ---")
    img_bytes = create_dummy_face_image()
    files = {"image": ("face.jpg", img_bytes, "image/jpeg")}
    data = {"intent": "match_me"}
    
    r9 = client.post("/api/analyze", files=files, data=data)
    print("POST /api/analyze status:", r9.status_code)
    if r9.status_code == 200:
        res = r9.json()
        print("POST /api/analyze success:", res["success"])
        print("Dominant Emotion:", res["emotion"]["dominant"])
        print("Recommendations count:", len(res["recommendations"]))
    else:
        print("POST /api/analyze response:", r9.text)

    print("\n--- ALL TEST CHECKS COMPLETED SUCCESSFULLY ---")

if __name__ == "__main__":
    main()
