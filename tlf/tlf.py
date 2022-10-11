import requests
import sys

# This might change when Gulesider is updated
BASE_URL = "https://www.gulesider.no/_next/data/icrEtxkRx7HLangO6erlo/nb/search/"


def filter_empty(dictionary):
    "Removes all empty values from the given dictionary"
    return {k: v for k, v in dictionary.items() if v}


def from_optional(dictionary: dict, *keys: str) -> str:
    "Returns a string of the values of the given keys in the given dictionary"
    return " ".join(filter(None, (dictionary.get(key) for key in keys)))


def person(item: dict) -> dict[str, str]:
    address = item["addresses"][0]
    return {
        "name": from_optional(item["name"], *item["name"].keys()),
        "street": from_optional(address, "streetName", "streetNumber"),
        "area": from_optional(address, "postalCode", "postalArea"),
        "phone_numbers": "\n".join(
            f"Tlf: {p['number']}" for p in item.get("phones", [])
        ),
    }


def company(item: dict) -> dict[str, str]:
    address = item["addresses"][0]
    return {
        "name": item["name"],
        "street": from_optional(address, "streetName", "streetNumber"),
        "area": from_optional(address, "postalCode", "postalArea"),
        "phone_number": "\n".join(
            f"Tlf: {p['number']}" for p in item.get("phones", [])
        ),
    }


def main(search_word: str):
    # Searching for companies returns persons as well, so this url works for everything
    resp = requests.get(
        f"{BASE_URL}{search_word}/companies/1/0.json?query={search_word}&searchType=companies&page=1&id=0"
    )
    # The response is for a SPA built on Next.js, so we can dig
    # directly into the page props for our data
    raw_search_result = dict(resp.json())["pageProps"]

    # Happens for unlisted numbers
    if "initialState" not in raw_search_result:
        print(f"No results for '{search_word}'")
        sys.exit(1)

    state = raw_search_result["initialState"]

    num_hits = state["totalHits"]
    if num_hits == 0:
        print(f"No results for '{search_word}'")
        sys.exit(1)

    companies = [filter_empty(company(res)) for res in state["companies"]]
    persons = [filter_empty(person(res)) for res in state["persons"]]

    plural = "s" if num_hits > 1 else ""
    print(f"{num_hits} result{plural} for '{search_word}':\n")

    for result in persons + companies:
        print("\n".join(result.values()), end="\n\n")


if __name__ == "__main__":
    from sys import argv

    prog, *args = argv
    if not args:
        print(f"Usage: {prog} <name or number>")
        sys.exit()

    main(" ".join(args))
