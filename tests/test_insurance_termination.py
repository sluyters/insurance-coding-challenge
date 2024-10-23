import unittest
import argparse
from datetime import date
from dateutil.relativedelta import relativedelta
import unittest.mock
from insurance_termination import insurance_termination


class TestParseDate(unittest.TestCase):
  """
  Test the parse_date function of the insurance_termination module.
  """

  def test_correct_date(self):
    result = insurance_termination.parse_date('1999-12-29')
    self.assertEqual(result, date(1999, 12, 29))

  def test_should_throw_exception_if_order_is_incorrect(self):
    self.assertRaises(argparse.ArgumentTypeError, insurance_termination.parse_date, '29-12-1999')

  def test_should_throw_exception_if_order_is_incorrect_2(self):
    self.assertRaises(argparse.ArgumentTypeError, insurance_termination.parse_date, '1999-29-12')

  def test_should_throw_exception_if_day_is_invalid(self):
    self.assertRaises(argparse.ArgumentTypeError, insurance_termination.parse_date, '1999-12-32')

  def test_should_throw_exception_if_day_is_invalid_2(self):
    self.assertRaises(argparse.ArgumentTypeError, insurance_termination.parse_date, '2001-02-29')

  def test_should_throw_exception_if_month_is_invalid(self):
    self.assertRaises(argparse.ArgumentTypeError, insurance_termination.parse_date, '1999-13-29')

  def test_should_throw_exception_if_year_is_invalid(self):
    self.assertRaises(argparse.ArgumentTypeError, insurance_termination.parse_date, '99-12-29')


class TestCeilYears(unittest.TestCase):
  """
  Test the ceil_years function of the insurance_termination module.
  """

  def test_round_year(self):
    result = insurance_termination.ceil_years(relativedelta(years=1))
    self.assertEqual(result, 1)

  def test_year_with_month(self):
    result = insurance_termination.ceil_years(relativedelta(years=1, months=6))
    self.assertEqual(result, 2)

  def test_year_with_day(self):
    result = insurance_termination.ceil_years(relativedelta(years=1, days=20))
    self.assertEqual(result, 2)

  def test_year_with_day_and_month(self):
    result = insurance_termination.ceil_years(relativedelta(years=1, months=4, days=6))
    self.assertEqual(result, 2)


class TestEarliestTerminationCase1(unittest.TestCase):
  """
  Test the get_earliest_termination_case_1 function of the insurance_termination module.
  """

  def test_should_give_date_of_first_renewal(self):
    result = insurance_termination.get_earliest_termination_case_1(date(2025, 10, 1))
    self.assertEqual(result, date(2026, 10, 1))


class TestEarliestTerminationCase2(unittest.TestCase):
  """
  Test the get_earliest_termination_case_2 function of the insurance_termination module.
  """

  def test_should_give_earliest_expected_termination_if_notice_ends_before(self):
    result = insurance_termination.get_earliest_termination_case_2(date(2026, 10, 1), date(2026, 6, 1), date(2026, 7, 1))
    self.assertEqual(result, date(2026, 10, 1))

  def test_should_wait_for_2_months_notice_from_first_contract_renewal(self):
    result = insurance_termination.get_earliest_termination_case_2(date(2026, 10, 1), date(2026, 6, 1), date(2026, 9, 1))
    self.assertEqual(result, date(2026, 11, 1))

  def test_should_wait_for_2_months_notice_from_reference_date(self):
    result = insurance_termination.get_earliest_termination_case_2(date(2026, 10, 1), date(2026, 9, 1), date(2026, 6, 1))
    self.assertEqual(result, date(2026, 11, 1))


class TestEarliestTerminationCase3(unittest.TestCase):
  """
  Test the get_earliest_termination_case_3 function of the insurance_termination module.
  """

  def test_should_give_next_renewal_if_notice_ends_before(self):
    result = insurance_termination.get_earliest_termination_case_3(date(2020, 10, 1), date(2020, 11, 1))
    self.assertEqual(result, date(2020, 11, 1))

  def test_should_skip_next_renewal_if_notice_ends_after(self):
    result = insurance_termination.get_earliest_termination_case_3(date(2020, 12, 1), date(2020, 11, 1))
    self.assertEqual(result, date(2021, 11, 1))


