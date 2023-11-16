import requests
import json
# import datetime
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta


load_dotenv()  # Load environment variables from .env file

# Replace 'YOUR_API_KEY' with the actual API key you received from Windy.
api_key = os.environ.get("WINDY_API_KEY")
# Define files' path and names
folder_path = 'Windy_API/data/'
original_filename = 'windy_data_original.json'
updated_filename = 'windy_data_updated.json'
future_filename = 'windy_data_future.json'
now_filename = 'windy_data_now.json'

# Define the API endpoint and parameters.
endpoint = 'https://api.windy.com/api/point-forecast/v2'
# Define latitude and longitude (sample: 33.6563005931192, -118.00345056657193)
latitude = 24.873355012923216
longitude = 121.84097563158377
model = "gfsWave"
parameters = ["waves", "swell1", "swell2"]

params = {
    "lat": latitude,
    "lon": longitude,
    "model": model,
    "parameters": parameters,
    "levels": ["surface"],
    "key": api_key
}


# Make the API request.
header = {"Content-Type" :"application/json"}
response = requests.post(endpoint, json=params, headers=header)
print(response)

if response.status_code == 200:
    print(f"Windy API request succeed with status code {response.status_code}")

    ###--- For the Original Data ---###
    data = response.json()
    # print(json.dumps(data, indent=4))

    # Save the "original" data to a JSON file
    with open(f'{folder_path}{original_filename}', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    ###--- For the Updated Data ---###
    # Convert the timestamps to human-readable dates
    timestamps = data.get("ts", [])
    readable_timestamps = []

    # Convert each timestamp to a human-readable date and time
    for timestamp in timestamps:
        dt = datetime.utcfromtimestamp(timestamp / 1000)  # Divide by 1000 to convert from milliseconds to seconds
        print("Readable Timestamp:", dt)
        readable_timestamps.append(dt.strftime('%Y-%m-%d %H:%M:%S'))

    # Overwrite "ts" data with the "readable timestamps" 
    data["ts"] = readable_timestamps

    # Overwrite the "null" value for each tag
    for tag in ["waves_height-surface", "waves_direction-surface", "waves_period-surface",
                "swell1_height-surface", "swell1_direction-surface", "swell1_period-surface",
                "swell2_height-surface", "swell2_direction-surface", "swell2_period-surface"]:
        for i in range(len(data[tag])):
            if data[tag][i] is None:
                if i != 0:
                    data[tag][i] = data[tag][i-1] if data[tag][i-1] is not None else data[tag][i+1]
                else:
                    data[tag][i] = 0.1


    # Save the "updated" data to a JSON file
    with open(f'{folder_path}{updated_filename}', 'w') as json_file:
        json.dump(data, json_file, indent=4)


    ###--- For the Future Data ---###
    # Get rid of the data of first date and last date because they are not complete
    # Determine the indices corresponding to the first and last dates
    first_date = data["ts"][0].split()[0]
    last_date = data["ts"][-1].split()[0]
    print("First Last Date Check: ", first_date, last_date)

    first_date_indices = [i for i, ts in enumerate(data["ts"]) if first_date in ts]
    last_date_indices = [i for i, ts in enumerate(data["ts"]) if last_date in ts]

    # Combine the indices for removal
    indices_to_remove = set(first_date_indices + last_date_indices)

    # Remove the corresponding data for each tag
    for tag in ["ts", "waves_height-surface", "waves_direction-surface", "waves_period-surface",
                "swell1_height-surface", "swell1_direction-surface", "swell1_period-surface",
                "swell2_height-surface", "swell2_direction-surface", "swell2_period-surface"]:
        data[tag] = [value for i, value in enumerate(data[tag]) if i not in indices_to_remove]

    # Now, 'data' has the first and last date data removed for each tag

    # Save the updated data to a "FUTURE" JSON file
    start_date = datetime.strptime(first_date, "%Y-%m-%d") + timedelta(days=1)
    end_date = datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=1)
    print("Start End Date for Future 'tp' Check: ", start_date, end_date)
    tp = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
    data["tp"] = tp
    with open(f'{folder_path}{future_filename}', 'w') as json_file:
        json.dump(data, json_file, indent=4)

else:
    print(f"Windy API request failed with status code {response.status_code}")




###--- For the Now Data ---###
# Load the original data from the file
# with open(f'{folder_path}{future_filename}', 'r') as file:
#     data = json.load(file)

# Extract timestamps and units from the original data
timestamps = data.get("ts", [])
units = data.get("units", {})

# Define the date range you want to include in the new file
start_date = datetime.strptime(first_date, "%Y-%m-%d")
end_date = datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=1)
date_range = [start_date + timedelta(hours=i * 3) for i in range((end_date - start_date).days * 8)]

end_date = datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=2)
tp = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
print("Start End Date for Now 'tp' Check: ", start_date, end_date)

# Create a new dictionary for the modified data
new_data = {
    "ts": [date.strftime('%Y-%m-%d %H:%M:%S') for date in date_range],
    "units": units,
}

# Copy the data for each parameter from the original data for dates 2023-11-16 to 2023-11-23
for parameter, values in data.items():
    if parameter not in ["ts", "tp", "units", "warning"]:
        # print("parameter: ", parameter, len(values[: -8]))
        new_data[parameter] = [None] * 8 
        new_data[parameter][8:] = values[: -8]

# Copy the data for date 2023-11-15
new_data["waves_height-surface"][:8] = data["waves_height-surface"][:8]
new_data["waves_direction-surface"][:8] = data["waves_direction-surface"][:8]
new_data["waves_period-surface"][:8] = data["waves_period-surface"][:8]
new_data["swell1_height-surface"][:8] = data["swell1_height-surface"][:8]
new_data["swell1_direction-surface"][:8] = data["swell1_direction-surface"][:8]
new_data["swell1_period-surface"][:8] = data["swell1_period-surface"][:8]
new_data["swell2_height-surface"][:8] = data["swell2_height-surface"][:8]
new_data["swell2_direction-surface"][:8] = data["swell2_direction-surface"][:8]
new_data["swell2_period-surface"][:8] = data["swell2_period-surface"][:8]
new_data["warning"] = data["warning"]
new_data["tp"] = tp

# Save the modified data to a new JSON file
with open(f'{folder_path}{now_filename}', 'w') as file:
    json.dump(new_data, file, indent=4)

