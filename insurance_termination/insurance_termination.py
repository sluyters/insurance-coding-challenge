#!/usr/bin/python3

import argparse
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Error classes
class UnsupportedDateError(ValueError):
  """Raise when a date falls out of the scope of a function."""


class ContractDateError(ValueError):
  """Raise when a contract starting date is invalid."""


# Main function
def get_earliest_standard_termination(
    contract_start: date,
    earliest_expected_termination: date = None,
    reference_date: date = None,
) -> date:
  """Provides the earliest possible termination date of a non-life insurance contract by the policyholder.

  This function provides the earliest possible termination date of a non-life insurance contract based on the starting date of the contract, the earliest expected termination date of the contract, and a reference date (i.e., the earliest possible starting date of the notice period).
  This function applies only to non-life insurance contracts concluded by consumers that started or were renewed after April 4, 2014. It does not handle exceptions such as termination following a claim, a non-payment, or a rise in the premium.

  Args:
    contract_start: A date object representing the starting date of the insurance contract, i.e., when the contract with the insurer first took effect.
    earliest_expected_termination: A date object representing the earliest termination date wanted by the policy holder (defaults to the same date as the reference_date argument if ignored or smaller than the reference_date).
    reference_date: A date object representing the earliest possible date at which notice can be given to the insurer for contract termination (defaults to today's date).

  Returns:
    date: A date object representing the earliest possible termination date of the insurance contract.

  Raises:
    UnsupportedDateError: If earliest_expected_termination is before April 4, 2014. 
    ContractDateError: If the starting date of a contract does not preceed the reference date. 
  """
  # Set default values if arguments are not provided
  reference_date = reference_date or date.today()
  if not earliest_expected_termination or earliest_expected_termination < reference_date:
    earliest_expected_termination = reference_date

  # Check validity of the parameters
  if reference_date < contract_start:
    raise ContractDateError(f'The starting date of a contract (contract_start = {contract_start}) should preceed the reference date (reference_date = {reference_date}).')
  if earliest_expected_termination < date(2014, 4, 4):
    raise UnsupportedDateError(f'The "earliest_expected_termination" parameter ({earliest_expected_termination}) falls outside of the supported range (2014/04/04 - now).')
  
  # Compute earliest contract termination date
  contract_age_at_expected_termination = relativedelta(earliest_expected_termination, contract_start)
  if contract_start >= date(2024, 10, 1):
    # Contract started after new law from October 1st, 2024
    earliest_notice_end = reference_date + relativedelta(months=2)
    first_contract_renewal = contract_start + relativedelta(years=1)
    if ceil_years(contract_age_at_expected_termination) <= 1 and earliest_notice_end < first_contract_renewal:
      # Case 1 - Before the first anniversary of a contract, terminate at the end of the contract with 2 months notice
      return get_earliest_termination_case_1(contract_start)
    else:
      # Case 2 - After first automatic renewal, terminate at any time with 2 months notice
      return get_earliest_termination_case_2(earliest_expected_termination, reference_date, first_contract_renewal)
  else:
    # Contract started before new law from October 1st, 2024
    earliest_notice_end = reference_date + relativedelta(months=3)
    next_contract_renewal = contract_start + relativedelta(years=ceil_years(contract_age_at_expected_termination))
    previous_contract_renewal = next_contract_renewal - relativedelta(years=1)
    if previous_contract_renewal >= date(2024, 10, 1):
      # Case 2
      return get_earliest_termination_case_2(earliest_expected_termination, reference_date, previous_contract_renewal)
    elif next_contract_renewal >= date(2024, 10, 1) and earliest_notice_end > next_contract_renewal:
      # Case 2
      return get_earliest_termination_case_2(earliest_expected_termination, reference_date, next_contract_renewal)
    else:
      # Case 3 - Terminate at the end of the contract with 3 months notice
      return get_earliest_termination_case_3(earliest_notice_end, next_contract_renewal)
 

