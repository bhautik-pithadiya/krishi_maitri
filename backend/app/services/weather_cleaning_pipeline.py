import datetime
import os

def clean_weather_data(data):
    cleaned_data = []
    for entry in data:
        dt = entry.get('dt_txt', '')
        temp = entry['main'].get('temp')
        feels_like = entry['main'].get('feels_like')
        humidity = entry['main'].get('humidity')
        pressure = entry['main'].get('pressure')
        rain = entry.get('rain', {}).get('3h', 0.0)  # mm in last 3h
        wind_speed = entry.get('wind', {}).get('speed')
        condition = entry['weather'][0].get('description', 'N/A')

        cleaned_data.append({
            "datetime": dt,
            "temperature_C": round(temp, 1),
            "feels_like_C": round(feels_like, 1),
            "humidity_%": humidity,
            "pressure_hPa": pressure,
            "rain_mm": round(rain, 2),
            "wind_speed_mps": round(wind_speed, 2),
            "condition": condition
        })
    return cleaned_data


def summarize_for_llm(cleaned_data):
    summary = []
    for entry in cleaned_data:
        dt_obj = datetime.datetime.strptime(entry['datetime'], '%Y-%m-%d %H:%M:%S')
        time_str = dt_obj.strftime("%d %b %Y %I:%M %p")

        rain_info = f"{entry['rain_mm']}mm rain" if entry['rain_mm'] > 0 else "no rain"
        summary.append(
            f"At {time_str}: {entry['condition'].capitalize()}, Temp {entry['temperature_C']}°C "
            f"(Feels {entry['feels_like_C']}°C), Humidity {entry['humidity_%']}%, "
            f"Wind {entry['wind_speed_mps']} m/s, {rain_info}."
        )
    return "\n".join(summary)