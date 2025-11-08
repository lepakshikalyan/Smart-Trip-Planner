from flask import Flask, render_template, request
import requests, math, datetime

app = Flask(__name__)

# ---------- WEATHER (Open-Meteo) ----------
def get_daily_weather(city, days):
    """Get forecast for today + 'days' more using Open-Meteo."""
    try:
        geo = f"https://nominatim.openstreetmap.org/search?city={city}&format=json&limit=1"
        loc = requests.get(geo, headers={"User-Agent":"trip-app"}).json()
        if not loc:
            return []
        lat, lon = loc[0]["lat"], loc[0]["lon"]

        # total days = user input + 1 (today + trip length)
        total_days = days + 1

        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={lat}&longitude={lon}"
               f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
               f"&forecast_days={total_days}&timezone=auto")

        data = requests.get(url).json()
        result = []
        today = datetime.date.today()

        for i in range(total_days):
            date = today + datetime.timedelta(days=i)
            tmin = data["daily"]["temperature_2m_min"][i]
            tmax = data["daily"]["temperature_2m_max"][i]
            rain = data["daily"]["precipitation_sum"][i]

            if rain > 2:
                tip = "🌧️ Carry an umbrella!"
            elif tmax > 32:
                tip = "🥵 Stay hydrated and wear a hat."
            elif tmin < 15:
                tip = "🧥 Carry a jacket for cool evenings."
            else:
                tip = "☀️ Great weather for exploring!"

            result.append({
                "date": str(date),
                "tmin": tmin,
                "tmax": tmax,
                "rain": rain,
                "suggestion": tip
            })
        return result
    except Exception as e:
        print("Weather error:", e)
        return []


# ---------- PLACES (OpenStreetMap Overpass) ----------
def get_places_osm(city_name, category, max_results=10):
    """
    Fetch places from OpenStreetMap using Overpass API (nodes + ways).
    category: 'attraction', 'restaurant', 'hotel'
    """
    overpass_url = "http://overpass-api.de/api/interpreter"

    osm_tags = {
        "attraction": [
            "tourism=attraction",
            "tourism=museum",
            "leisure=park",
            "historic=monument"
        ],
        "restaurant": [
            "amenity=restaurant",
            "amenity=cafe",
            "amenity=fast_food",
            "amenity=food_court",
            "amenity=bar"
        ],
        "hotel": [
            "tourism=hotel",
            "tourism=guest_house",
            "amenity=lodging",
            "tourism=hostel",
            "building=hotel"
        ]
    }

    if category not in osm_tags:
        return []

    # Query both node + way + relation (polygons)
    elements_query = ""
    for tag in osm_tags[category]:
        elements_query += f"  node[{tag}](area.searchArea);\n"
        elements_query += f"  way[{tag}](area.searchArea);\n"
        elements_query += f"  relation[{tag}](area.searchArea);\n"

    query = f"""
    [out:json][timeout:40];
    area["name"="{city_name}"][admin_level~"6|7|8"]->.searchArea;
    (
    {elements_query}
    );
    out center;
    """

    try:
        res = requests.get(overpass_url, params={"data": query}, timeout=45)
        data = res.json()
    except Exception as e:
        print("❌ OSM Error:", e)
        return []

    places = []
    for el in data.get("elements", [])[:max_results]:
        tags = el.get("tags", {})
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        name = tags.get("name")
        if lat and lon and name:
            places.append({
                "name": name,
                "lat": lat,
                "lng": lon,
                "address": city_name
            })
    return places


# ---------- ITINERARY BUILDER ----------
def make_schedule(attractions, days):
    if not attractions:
        return []
    per_day = math.ceil(len(attractions) / days)
    return [attractions[i:i + per_day] for i in range(0, len(attractions), per_day)]


# ---------- TRANSPORT LOGIC ----------
def suggest_transport(city):
    city = city.lower()
    if city in ["hyderabad", "chennai", "delhi", "bangalore", "mumbai"]:
        return "🚇 Metro, 🚌 Bus, 🚗 Cab, 🚕 Auto available locally."
    elif city in ["ooty", "manali", "coorg", "shimla"]:
        return "🚗 Local taxis and 🚶 walking recommended in hill areas."
    else:
        return "🚌 City buses or 🚕 autos available in most cities."


# ---------- MAIN ROUTE ----------
@app.route("/", methods=["GET", "POST"])
def index():
    itinerary, restaurants, hotels = [], [], []
    weather = []
    transport = ""
    message = ""
    city = ""
    days = 0

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        days = int(request.form.get("days", 3))

        if not city:
            message = "Please enter a valid city name."
            return render_template("index.html", message=message)

        attractions = get_places_osm(city, "attraction", max_results=12)
        restaurants = get_places_osm(city, "restaurant", max_results=6)
        hotels = get_places_osm(city, "hotel", max_results=6)
        if not attractions:
            message = f"Could not find attractions for {city}."
            return render_template("index.html", message=message)

        itinerary = make_schedule(attractions, days)
        weather = get_daily_weather(city, days)  # ✅ updated to use user input days
        transport = suggest_transport(city)

    return render_template(
        "index.html",
        itinerary=itinerary,
        restaurants=restaurants,
        hotels=hotels,
        weather=weather,
        transport=transport,
        city=city,
        days=days,
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)
