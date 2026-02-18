import requests

def get_lat_long_from_pincode(pincode):
    try:
        url = f"https://nominatim.openstreetmap.org/search?postalcode={pincode}&country=India&format=json"
        headers = {"User-Agent": "kaagazseva-app"}

        res = requests.get(url, headers=headers)
        data = res.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass

    return None, None
