# Smart-Trip-Planner
A Flask-based web application that helps users plan short trips by generating itineraries, weather forecasts, nearby attractions, restaurants, and hotels using live data from public APIs.

---

## Contents

| File | Description |
|------|--------------|
| `app.py` | Main Flask backend application handling routes, API requests, and trip logic. |
| `templates/index.html` | Frontend HTML file with Tailwind CSS styling for the web interface. |
| `static/` | Optional folder for static files (CSS, JS, images). |
| `README.md` | Project documentation and setup instructions. |

---

## Requirements

- Python ≥ 3.8  
- Flask  
- Requests library  
- Internet connection (for API calls to OpenStreetMap and Open-Meteo)

---

## Installation Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/smart-trip-planner.git
cd smart-trip-planner
```
###2.Create and Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # For macOS/Linux
venv\Scripts\activate         # For Windows
```
###3.Install Dependencies
```bash
pip install flask requests
```
### Start the Flask app
python app.py

Access in Browser
Open the following link in your web browser:
```bash
http://127.0.0.1:5000
```


