import requests
import sys
import pprint
from typing import Dict, Any

BASE_URL = "https://www.gulesider.no"
def result_item_to_dict(item: dict)-> Dict[str, str]:
    d = dict()
    d["name"] = item["name"]
    d["street"] = f'{item["address"][0]["streetName"]} {item["address"][0]["streetNumber"]}'
    d["area"] = f'{item["address"][0]["postCode"]} {item["address"][0]["postArea"]}'
    d["phone_number"] = ""
    if item["phoneNumbers"]:
        d["phone_number"] = f'{item["phoneNumbers"][0]["phoneNumber"]}'
    return d

# No arguments is handled py the PowerShell-script calling tlf.py
include_num = False
if len(sys.argv) == 2:
    search_word: str = sys.argv[1]
    if not search_word.isdigit():
        include_num = True
elif len(sys.argv) > 2:
    sys.argv.pop(0)
    if not sys.argv[0].isdigit():
        search_word = ' '.join(sys.argv)
        include_num = True
    else:
        print(f"Searching for {sys.argv[0]}...\n")
        search_word = sys.argv[0]

query_dict = {"query": search_word, "profile": "no"}
resp = requests.get(f"{BASE_URL}/api/search/count", params=query_dict)
response_dict = dict(resp.json())

# Determine what type of search this would require, personal or company?
num_type = ""
if response_dict["ps"]:
    num_type = "ps"
if response_dict["cs"]:
    num_type = "cs"
if num_type:
    query_dict = {"query": search_word,
                  "sortOrder": "default",
                  "profile": "no",
                  "page": "1",
                  "lat": "0",
                  "lng": "0",
                  "limit": "25",
                  "client": "true",
                 }
    resp = requests.get(f"{BASE_URL}/api/{num_type}", params=query_dict)
    raw_search_result = dict(resp.json())
else:
    print("Could not determine number type")
    sys.exit(1)

hits = raw_search_result["hits"]
if hits:
    print(f"{hits} results from searching '{search_word}':\n")
    results: Dict[str, list] = dict()
    results["results"] = [result_item_to_dict(item) for item in raw_search_result["items"]]
    for result in results["results"]:
        print(result["name"])
        print(result["street"])
        print(result["area"])
        if include_num:
            print(f"Tlf: {result['phone_number']}")
        print()
else:
    print(f"No match searching: {search_word}")
    sys.exit(1)


