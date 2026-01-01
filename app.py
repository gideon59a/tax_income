import argparse
from flask import Flask, render_template, request, jsonify

from tax_income.tax_years import calc_net
from shared_utils.my_utils.glogger import LoggerManager
from shared_utils.my_utils.structs import parse_bool

glogger = LoggerManager(filename='tax_api.log')
logger = glogger.get_logger()
logger.debug("Start logging.")

app = Flask(__name__)

default_year = 2026
default_income = 280000
default_at_pension_age = True

index_html_params = {
    "default2": default_year,
    "default4": default_income,
    "at_pension_age": str(default_at_pension_age),
}


def calc_payload(year, income, at_pension_age_bool):
    logger.info("Calc. year=%r income=%r pension=%r", year, income, at_pension_age_bool)
    yearly_income_for_tax, net_income, tax_yearly, marginal_tax_rate = (
        calc_net(year_str=str(year), income=int(income), log=logger, pension=at_pension_age_bool)
    )

    row_inputs = [
        ["Year", str(year)],
        ["Income ils", int(income)],
        ["Pension year?", at_pension_age_bool],
    ]
    row_outputs = [
        ["Yearly income for tax", round(yearly_income_for_tax)],
        ["Net income ils, yearly", round(net_income)],
        ["Net income ils, monthly", round(net_income / 12)],
        ["Tax ils, yearly", round(tax_yearly)],
        ["Tax margin %", marginal_tax_rate],
    ]
    return {
        "main_table": {"columns": ["Parameter", "Value"], "rows": row_inputs},
        "net_income_table": {"columns": ["Parameter", "Value"], "rows": row_outputs},
    }

# This is the main code for calculation tax per user inputs
def handle_calc_request(data, web_interface=False):
    try:
        if web_interface:  # Inputs read from the web page the program opens
            year = data["val2"]
            income = data["val4"]
            at_pension_age = data.get("at_pension_age")
        else:  # http interface
            year = data.get("year", default_year)
            income = data.get("income", default_income)
            at_pension_age = data.get("at_pension_age", default_at_pension_age)

        at_pension_age_bool = parse_bool(at_pension_age)
        return calc_payload(year=year, income=income, at_pension_age_bool=at_pension_age_bool)

    except Exception as e:
        logger.exception("handle_calc_request failed")
        raise e


@app.route("/")
def index():
    return render_template("index.html", **index_html_params)

@app.route("/process", methods=["POST"])
def process():
    try:
        data = request.get_json(silent=True) or {}
        return jsonify(handle_calc_request(data, web_interface=True))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/v1/calc", methods=["POST"])
def api_calc_post():
    try:
        data = request.get_json(silent=True) or {}
        return jsonify(handle_calc_request(data))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--test", action="store_true", help="Run a self-test against /api/v1/calc (no server needed)")
    args = p.parse_args()

    if args.test:
        from test.test import run_self_test
        run_self_test()
        # The below is just an example of a curl command performing the test
        #from test.test import run_curl_self_test
        # run_curl_self_test()
    else:
        app.run(host="127.0.0.1", port=5011, debug=True)
