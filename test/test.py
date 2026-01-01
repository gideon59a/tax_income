import json
from app import app


def run_self_test():
    payload = {
        "year": "2026",
        "income": 280000,
        "at_pension_age": True,
    }

    with app.test_client() as c:
        resp = c.post("/api/v1/calc", json=payload)

    if resp.status_code != 200:
        raise SystemExit(f"TEST FAILED: HTTP {resp.status_code}: {resp.get_data(as_text=True)}")

    data = resp.get_json(silent=True) or {}
    if "net_income_table" not in data or "rows" not in data["net_income_table"]:
        raise SystemExit(f"TEST FAILED: unexpected JSON shape: {data}")

    # basic sanity checks (adjust as you like)
    rows = data["net_income_table"]["rows"]
    as_dict = {k: v for k, v in rows}
    if as_dict.get("Net income ils, yearly") is None:
        raise SystemExit("TEST FAILED: missing Net income ils, yearly")
    if as_dict["Net income ils, yearly"] <= 0:
        raise SystemExit(f"TEST FAILED: net income not positive: {as_dict['Net income ils, yearly']}")

    # Verify result
    expected_yearly_for_tax = 263734
    expected_net_yearly = 240458
    expected_tax_yearly = 39542
    expected_tax_margin_percentage = 31

    assert as_dict["Yearly income for tax"] == expected_yearly_for_tax, \
        f"Error in Yearly income for tax = {as_dict["Yearly income for tax"]} - should be {expected_yearly_for_tax}"
    assert as_dict["Net income ils, yearly"] == expected_net_yearly, \
        f"Error in Net income ils, yearly = {as_dict["Net income ils, yearly"]} - should be {expected_net_yearly}"
    assert as_dict["Tax ils, yearly"] == expected_tax_yearly, \
        f"Error in Tax ils, yearly = {as_dict["Tax ils, yearly"]} - should be {expected_tax_yearly}"
    assert as_dict["Tax margin %"] == expected_tax_margin_percentage, \
        f"Error in Tax margin % = {as_dict["Tax margin %"]} - should be {expected_tax_margin_percentage}"

    print(json.dumps(data, ensure_ascii=False, indent=2)[:1500])  # avoid dumping huge output
    print("**************** TEST OK  **********************")


# Just for information, the below shows the Equivalent Bash curl Command
def run_curl_self_test():
    from app3 import app

    test_data = {
        "year": "2026",
        "income": "280000",
        "at_pension_age": "True"  # This is for json format. Actuallty, it could be also just True,
                                  # as the backend handles it using the parse_bool command
    }

    print("\n--- Python Test Request ---")
    with app.test_client() as c:
        res = c.post("/api/v1/calc", json=test_data)
        print("Status code:", res.status_code)
        print("Response JSON:", res.json)

    print("\n--- Equivalent Bash curl Command ---")
    curl_cmd = (
        "curl -X POST http://127.0.0.1:5011/api/v1/calc "
        "-H 'Content-Type: application/json' "
        f"-d '{json.dumps(test_data)}'"
    )
    print(curl_cmd)
