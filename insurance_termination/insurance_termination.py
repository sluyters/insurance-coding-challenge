#!/usr/bin/python3

import argparse
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

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
    contract_start: A date object representing the starting date of the insurance contract, i.e., when the contract with the insurance broker first took effect.
    earliest_expected_termination: A date object representing the earliest termination date wanted by the policy holder (defaults to the same date as the reference_date argument if ignored or smaller than the reference_date).
    reference_date: A date object representing the earliest possible date at which notice can be given to the insurer for contract termination (defaults to today's date).

  Returns:
    date: A date object representing the earliest possible termination date of the insurance contract.

  Raises:
    DateError: If the latest contract renewal date falls outside of the supported range. 
  """

  # Set default values if arguments are not provided
  reference_date = reference_date or date.today()
  if not earliest_expected_termination or earliest_expected_termination < reference_date:
    earliest_expected_termination = reference_date

  # Get the date of the latest renewal before the earliest expected termination date
  contract_age = relativedelta(earliest_expected_termination, contract_start)
  latest_renewal = contract_start + relativedelta(years=contract_age.years)

  # Check which rules should be applied based on the latest renewal date
  if latest_renewal >= date(2024, 10, 1):
    return get_earliest_standard_termination_from_10_2024_law(contract_start, latest_renewal, earliest_expected_termination, reference_date,)
  elif latest_renewal >= date(2014, 4, 4):
    return get_earliest_standard_termination_from_04_2014_law(latest_renewal, earliest_expected_termination, reference_date)
  else:
    raise UnsupportedDateError(f'Latest contract renewal date ({latest_renewal}) falls outside of the supported range (2014/04/04 - now).')


# Helpers
class UnsupportedDateError(ValueError):
  """Raise when a date falls out of the scope of a function."""


def get_earliest_standard_termination_from_10_2024_law(
    contract_start: date, 
    latest_renewal: date, 
    earliest_expected_termination: date,
    reference_date: date
) -> date:
  """
    Provides the earliest possible termination date of a non-life insurance contract started or last renewed after October 1st, 2024. 

    Args:
      contract_start: A date object representing the starting date of the insurance contract, i.e., when the contract with the insurance broker first took effect.
      latest_renewal: A date object representing the latest renewal of the insurance contract.
      earliest_expected_termination: A date object representing the earliest termination date wanted by the policy holder/provider.
      reference_date: A date object representing the earliest possible date at which notice can be given to the insurer for contract termination.
      
    Returns:
      A date object representing the earliest possible termination date of the insurance contract.
  """

  earliest_notice_end = reference_date + relativedelta(months=2)
  if contract_start == latest_renewal:
    # Within the first year of the contract, terminate at the end of the contract with 2 months notice
    earliest_possible_termination = latest_renewal + relativedelta(years=1)
    return max(earliest_possible_termination, earliest_expected_termination, earliest_notice_end)
  else:
    # After renewal, terminate at any time with 2 months notice
    return max(earliest_expected_termination, earliest_notice_end)
  

def get_earliest_standard_termination_from_04_2014_law(
    latest_renewal: date, 
    earliest_expected_termination: date,
    reference_date: date
) -> date:
  """
    Provides the earliest possible termination date of a non-life insurance contract started or last renewed after April 4, 2014 and before September 30, 2024. 

    Args:
      latest_renewal: A date object representing the latest renewal of the insurance contract.
      earliest_expected_termination: A date object representing the earliest termination date wanted by the policy holder/provider.
      reference_date: A date object representing the earliest possible date at which notice can be given to the insurer for contract termination.

    Returns:
      A date object representing the earliest possible termination date of the insurance contract.
  """
  
  # Terminate at the end of the contract with 3 months notice
  earliest_notice_end = reference_date + relativedelta(months=3)
  earliest_possible_termination = latest_renewal + relativedelta(years=1)
  return max(earliest_possible_termination, earliest_expected_termination, earliest_notice_end)


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
  parser.add_argument('contractstart', help='The starting date of the insurance contract, i.e., when the contract with the insurance broker first took effect. Format: YYYY-MM-DD.', type=parse_date)
  parser.add_argument('-t', '--earliestexpectedtermination', help='The earliest termination date (YYYY-MM-DD) wanted by the policy holder. Format: YYYY-MM-DD.', type=parse_date, default=None)
  parser.add_argument('-r', '--referencedate', help='The first possible date at which notice can be given to the policy holder/provider for contract termination. Format: YYYY-MM-DD.', type=parse_date, default=None)
  # Parse arguments & run function
  args = parser.parse_args()
  est = get_earliest_standard_termination(args.contractstart, args.earliestexpectedtermination, args.referencedate)
  print(f'Earliest possible termination date: {est}.')
