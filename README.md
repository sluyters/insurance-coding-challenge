# Coding challenge
## Challenge description
1. Investigate the new rules for terminating insurance contracts (excl. life insurance) in Belgium.
2. Create a program that takes the **starting date of the insurance contract** (contract_start) and the **earliest expected termination date** (earliest_expected_termination) as input, and returns the **earliest possible termination date of the current contract**.

## Source material
- [New rules in effect since October 1st, 2024](https://economie.fgov.be/fr/themes/services-financiers/assurances/contrat-dassurance/resiliation-dun-contrat), valid for contracts started/renewed after October 1st 2024.
  - 2 scenarios:
    - Termination within the first year of the contract: at the end of the contract, 2 months notice required.
    - Termination after the contract has been implicitly renewed: anytime, 2 months notice required.
- [Previous rules (between April 4, 2014 and September 30, 2024)](https://www.test-achats.be/argent/assurance/dossier/resilier-une-assurance), valid for contracts started/renewed before October 1st 2024.
  - At the end of the contract, 3 months notice required .

## Assumptions
- Exceptional situations, such as terminating a contract following a claim or after a rise in the premium, are handled by a different function.
- The entity terminating the contract is the insurance policy holder, NOT the insurance provider, which has to follow different rules.
- Contracts started before April 4, 2014 are also renewed annually. In addition, once they are renewed after April 4, 2014, they fall under the same rules as contracts started after April 4, 2014.


## Instructions
### Prerequisites
Install Python 3.12.x

### Running the program
In the root directory, run 
```
python .\insurance_termination\insurance_termination.py [-h] CONTRACT_START_DATE [-t EARLIEST_EXPECTED_TERMINATION] [-r REFERENCE_DATE]
```

For instance, 
```
python insurance_termination/insurance_termination.py 2023-09-05 -t 2025-12-05 -r 2025-11-05
``` 
outputs 
```
Earliest possible termination date: 2026-01-05.
```
Because the contract was last renewed on September 5, 2025, so after the new rules from October 1st 2024, it can be terminated anytime following 2 months notice. 

The reference date is November 5, 2025, meaning that the notice period can end on January 5, 2026, if it starts immediately. 

As such, the earliest possible termination date is January 5, 2026, which is compatible with the earliest expected termination date provided by the policy holder (December 5, 2025).

### Running the tests
In the root directory, run 
```
python -m unittest
```
