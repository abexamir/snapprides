# Snapp Rides Report Generator

This Python script generates a report of your Snapp rides. It fetches ride data, captures screenshots of the receipts, and saves the data in a JSON file. It also generates a markdown report.

## How to Use

1. Run the script: `python snapprides.py`
2. When prompted, enter your bearer token. This should be in the format `<token>`. Do not include 'Bearer ' in your input.
3. Enter a keyword to search for in source and destination addresses.
4. Enter the number of pages to fetch. Each page contains 14 rides. The default is 2 if you don't enter a value.
5. The script will generate a JSON file with the ride data and a markdown report.

## Output

The script generates two files in a directory under `~/snapp_reports/` with a timestamp:

- `result.json`: This file contains the total price of all rides, the total number of rides, and a list of all rides. Each ride in the list includes the date, price, and a link to a screenshot of the receipt.
- `report.md`: This is a markdown report of the rides.

## Requirements

- Python 3
- Libraries: os, datetime, json, selenium