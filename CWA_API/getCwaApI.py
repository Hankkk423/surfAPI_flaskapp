import requests
import json
import os
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file

# Replace these values with your actual dataid and apikey
api_key = os.environ.get("CWA_API_KEY")
dataid = 'F-A0021-001'
format = "JSON"  # You can also use "XML" if needed
# Specify the desired LocationId
desired_location_id = "A00100"
# Define files' path and names
folder_path = 'CWA_API/'
original_filename = 'cwa_data_original.json'
sorted_filename = 'cwa_data_sorted.json'
id_filename = f"cwa_data_{desired_location_id}.json"

# Construct the API URL
url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{dataid}?Authorization={api_key}&format={format}"

# Send an HTTP GET request to the API
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print(f"CWA API request succeed with status code {response.status_code}")
    
    data = response.json()  # Use response.text for XML
    print(json.dumps(data, indent=4))


    # Save the "original" data to a JSON file
    with open(f"{folder_path}{original_filename}", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print(f"CWA Data has been saved to '{folder_path}{original_filename}'.")

else:
    print(f"CWA API request failed with status code {response.status_code}")



# Sort the "Date" AND Map mandarin to english
# Define mapping for TideRange and Tide values
tide_range_mapping = {"小": "S", "中": "M", "大": "L"}
tide_mapping = {"乾潮": "L", "滿潮": "H"}

if "TideForecasts" in data["records"]:
    # Sort the "Daily" data based on the "Date" field within each "TideForecasts"
    for location in data["records"]["TideForecasts"]:
        if "Daily" in location["Location"]["TimePeriods"]:
            location["Location"]["TimePeriods"]["Daily"] = sorted(location["Location"]["TimePeriods"]["Daily"], key=lambda x: x["Date"])

            # Modify TideRange and Tide values
            for daily_data in location["Location"]["TimePeriods"]["Daily"]:
                daily_data["TideRange"] = tide_range_mapping.get(daily_data["TideRange"], daily_data["TideRange"])
                for each_time in daily_data["Time"]:
                    each_time["Tide"] = tide_mapping.get(each_time["Tide"], each_time["Tide"])

# Save the modified JSON data with sorted "Daily" data to a new file
with open(f"{folder_path}{sorted_filename}", "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

print(f"Sorted JSON data with sorted dates saved to {folder_path}{sorted_filename}.")


# Extract specific "LocationId data(desired_location_id)" from "sorted.json data"
# Filter the data for the specified LocationId (the data here is sorted already)

# with open(f"{folder_path}{sorted_filename}", "r", encoding="utf-8") as json_file:
#     data = json.load(json_file)
filtered_data = {
    "success": data["success"],
    "result": data["result"],
    "records": {
        "dataid": data["records"]["dataid"],
        "note": data["records"]["note"],
        "TideForecasts": [
            forecast for forecast in data["records"]["TideForecasts"]
            if forecast["Location"]["LocationId"] == desired_location_id
        ]
    }
}

# Save the "filtered id data" to a new file
with open(f"{folder_path}{id_filename}", "w", encoding="utf-8") as json_file:
    json.dump(filtered_data, json_file, ensure_ascii=False, indent=4)

print(f"Filtered data for LocationId {desired_location_id} saved to '{folder_path}{id_filename}'.")

