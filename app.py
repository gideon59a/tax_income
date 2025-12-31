from flask import Flask, render_template, request, jsonify
import json

from tax_income.tax_years import calc_net
from shared_utils.my_utils.glogger import LoggerManager

glogger = LoggerManager(filename='tax_api.log')
logger = glogger.get_logger()
logger.debug(f"Start logging.")

app = Flask(__name__)

default_year = 2026
default_income =280000
default_at_pension_age = 'True'
index_html_params = {
    "default2": default_year,
    "default4": default_income,
    "at_pension_age": default_at_pension_age
}


@app.route('/')
def index():
    # Entering the main url activates this html page
    return render_template("index.html", **index_html_params)


@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()

    net_income, tax_yearly, marginal_tax_rate = 0, 0, 0
    year = data['val2']
    at_pension_age = data['at_pension_age']
    income = data['val4']

    # convert at_pension_age string to boolean
    at_pension_age_bool = json.loads(at_pension_age.lower())
    try:
        logger.info(f"Staring. year: {type(year)} {year}, income: {income}, at_pension_age: {at_pension_age_bool} ")
        yearly_income_for_tax, net_income, tax_yearly, marginal_tax_rate = (
            calc_net(year_str=year, income=int(income), log=logger, pension=at_pension_age_bool))
    except Exception as e:
        logger.error(f"Exception: {e}")
        print(f"*** FAILED **** error: {e}")

    # Create the json to return to the html page
    # ------------------------------------------
    row_inputs = [
        ["Year", f"{data['val2']}"],
        ["Income ils", int(data['val4']) if data['val4'].isdigit() else "Invalid int"],
        ["Pension year?", data['at_pension_age']]
    ]

    row_outputs = [
        ["Yearly income for tax", round(yearly_income_for_tax)],
        ["Net income ils, yearly", round(net_income)],
        ["Net income ils, monthly", round(net_income/12)],
        ["Tax ils, yearly", round(tax_yearly)],
        ["Tax margin %", marginal_tax_rate]
    ]

    return jsonify({
        "main_table": {
            "columns": ["Parameter", "Value"],
            "rows": row_inputs
        },
        "net_income_table": {
            "columns": ["Parameter", "Value"],
            "rows": row_outputs
        }
    })


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5011, debug=True)