class TestGetEarliestTermination(unittest.TestCase):
  """
  Test the get_earliest_standard_termination function of the insurance_termination module.
  """

  def test_should_throw_exception_if_last_renewal_is_before_01_04_2014(self):
    self.assertRaises(insurance_termination.UnsupportedDateError, insurance_termination.get_earliest_standard_termination, date(1999, 1, 1), date(2000, 1, 1), date(2000, 1, 1))

  def test_should_throw_exception_if_contract_start_more_recent_than_reference_date(self):
    self.assertRaises(insurance_termination.ContractDateError, insurance_termination.get_earliest_standard_termination, date(2020, 1, 1), date(2020, 1, 1), date(2018, 1, 1))


  def test_should_wait_until_end_of_contract_for_contracts_started_after_01_10_2024_in_their_first_year(self):
    result = insurance_termination.get_earliest_standard_termination(date(2024, 10, 1), date(2025, 4, 1), date(2025, 3, 1))
    self.assertEqual(result, date(2025, 10, 1))

  def test_should_require_2_months_notice_for_contracts_started_after_01_10_2024_in_their_first_year(self):
    result = insurance_termination.get_earliest_standard_termination(date(2024, 10, 1), date(2025, 9, 1), date(2025, 9, 1))
    self.assertEqual(result, date(2025, 12, 1))

  def test_should_require_2_months_notice_for_contracts_started_after_01_10_2024_older_than_a_year(self):
    result = insurance_termination.get_earliest_standard_termination(date(2024, 10, 1), date(2026, 9, 1), date(2026, 9, 1))
    self.assertEqual(result, date(2026, 11, 1))


  def test_should_wait_until_end_of_contract_for_contracts_started_before_01_10_2024_not_renewed_after_01_10_2024(self):
    result = insurance_termination.get_earliest_standard_termination(date(2018, 5, 18), date(2024, 10, 1), date(2024, 10, 1))
    self.assertEqual(result, date(2025, 5, 18))

  def test_should_require_3_months_notice_for_contracts_started_before_01_10_2024_not_renewed_after_01_10_2024(self):
    result = insurance_termination.get_earliest_standard_termination(date(2018, 5, 18), date(2025, 2, 20), date(2025, 2, 20))
    self.assertEqual(result, date(2025, 7, 18))

  def test_should_require_2_months_notice_for_contracts_started_before_01_10_2024_renewed_after_01_10_2024(self):
    result = insurance_termination.get_earliest_standard_termination(date(2018, 5, 18), date(2025, 5, 21), date(2025, 5, 21))
    self.assertEqual(result, date(2025, 7, 21))

  
  def test_should_wait_until_end_of_contract_for_contracts_started_before_01_10_2024_with_3_months_notice_1(self):
    result = insurance_termination.get_earliest_standard_termination(date(2016, 1, 1), date(2017, 1, 1), date(2016, 8, 31))
    self.assertEqual(result, date(2017, 1, 1))

  def test_should_wait_until_end_of_contract_for_contracts_started_before_01_10_2024_with_3_months_notice_2(self):
    result = insurance_termination.get_earliest_standard_termination(date(2016, 1, 1), date(2016, 8, 1), date(2016, 8, 31))
    self.assertEqual(result, date(2017, 1, 1))

  def test_should_wait_until_next_renewal_for_contracts_started_before_01_10_2024_with_late_notice(self):
    result = insurance_termination.get_earliest_standard_termination(date(2016, 1, 1), date(2016, 12, 31), date(2016, 12, 31))
    self.assertEqual(result, date(2018, 1, 1))

  def test_should_wait_until_next_renewal_after_earliest_expected_termination_for_contracts_started_before_01_10_2024_1(self):
    result = insurance_termination.get_earliest_standard_termination(date(2016, 1, 1), date(2017, 1, 2), date(2016, 8, 31))
    self.assertEqual(result, date(2018, 1, 1))

  def test_should_wait_until_next_renewal_after_earliest_expected_termination_for_contracts_started_before_01_10_2024_2(self):
    result = insurance_termination.get_earliest_standard_termination(date(2016, 1, 1), date(2022, 1, 2), date(2016, 8, 31))
    self.assertEqual(result, date(2023, 1, 1))


  def test_should_handle_contracts_created_on_a_leap_day_before_01_10_2024(self):
    result = insurance_termination.get_earliest_standard_termination(date(2016, 2, 29), date(2017, 2, 10), date(2016, 10, 15))
    self.assertEqual(result, date(2017, 2, 28))

  def test_should_handle_contracts_created_after_a_leap_day_before_01_10_2024(self):
    result = insurance_termination.get_earliest_standard_termination(date(2016, 3, 1), date(2017, 2, 10), date(2016, 10, 15))
    self.assertEqual(result, date(2017, 3, 1))

  def test_should_handle_contracts_created_on_a_leap_day_after_01_10_2024(self):
    result = insurance_termination.get_earliest_standard_termination(date(2028, 2, 29), date(2029, 2, 10), date(2028, 10, 15))
    self.assertEqual(result, date(2029, 2, 28))

  def test_should_handle_contracts_created_after_a_leap_day_after_01_10_2024(self):
    result = insurance_termination.get_earliest_standard_termination(date(2028, 3, 1), date(2029, 2, 10), date(2028, 10, 15))
    self.assertEqual(result, date(2029, 3, 1))


  def test_should_use_reference_date_as_default_earliest_expected_termination(self):
    result = insurance_termination.get_earliest_standard_termination(date(2024, 10, 10), reference_date=date(2025, 11, 1))
    self.assertEqual(result, date(2026, 1, 1))

  @unittest.mock.patch('insurance_termination.insurance_termination.date')
  def test_should_use_today_as_default_reference_date(self, mock_date):
    # Replace today() by a custom date for testing
    mock_date.today.return_value = date(2025, 11, 1)
    mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
    result = insurance_termination.get_earliest_standard_termination(date(2024, 10, 10), earliest_expected_termination=date(2025, 12, 1))
    self.assertEqual(result, date(2026, 1, 1))

  @unittest.mock.patch('insurance_termination.insurance_termination.date')
  def test_should_use_today_as_default_reference_date_and_earliest_expected_termination(self, mock_date):
    # Replace today() by a custom date for testing
    mock_date.today.return_value = date(2025, 11, 1)
    mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
    result = insurance_termination.get_earliest_standard_termination(date(2024, 10, 10))
    self.assertEqual(result, date(2026, 1, 1))

  @unittest.mock.patch('insurance_termination.insurance_termination.date')
  def test_should_not_terminate_contract_before_earliest_expected_termination(self, mock_date):
    # Replace today() by a custom date for testing
    mock_date.today.return_value = date(2025, 11, 1)
    mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
    result = insurance_termination.get_earliest_standard_termination(date(2024, 10, 10), earliest_expected_termination=date(2026, 2, 1))
    self.assertEqual(result, date(2026, 2, 1))

  def test_should_ignore_earliest_expected_termination__date_if_earlier_than_reference_date(self):
    result = insurance_termination.get_earliest_standard_termination(date(2023, 9, 5), date(2024, 11, 5), date(2025, 11, 5))
    self.assertEqual(result, date(2026, 1, 5))


if __name__ == '__main__':
  unittest.main()