import unittest
import argparse
from datetime import date
import unittest.mock
from insurance_termination import insurance_termination

class TestParseDate(unittest.TestCase):
  """
  Test the parse_date function.
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


class TestGetEarliestTermination(unittest.TestCase):
  """
  Test the get_earliest_standard_termination function.
  """

  def test_should_throw_exception_if_last_renewal_is_before_01_04_2014(self):
    self.assertRaises(insurance_termination.UnsupportedDateError, insurance_termination.get_earliest_standard_termination, date(1999, 1, 1), date(2000, 1, 1), date(2000, 1, 1))


  def test_should_wait_until_end_of_contract_for_contract_started_after_01_10_2024_within_first_year(self):
    result = insurance_termination.get_earliest_standard_termination(date(2024, 10, 1), date(2025, 4, 1), date(2025, 3, 1))
    self.assertEqual(result, date(2025, 10, 1))

  def test_should_require_2_months_notice_for_contract_started_after_01_10_2024_after_renewal_1(self):
    result = insurance_termination.get_earliest_standard_termination(date(2024, 10, 1), date(2025, 9, 20), date(2025, 9, 20))
    self.assertEqual(result, date(2025, 11, 20))

  def test_should_require_2_months_notice_for_contract_started_after_01_10_2024_after_renewal_2(self):
    result = insurance_termination.get_earliest_standard_termination(date(2024, 10, 1), date(2026, 6, 25), date(2026, 4, 25))
    self.assertEqual(result, date(2026, 6, 25))


  def test_should_wait_until_end_of_contract_for_old_contract_not_renewed_after_01_10_2024(self):
    result = insurance_termination.get_earliest_standard_termination(date(2022, 5, 18), date(2024, 10, 1), date(2024, 10, 1))
    self.assertEqual(result, date(2025, 5, 18))

  def test_should_require_3_months_notice_for_old_contract_not_renewed_after_01_10_2024(self):
    result = insurance_termination.get_earliest_standard_termination(date(2022, 5, 18), date(2025, 2, 20), date(2025, 2, 20))
    self.assertEqual(result, date(2025, 5, 20))

  def test_should_require_2_months_notice_for_old_contract_renewed_after_01_10_2024(self):
    result = insurance_termination.get_earliest_standard_termination(date(2022, 5, 18), date(2025, 5, 21), date(2025, 5, 21))
    self.assertEqual(result, date(2025, 7, 21))


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