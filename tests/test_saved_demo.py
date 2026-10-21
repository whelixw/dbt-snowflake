"""Offline portfolio checks: run with python -m unittest discover -s tests."""
import csv
from decimal import Decimal
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class SavedDemoTests(unittest.TestCase):
    def test_verified_snapshot(self):
        with (ROOT / "dashboard/data/fct_coffee_shop_sales.csv").open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 149116)
        self.assertEqual(len({r["TRANSACTION_ID"] for r in rows}), 149116)
        self.assertEqual(sum(int(r["TRANSACTION_QTY"]) for r in rows), 214470)
        self.assertEqual(sum(Decimal(r["REVENUE"]) for r in rows), Decimal("698812.33"))
        self.assertEqual(min(r["TRANSACTION_DATE"] for r in rows), "2023-01-01")
        self.assertEqual(max(r["TRANSACTION_DATE"] for r in rows), "2023-06-30")
        self.assertTrue(all(Decimal(r["REVENUE"]) == int(r["TRANSACTION_QTY"]) * Decimal(r["UNIT_PRICE"]) for r in rows))

    def test_saved_demo_without_snowflake(self):
        with patch("streamlit.connection", side_effect=AssertionError("Offline mode contacted Snowflake")) as connection:
            app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.radio[0].value, "Saved demo")
            self.assertEqual(len(app.text_input), 0)
            self.assertEqual([m.value for m in app.metric][:3], ["698,812.33", "149,116", "214,470"])
            app.multiselect[0].set_value(["Lower Manhattan"]).run()
            self.assertFalse(app.exception)
            self.assertNotEqual(app.metric[0].value, "698,812.33")
            app.button[0].click().run()
            self.assertEqual(app.metric[0].value, "698,812.33")
            app.multiselect[0].set_value([]).run()
            self.assertFalse(app.exception)
            self.assertTrue(app.info)
            app.radio[0].set_value("Live Snowflake").run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.text_input), 2)
            app.radio[0].set_value("Saved demo").run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.text_input), 0)
            self.assertEqual(app.metric[0].value, "698,812.33")
            connection.assert_not_called()


if __name__ == "__main__":
    unittest.main()
