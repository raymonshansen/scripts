import requests
import sys

def person(item: dict) -> dict[str, str]:
    return {
        "name": item["name"]["firstName"] + " " + item["name"]["lastName"],
        "street": item["addresses"][0]["streetName"] + " " + item["addresses"][0]["streetNumber"],
        "area": item["addresses"][0]["postalCode"] + " " + item["addresses"][0]["postalArea"],
        "phone_number": item["phones"][0]["number"]
    }

def company(item: dict) -> dict[str: str]:
    return {
        "name": item["name"],
        "street": item["addresses"][0]["streetName"] + " " + item["addresses"][0]["streetNumber"],
        "area": item["addresses"][0]["postalCode"] + " " + item["addresses"][0]["postalArea"],
        "phone_number": item["phones"][0]["number"]
    }

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

# Determine what type of search this would require, personal or company?
resp = requests.get(f"https://one-back.gulesider.no/custom/superSearch/gulesider/{search_word}")
match resp.content:
    case b"cs":
        num_type = "companies"
    case b"ps":
        num_type = "persons"
    case _:
        num_type = None

if num_type:
    url = f"https://www.gulesider.no/_next/data/icrEtxkRx7HLangO6erlo/nb/search/{search_word}/{num_type}/1/0.json?query={search_word}&searchType={num_type}&page=1&id=0"
    resp = requests.get(url)
    raw_search_result = dict(resp.json())["pageProps"]["initialState"][num_type]
else:
    print("Could not determine number type")
    sys.exit(1)

if raw_search_result:
    print(f"{len(raw_search_result)} results from searching '{search_word}':\n")
    match num_type:
        case "companies":
            results = [company(res) for res in raw_search_result]
        case "persons":
            results = [person(res) for res in raw_search_result]
        case _:
            results = []
    for result in results:
        print(result["name"])
        print(result["street"])
        print(result["area"])
        if include_num:
            print(f"Tlf: {result['phone_number']}")
        print()
else:
    print(f"No match searching: {search_word}")
    sys.exit(1)


