import requests

def get_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        location = data.get("loc", "Unknown").split(",")
        city = data.get("city", "N/A")
        region = data.get("region", "N/A")
        country = data.get("country", "N/A")
        return {
            "latitude": location[0],
            "longitude": location[1],
            "city": city,
            "region": region,
            "country": country,
            "ip": data.get("ip", "N/A")
        }
    except Exception as e:
        return {"error": str(e)}

info = get_location()
print(info)

