import jwt

SECRET_KEY = "testkey"
payload = {"sub": 1}

# Encode token
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
print("Token:", token)

# Decode token
decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
print("Decoded:", decoded)

# token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjF9.uWIyH1I28pCNb79Py9jaMmXMVZ_PatNXt4c4WXiYP4I
# Decoded: {'sub': 1}