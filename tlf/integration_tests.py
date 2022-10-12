import unittest
from tlf import search_gulesider  # type: ignore


class TestGulesider(unittest.TestCase):
    def test_search_for_nonsense(self) -> None:
        persons, companies = search_gulesider("gurbagurba")
        self.assertEqual(len(persons), 0)
        self.assertEqual(len(companies), 0)

    def test_search_for_single_person(self) -> None:
        persons, companies = search_gulesider("Mads Robert Johansen")
        self.assertEqual(len(persons), 1)
        self.assertEqual(len(companies), 0)
        res = persons[0]
        self.assertEqual(res.name, "Mads Robert Johansen")
        self.assertEqual(res.street, "Otervegen 13")
        self.assertEqual(res.area, "9017 Tromsø")
        self.assertIn("959 62 392", res.phone_numbers)

    def test_search_for_single_company(self) -> None:
        persons, companies = search_gulesider("Blå Rock Cafe")
        self.assertEqual(len(persons), 0)
        self.assertEqual(len(companies), 1)
        res = companies[0]
        self.assertEqual(res.name, "Blå Rock Cafe AS")
        self.assertEqual(res.street, "Strandgata 14")
        self.assertEqual(res.area, "9008 Tromsø")
        self.assertIn("77 61 00 20", res.phone_numbers)

    def test_search_for_multiple_companies(self) -> None:
        _, companies = search_gulesider("Blå Rock")
        self.assertEqual(len(companies), 2)
        first, second = companies
        self.assertEqual(
            str(first), "Blå Rock Cafe AS\nStrandgata 14\n9008 Tromsø\nTlf: 77 61 00 20"
        )
        self.assertEqual(str(second), "Blå Rock Eiendom AS\nStorgata 37\n9008 Tromsø")

    def test_search_for_person_with_no_address(self) -> None:
        persons, companies = search_gulesider("David Andreas Swan")
        self.assertEqual(len(persons), 1)
        self.assertEqual(len(companies), 0)
        res = persons[0]
        self.assertEqual(res.name, "David Andreas Swan")
        self.assertEqual(res.street, "")
        self.assertEqual(res.area, "")
        self.assertIn("412 25 400", res.phone_numbers)

    def test_search_for_company_with_no_phone(self) -> None:
        persons, companies = search_gulesider("Chips og Dip AS")
        self.assertEqual(len(persons), 0)
        self.assertEqual(len(companies), 1)
        res = companies[0]
        self.assertEqual(res.name, "Chips og Dip AS")
        self.assertEqual(res.street, "Prestenggata 5")
        self.assertEqual(res.area, "9008 Tromsø")
        self.assertEqual(res.phone_numbers, [])


if __name__ == "__main__":
    from sys import argv

    if "-q" not in argv:
        print("These are integration tests that hit the Gulesider server directly.")
        if input("Are you sure you want to continue? [y/N] ").lower() not in (
            "y",
            "yes",
        ):
            print("Aborting test run")
            exit()
    unittest.main()
