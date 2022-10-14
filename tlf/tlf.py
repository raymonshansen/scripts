from dataclasses import dataclass
from typing import Tuple
import requests
import sys


# The buildId for Gulesiders SPA changes every time they deploy
# so we need to fetch it every time we want to search
def get_url() -> str:
    gulesider_src = requests.get("https://www.gulesider.no/").text
    # The url is inside some embedded json, so we can just search for it
    build_id = gulesider_src.split('"buildId":"')[1].split('"')[0]
    return f"https://www.gulesider.no/_next/data/{build_id}/nb/search"


def from_optional(dictionary: dict, *keys: str) -> str:
    "Returns a string of the values of the given keys in the given dictionary"
    return " ".join(filter(None, (dictionary.get(key) for key in keys)))


@dataclass
class SearchResult:
    """Represents a search result from Gulesider

    Most properties can be empty, but printing the result directly
    will handle the display logic for you.

    >>> SearchResult({
    ...     "name": {
    ...         "firstName": "Ola",
    ...         "lastName": "Nordmann",
    ...     },
    ...     "addresses": [
    ...         {
    ...             "streetName": "Storgata",
    ...             "streetNumber": "1",
    ...             "postalCode": "1234",
    ...             "postalArea": "Oslo",
    ...         }
    ...     ],
    ...     "phones": [
    ...         {
    ...             "number": "12345678",
    ...         }
    ...     ],
    ... })
    SearchResult(name='Ola Nordmann', street='Storgata 1', area='1234 Oslo', phone_numbers=['12345678'])
    >>> SearchResult({
    ...     "name": "Nordmann AS",
    ...     "addresses": [
    ...         {
    ...             "streetName": "Sjøgata",
    ...             "streetNumber": "2",
    ...             "postalCode": "9000",
    ...             "postalArea": "Tromsø",
    ...         }
    ...     ],
    ...     "phones": [
    ...         {
    ...             "number": "98765432",
    ...         },
    ...         {
    ...             "number": "87654321",
    ...         }
    ...     ],
    ... })
    SearchResult(name='Nordmann AS', street='Sjøgata 2', area='9000 Tromsø', phone_numbers=['98765432', '87654321'])
    """

    name: str
    street: str
    area: str
    phone_numbers: list[str]

    def __init__(self, item: dict):
        self.name = (
            item["name"]
            # Companies have names as plain strings
            if isinstance(item["name"], str)
            # But persons have name dictionaries with optional properties
            else from_optional(item["name"], *item["name"].keys())
        )
        # Some results have no addresses
        address = item["addresses"][0] if item["addresses"] else {}
        self.street = from_optional(address, "streetName", "streetNumber")
        self.area = from_optional(address, "postalCode", "postalArea")
        self.phone_numbers = [p["number"] for p in item.get("phones", [])]

    def __str__(self):
        phone_numbers = "\n".join(f"Tlf: {p}" for p in self.phone_numbers)
        return "\n".join(
            filter(None, [self.name, self.street, self.area, phone_numbers])
        )


def search_gulesider(query: str) -> Tuple[list[SearchResult], list[SearchResult]]:
    url = get_url()
    # Searching for companies returns persons as well, so this url works for everything
    resp = requests.get(f"{url}/{query}/companies/1/0.json?query={query}")
    # The response is for a SPA built on Next.js, so we can dig
    # directly into the page props for our data
    page_props = dict(resp.json())["pageProps"]

    # No results can happen for unlisted numbers
    if "initialState" not in page_props:
        return [], []

    state = page_props["initialState"]
    persons = [SearchResult(res) for res in state["persons"]]
    companies = [SearchResult(res) for res in state["companies"]]

    return persons, companies


if __name__ == "__main__":
    from sys import argv

    prog, *args = argv
    if not args:
        print(f"Usage: {prog} <name or number>")
        sys.exit()

    query = " ".join(args)
    persons, companies = search_gulesider(query)

    num_hits = len(persons + companies)
    if num_hits == 0:
        print(f"No results for '{query}'")
        sys.exit()

    plural = "s" if num_hits > 1 else ""
    print(f"{num_hits} result{plural} for '{query}':\n")

    print("\n\n".join(str(res) for res in persons + companies))
