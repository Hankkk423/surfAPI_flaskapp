import requests
import json
import datetime
import os
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file

# Replace 'YOUR_API_KEY' with the actual API key you received from Windy.
api_key = os.environ.get("WINDY_API_KEY")
# Define files' path and names
folder_path = 'Windy_API/'
original_filename = 'windy_data_original.json'
updated_filename = 'windy_data_updated.json'
# Define the API endpoint and parameters.
endpoint = 'https://api.windy.com/api/point-forecast/v2'
# Define latitude and longitude (sample: 33.6563005931192, -118.00345056657193)
latitude = 24.873355012923216
longitude = 121.84097563158377

params = {
    "lat": latitude,
    "lon": longitude,
    "model": "gfsWave",
    "parameters": ["waves", "swell1", "swell2"],
    "levels": ["surface"],
    "key": api_key
}


# Make the API request.
header = {"Content-Type" :"application/json"}
response = requests.post(endpoint, json=params, headers=header)
print(response)

if response.status_code == 200:
    print(f"Windy API request succeed with status code {response.status_code}")
    
    data = response.json()
    print(json.dumps(data, indent=4))

    # Save the "original" data to a JSON file
    with open(f'{folder_path}{original_filename}', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    
    # Convert the timestamps to human-readable dates
    timestamps = data.get("ts", [])
    readable_timestamps = []

    # Convert each timestamp to a human-readable date and time
    for timestamp in timestamps:
        dt = datetime.datetime.utcfromtimestamp(timestamp / 1000)  # Divide by 1000 to convert from milliseconds to seconds
        print("Readable Timestamp:", dt)
        readable_timestamps.append(dt.strftime('%Y-%m-%d %H:%M:%S'))

    # Overwrite "ts" data with the "readable timestamps" 
    data["ts"] = readable_timestamps
    # Save the "updated" data to a JSON file
    with open(f'{folder_path}{updated_filename}', 'w') as json_file:
        json.dump(data, json_file, indent=4)

else:
    print(f"Windy API request failed with status code {response.status_code}")


