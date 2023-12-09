from nric_utils import nric_finder, nric_validator

nric = "F7455387R"

print(nric_validator(nric))

birth_date, last_four_char = "12121999", "123A"

print(nric_finder(birth_date, last_four_char))
