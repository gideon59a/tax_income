import os
import logging

from tax_general_calc import calc_year_tax
from shared_utils.my_utils.excel_rw import read_excel_file
from shared_utils.my_utils.glogger import LoggerManager
from info.tax_info import pension_ptor_per_month_dict

def calc_net(year_str, income, log, pension=False):
    """
    Calculates the tax and net income.
    Args:
        year (int): The year of the income
        income (int): Yearly gross income in ils
        log (logger)
        pension (bool): Is it a pension year, that is, after 67?
    Returns:
        net_income: yearly net income
        tax_yearly: Yearly tax deduced from the net income
        marginal_tax_rate: Of that tax, in percentage
    """

    if pension:
        pension_ptor_per_month = pension_ptor_per_month_dict[year_str]
        log.info(f"Pension PTOR per month: {pension_ptor_per_month} ILS")
        if year_str == "2026":  # Assuming I get just 3 months pension that year
            num_of_pension_month = 3
        else:
            num_of_pension_month = 12
        yearly_income_for_tax = income - pension_ptor_per_month * num_of_pension_month
        log.info(f"Reducing income amount for tax by {pension_ptor_per_month * num_of_pension_month} ILS because it is a pension year")
    else:
        yearly_income_for_tax = income
    log.info(f"Calculating tax for yearly_income_for_tax of {yearly_income_for_tax}")
    tax_yearly, marginal_tax_rate = calc_year_tax(year_str, yearly_income_for_tax, log=log, calc_nekudot_zikui=True)
    log.info(f"Tax per year {year_str} for yearly income {income} = {tax_yearly}"
             f" with marginal_tax_rate = {marginal_tax_rate}%")
    net_income = income - tax_yearly
    log.info(f"net income = {round(net_income)}")
    return yearly_income_for_tax, net_income, tax_yearly, marginal_tax_rate


def not_used__read_income_and_tax(year, income):

    run_py_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the directory where run.py is located
    info_dir_path = os.path.join(run_py_dir, 'info')  # Construct the path to the info_dir subdirectory
    info_py_abs_path = os.path.join(info_dir_path, 'prv_income_info.xlsx')  # Construct the full absolute path to info.py
    print(f"Absolute path of run.py's directory: {run_py_dir}")
    print(f"Absolute path of info.py: {info_py_abs_path}")

    dict_read = read_excel_file(info_py_abs_path, log=logger, abs_file_path=None, sheet_names_list=None)
    print(dict_read)


if __name__ == "__main__":
    glogger = LoggerManager(filename='tax.log')
    logger = glogger.get_logger()
    logger.debug(f"Start logging.")

    logger.info(f"\n ****** Calculate for a pension year ***")
    yearly_net_income_pension, tax, tax_margin = calc_net(2025, income=23000*12, log=logger, pension=True)
    logger.info(f"yearly_net_income if pension: {round(yearly_net_income_pension)}. "
                f"PER MONTH={round(yearly_net_income_pension/12)}. \n"
                f"Yearly tax={tax} with {tax_margin}% margin\n")

    logger.info(f"\n ****** Calculate for a REGULAR (non pension) year ***")
    yearly_net_income_regular, tax, tax_margin = calc_net(2025, income=23000*12, log=logger, pension=False)
    logger.info(f"yearly_net_income for regular: {round(yearly_net_income_regular)}. "
                f"PER MONTH={round(yearly_net_income_regular/12)}. \n"
                f"Yearly tax={tax} with {tax_margin}% margin\n")

    diff_between_pension_and_regualr = round(yearly_net_income_pension - yearly_net_income_regular)
    logger.info(f"Diff between a pension and a non-pension tax: {diff_between_pension_and_regualr} ILS")
