import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()  # Load environment variables from .env file


folder_path="CWA_API/Tide/" 
original_filename="cwa_tide_original.json"
sorted_filename = 'cwa_tide_sorted.json'
api_key = os.environ.get("CWA_API_KEY")


def fetch_cwa_tide_data(format="JSON"):
    try:
        # Construct the API URL
        dataid = 'F-A0021-001'
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{dataid}?Authorization={api_key}&format={format}"

        # Send an HTTP GET request to the API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print(f"CWA Tide API request succeeded with status code {response.status_code}")

            data = response.json()  # Use response.text for XML
            # print(json.dumps(data, indent=4))

            # Save the "original" data to a JSON file
            with open(os.path.join(folder_path, original_filename), "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

            print(f"CWA Tide Data has been saved to '{os.path.join(folder_path, original_filename)}'.")

        
        
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

            print(f"CWA Tide Data Sorted JSON data with sorted dates saved to {folder_path}{sorted_filename}.")
            
            return data

        else:
            print(f"CWA Tide API request failed with status code {response.status_code}")
            return None

    except Exception as e:
        # Handle exceptions, if any
        print(f"Error: {e}")
        return None


# Call the function to fetch and save CWA data
cwa_data = fetch_cwa_tide_data()



# Get the absolute path to the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
file_name = os.path.join(script_dir, sorted_filename)

def getThreeDays(locationId):
    try:
        # Convert the data to JSON format
        # json_data = json.dumps(data)

        
        with open(file_name, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        # Filter the desired locationId
        filtered_data = {
            "success": data["success"],
            "result": data["result"],
            "records": {
                "dataid": data["records"]["dataid"],
                "note": data["records"]["note"],
                "TideForecasts": [
                    forecast for forecast in data["records"]["TideForecasts"]
                    if forecast["Location"]["LocationId"] == locationId
                ]
            }
        }

        # Save the modified JSON data with sorted "Daily" data to a new file
        with open(f"{folder_path}locationid.json", "w", encoding="utf-8") as json_file:
            json.dump(filtered_data, json_file, ensure_ascii=False, indent=4)


        temp = []
        # for x0 and x1
        for i in range(2):
            temp.append({
            "x": i,
            "y": 200 - 100*i,
            "Date": "",
            "Time": "" 
        })
        days_processed = 0  # Counter for tracking the number of days processed
        
        for location in filtered_data["records"]["TideForecasts"]:
            for daily_data in location["Location"]["TimePeriods"]["Daily"]:
                for each_time in daily_data["Time"]:
                    # Parse the original datetime string
                    parsed_datetime = datetime.strptime(each_time["DateTime"], "%Y-%m-%dT%H:%M:%S%z")

                    # Extract the date and time parts
                    formatted_date = parsed_datetime.strftime("%m/%d")
                    formatted_time = parsed_datetime.strftime("%H:%M")
                    formatted_hour = int(parsed_datetime.strftime("%H"))
                    formatted_minute = int(parsed_datetime.strftime("%M"))

                    # x range is 0-720
                    x = formatted_hour*10 + int(formatted_minute/6) + (days_processed*240)

                    # y range is 0-200, 100 is the middle base line
                    y = int(100 - each_time["TideHeights"]["AboveLocalMSL"])

                    temp.append({
                        "x": x,
                        "y": y,
                        "Date": formatted_date,
                        "Time": formatted_time
                    })
                
                # Increment the counter after processing each day
                days_processed += 1

                # Break the loop if we have processed data for three days
                if days_processed >= 3:
                    break
            
            # Break the outer loop if we have processed data for three days
            if days_processed >= 3:
                break

        # for x719 and x720
        for i in range(2):
            temp.append({
            "x": i + 719,
            "y": 100 + 100*i,
            "Date": "",
            "Time": "" 
        })

        transfered_data = {
            "data": temp
        }

        # print("transfered_data: ", transfered_data)

        return transfered_data
    except Exception as e:
        # Handle exceptions, if any
        return f"Error: {e}"


# Example usage:
LocationID = "A00100"
json_result = getThreeDays(LocationID)
print(json.dumps(json_result, indent=4))

