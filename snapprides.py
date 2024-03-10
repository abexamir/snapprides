import requests
import json
import os
import datetime

from selenium import webdriver

def capture_screenshot(url, filename):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.save_screenshot(filename)
    driver.quit()

def get_filtered_rides(url: str, headers: dict, keyword: str, page: int):
    try:
        response = requests.get(f"{url}?page={page}", headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        return []
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        return []
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        return []
    except requests.exceptions.RequestException as err:
        print ("Something went wrong",err)
        return []

    data = response.json().get('data', {})
    rides = data.get('rides', [])
    filtered_rides = [ride for ride in rides if keyword in ride.get('origin', {}).get(
        'formatted_address', '') or keyword in ride.get('destination', {}).get('formatted_address', '')]
    return filtered_rides

def fetch_rides(url: str, headers: dict, keyword: str, pages: int):
    all_filtered_rides = []
    for i in range(1, pages+1):
        new = get_filtered_rides(url, headers, keyword, i)
        if new:
            all_filtered_rides.extend(new)

    final = [
        {
            'price': ride.get('final_price'),
            'receipt_link': ride.get('receipt_link'),
            'date': ride.get('created_at').split(' ')[0],
            'time': ride.get('created_at').split(' ')[1],
            'id': ride.get('human_readable_id'),
            'origin': ride.get('origin', {}).get('formatted_address'),
            'destination': ride.get('destination', {}).get('formatted_address'),
        }
        for ride in all_filtered_rides]

    return final

def generate_markdown(json_path, markdown_path, keyword):
    with open(json_path, 'r') as json_file:
        final_result = json.load(json_file)

    with open(markdown_path, 'w') as md_file:
        md_file.write("<div dir='rtl'>\n\n")  # Start of RTL
        md_file.write(f"# سفرهای اسنپ از مبدا/به مقصد {keyword}  \n")
        md_file.write(f"**تعداد سفر ها:** {final_result['total_rides']}  \n")
        md_file.write(f"**هزینه کل:** {final_result['total_price']} ریال \n")
        md_file.write(f"## لیست سفر ها\n")
        for i, ride in enumerate(final_result['rides']):
            md_file.write(f"## سفر {i + 1}\n")  # Ride title
            md_file.write(f"** مبدا:  ** {ride['origin']}  \n")
            md_file.write(f"** مقصد:  ** {ride['destination']}  \n")
            md_file.write(f"**قیمت:  ** {ride['price']}  \n")
            md_file.write(f"**تاریخ:  ** {ride['date']}  \n")
            md_file.write(f"**رسید:** [لینک]  ({ride['receipt_link']})\n")
            md_file.write(f"![اسکرین شات]({ride['screenshot_file']})  \n")
            md_file.write("\n")
        md_file.write("</div>\n")  # End of RTL

def generate_json(keyword, bearer_token, pages, workspace):
    url = 'https://app.snapp.taxi/api/api-base/v2/passenger/ride/history'
    os.makedirs(f"{workspace}screenshots/", exist_ok=True)
    headers = {'authorization': f"Bearer {bearer_token}"}
    rides = fetch_rides(url, headers, keyword, pages)
    final_result = {"total_price": sum(ride['price'] for ride in rides), "total_rides": len(rides), "rides": []}
    for ride in rides:
        screenshot_name = f"{workspace}/screenshots/{ride['date']}_{ride['price']}.png"
        capture_screenshot(ride['receipt_link'], screenshot_name)
        ride['screenshot_file'] = screenshot_name
        final_result['rides'].append(ride)
        print(ride)

    with open(f"{workspace}result.json", 'w') as f:
        json.dump(final_result, f, indent=4)
    return f"{workspace}result.json"

if __name__ == "__main__":
    bearer_token = input("Enter your token, it's format is: Bearer <token>: ")
    if not bearer_token:
        print("Please enter your token")
        exit(1)
    if bearer_token.startswith('Bearer '):
        print("Please enter your token without 'Bearer '")
        exit(1)
    keyword = input("Enter your keyword to search for in source and destination addresses: ")
    workspace = os.path.expanduser('~') + '/snapp_reports/' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '/'
    pages = int(input("Enter number of pages to fetch, each page contains 14 rides, default is 2): ") or 2)
    json_path = generate_json(keyword, bearer_token, pages, workspace)
    generate_markdown(json_path, f"{workspace}report.md", keyword)

