from tax_income.info.tax_info import tax_steps, value_nekudot_zikui_per_month_dict


def calc_year_tax(year_str, year_income: int, log, calc_nekudot_zikui=True):
    """
    Calculates the yearly tax
    Args:
        year: int or str
        calc_nekudot_zikui - If True then take into account the nekudot zikui
    Returns:
        tax: tax amount in ils
        marginal_tax_rate: The max tax step paid, in percentage
    """

    log.info(f"Calculate the tax amount for year {year_str} per the yearly income for tax {year_income}")

    tax_steps_year = tax_steps[year_str]

    tax = 0
    income_left_for_calc_tax = year_income
    previuos_max_annual_ils = 0
    marginal_tax_rate = 0
    for step_info in tax_steps_year:
        key = next(iter(step_info))  # The step has a single ket-value pair, so it gets the 1st and only key
        params = step_info[key]
        log.debug(f"key {key}, params {params}")
        log.debug(f"income left for tax calc: {income_left_for_calc_tax} previuos_max_annual_ils : {previuos_max_annual_ils}"
                  f"----------------------------------------------------------------------")
        this_step_max_amount = params["max_annual_ils"] - previuos_max_annual_ils
        amount_to_tax_in_this_step = min(income_left_for_calc_tax, this_step_max_amount)
        this_step_tax = amount_to_tax_in_this_step * params["tax_percentage"] / 100
        tax += this_step_tax
        log.info(f"Tax calculated for step {step_info[key]} is {this_step_tax}. Accumulated tax: {tax}")

        previuos_max_annual_ils = params["max_annual_ils"]
        income_left_for_calc_tax -= amount_to_tax_in_this_step
        log.info(f"Income left for tax calculation: {income_left_for_calc_tax}")

        if income_left_for_calc_tax == 0:
            marginal_tax_rate = params["tax_percentage"]
            log.debug(f"Tax calc ends. Yearly tax (w/o nekudot zikui) = {tax}, "
                      f"with marginal tax rate = {marginal_tax_rate}%")
            break
    if income_left_for_calc_tax != 0:
        log.error(f"Code error in tax calc")
        exit(1)

    if calc_nekudot_zikui:
        value_nekudot_zikui_per_month = value_nekudot_zikui_per_month_dict[year_str]
        log.info(f"Deducing {value_nekudot_zikui_per_month * 12} ILS due to nekudot zikui")
        tax -= value_nekudot_zikui_per_month * 12
        tax = max(tax, 0)

    return tax, marginal_tax_rate


def test_calc_year_tax(log):
    # Code test
    test_income = [50000, 100000, 250000, 500000]
    test_tax = [5000, 10635, 45574, 132303]
    for n in range(len(test_income)):
        tax, marginal_tax_rate = calc_year_tax("2025", test_income[n], log, calc_nekudot_zikui=False)
        print(f"For income {test_income[n]} the tax is {tax} "
              f"with marginal tax rate = {marginal_tax_rate}%")
        assert round(tax) == test_tax[n], f"Error in tax calc for {test_income[n]}"
    # Test also with nekudot_zikui
    test_income = [250000]
    test_tax = [45574 - 6534]
    tax, marginal_tax_rate = calc_year_tax("2025", test_income[0], log)
    log.info(f"For income {test_income[0]} the tax is after nekudot_zikui {tax} "
             f"with marginal tax rate = {marginal_tax_rate}%")
    assert round(tax) == test_tax[0], f"Error in tax calc for {test_income[0]}"
    return 0


if __name__ == "__main__":
    from shared_utils.my_utils.glogger import LoggerManager
    glogger = LoggerManager(filename='test.log')
    logger = glogger.get_logger()
    logger.debug(f"Start logging.")
    result = test_calc_year_tax(logger)
    if result == 0:
        print("Test ended successfully")

    # TEST ALSO WITH https://finka.co.il/%d7%9e%d7%97%d7%a9%d7%91%d7%95%d7%9f-%d7%a7%d7%99%d7%91%d7%95%d7%a2-%d7%96%d7%9b%d7%95%d7%99%d7%95%d7%aa/