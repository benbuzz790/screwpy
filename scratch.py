from units_config import ureg
import re
# Test the current pattern vs what we want
CURRENT_PATTERN = r'^(\d+/\d+|\d+\.?\d*)[-](\d+)(?:\s+(UNC|UNF))?$'
PROPOSED_PATTERN = r'^(\d+/\d+|\d+\.?\d*)[-](\d+)\s+(UNC|UNF)$'

test_cases = [
    '1/4-20 UNC',   # Should pass
    '3/8-24 UNF',   # Should pass
    '1/4-20',       # Should fail - no series
    '1/4 UNC',      # Should fail - no TPI
    'abc-def UNC',  # Should fail - invalid format
    '1-13 UNC',     # Should fail - non-standard size
]

print('Testing patterns:')
print('\nCurrent pattern results:')
for case in test_cases:
    match = re.match(CURRENT_PATTERN, case)
    print(f'{case}: {"PASS" if match else "FAIL"} {match.groups() if match else ""}')

print('\nProposed pattern results:')
for case in test_cases:
    match = re.match(PROPOSED_PATTERN, case)
    print(f'{case}: {"PASS" if match else "FAIL"} {match.groups() if match else ""}')

# Test thread specs validation
THREAD_SPECS = {
    'UNC': {
        '1/4': 20,
        '3/8': 16,
        '1/2': 13,
        '3/4': 10
    },
    'UNF': {
        '1/4': 28,
        '3/8': 24,
        '1/2': 20,
        '3/4': 16
    }
}

def validate_spec(spec):
    match = re.match(PROPOSED_PATTERN, spec)
    if not match:
        return False, 'Invalid format'
    
    diameter, tpi, series = match.groups()
    if diameter not in THREAD_SPECS[series]:
        return False, f'Non-standard size for {series}'
    if int(tpi) != THREAD_SPECS[series][diameter]:
        return False, f'Wrong TPI for {series} {diameter}'
    return True, 'Valid'

print('\nTesting validation:')
test_cases.extend(['1/4-28 UNC', '3/8-20 UNF'])  # Add more invalid cases
for case in test_cases:
    valid, reason = validate_spec(case)
    print(f'{case}: {"PASS" if valid else "FAIL"} - {reason}')
