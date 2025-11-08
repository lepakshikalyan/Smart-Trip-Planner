import requests

def test_weather(city="Ooty"):
    geo = f"https://nominatim.openstreetmap.org/search?city={city}&format=json&limit=1"
    loc = requests.get(geo, headers={"User-Agent":"trip-test"}).json()
    lat, lon = loc[0]["lat"], loc[0]["lon"]
    wurl = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&forecast_days=7&timezone=auto"
    res = requests.get(wurl).json()
    print(f"🌦️ 7-Day Weather in {city}")
    for i, d in enumerate(res["daily"]["time"]):
        print(f"{d}: {res['daily']['temperature_2m_min'][i]}–{res['daily']['temperature_2m_max'][i]}°C, rain {res['daily']['precipitation_sum'][i]} mm")

def test_osm(city="Ooty"):
    q = f"""
    [out:json][timeout:25];
    area["name"="{city}"][admin_level~"6|7|8"]->.a;
    (node["amenity"="restaurant"](area.a););
    out center 5;
    """
    r = requests.get("http://overpass-api.de/api/interpreter", params={"data":q}).json()
    print(f"🍽️ Restaurants in {city}:")
    for e in r.get("elements",[])[:5]:
        print("-", e.get("tags",{}).get("name","Unknown"))

test_weather()
test_osm()
