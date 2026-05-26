import base64

with open("auth.json", "rb") as f:
    data = f.read()

encoded = base64.b64encode(data).decode("utf-8")

with open("auth.b64", "w", encoding="utf-8") as f:
    f.write(encoded)

print("Fertig. auth.b64 geschrieben.")