# Helpers
def get_earliest_termination_case_1(
    contract_start: date
) -> date:
  """
  Provides the earliest termination date of a contract signed after October 1st, 2024, before its first automatic renewal.

  Args:
    contract_start: A date object representing the starting date of the insurance contract, i.e., when the contract with the insurer first took effect.

  Returns:
    date: A date object representing the earliest possible termination date of the insurance contract.
  """
  return contract_start + relativedelta(years=1)


def get_earliest_termination_case_2(
    earliest_expected_termination: date,
    reference_date: date,
    first_contract_renewal: date
) -> date:
  """
  Provides the earliest termination date of a contract signed or renewed after October 1st, 2024, after its first automatic renewal.

  Args:
    earliest_expected_termination: A date object representing the earliest termination date wanted by the policy holder.
    reference_date: A date object representing the earliest possible date at which notice can be given to the insurer for contract termination.
    first_contract_renewal: A date object representing the date of the first automatic renewal of the contract after October 1st, 2024.

  Returns:
    date: A date object representing the earliest possible termination date of the insurance contract.
  """
  earliest_notice_end = max(reference_date, first_contract_renewal) + relativedelta(months=2)
  return max(earliest_expected_termination, earliest_notice_end)


def get_earliest_termination_case_3(
    earliest_notice_end: date,
    next_contract_renewal: date
) -> date:
  """
  Provides the earliest termination date of a contract last renewed before October 1st, 2024.

  Args:
    earliest_notice_end: The earliest date at which the notice given to the insurer ends.
    next_contract_renewal: The date of the next renewal of the insurance contract.
  
  Returns:
    date: A date object representing the earliest possible termination date of the insurance contract.
  """
  if earliest_notice_end > next_contract_renewal:
    return next_contract_renewal + relativedelta(years=1)
  else:
    return next_contract_renewal


def ceil_years(delta: relativedelta) -> int:
  """Rounds up the number of years in a relativedelta object.

  Args:
    delta: A relativedelta object. 

  Returns: 
    int: The number of years in the delta parameter rounded up.
  """
  if delta.days > 0 or delta.months > 0:
    return delta.years + 1
  else:
    return delta.years
  

def parse_date(string_date: str) -> date:
  """
  Extracts a date object from a string representation of a date.
  
  Args:
    string_date: A string representation of a date (format: YYYY-MM-DD).

  Returns:
    A date object corresponding to the date in the string_date argument.

  Raises:
    argparse.ArgumentTypeError: If string_date could not be parsed into a valid date object. 
  """
  try:
    return datetime.strptime(string_date, '%Y-%m-%d').date()
  except ValueError:
    raise argparse.ArgumentTypeError(f'Invalid date: {string_date}')


# Execute only when the module is run as a script
if __name__ == '__main__':
  # Define program arguments
  parser = argparse.ArgumentParser('insurance_termination', description='This program provides the earliest possible termination date of a non-life insurance contract based on the starting date of the contract, the earliest possible starting date of the notice period (today if not specified), and the earliest expected termination date of the contract. It applies only to non-life insurance contracts concluded by consumers that started or were renewed after April 4, 2014.')
  parser.add_argument('contractstart', help='The starting date of the insurance contract, i.e., when the contract with the insurer first took effect. Format: YYYY-MM-DD.', type=parse_date)
  parser.add_argument('-t', '--earliestexpectedtermination', help='The earliest termination date (YYYY-MM-DD) wanted by the policy holder. Format: YYYY-MM-DD.', type=parse_date, default=None)
  parser.add_argument('-r', '--referencedate', help='The first possible date at which notice can be given to the policy holder/provider for contract termination. Format: YYYY-MM-DD.', type=parse_date, default=None)
  # Parse arguments & run function
  args = parser.parse_args()
  est = get_earliest_standard_termination(args.contractstart, args.earliestexpectedtermination, args.referencedate)
  print(f'Earliest possible termination date: {est}.')
