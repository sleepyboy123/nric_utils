from calendar import monthrange
import requests



def nric_validator(nric):
    valid_nric = False
    total_sum = 0

    if len(nric) != 9:
        print("NRIC should have 9 characters")
        return valid_nric

    # Parse the data into usable format
    starting_letter, digits, checksum = nric[0], nric[1:-1], nric[-1]
    digits_array = [int(d) for d in digits]

    if starting_letter.upper() not in {"S", "T", "F", "G"}:
        print("Invalid Starting Character, should be \{S, T, F, G\}")
        return valid_nric
    
    # Calculate the total sum based on each digits weightage
    weight = "2765432"
    for i in range(len(digits_array)):
        total_sum += digits_array[i] * int(weight[i])

    if starting_letter.upper() in {"T", "G"}:
        total_sum += 4
    
    remainder = total_sum % 11

    # Use the relevant predefined checksum based on starting letter
    if starting_letter.upper() in {"S", "T"}:
        predefined_checksum = "JZIHGFEDCBA"
    elif starting_letter.upper() in {"F", "G"}:
        predefined_checksum = "XWUTRQPNMLK"

    # Use the remainder to check the predefined checksum and validate it with provided checksum
    if predefined_checksum[remainder] == checksum:
        valid_nric = True

    return valid_nric

def nric_finder(birth_date, last_four_char):
    # Parse relevant information from birthdate DDMMYYYY
    birth_day, birth_month, birth_year = birth_date[:2], birth_date[2:4], birth_date[-4:]
    first_letter = "S" if int(birth_year[:2]) == 19 else "T"

    # Build the NRIC format with current known information
    # first_letter + birth_year[-2:] + ? + ? + last_four_char

    # Fetch the birth data for birth year from singstat
    url = "http://tablebuilder.singstat.gov.sg/api/table/tabledata/M810051"
    headers = {
        'Referer': 'https://tablebuilder.singstat.gov.sg/table/TS/M810051',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    json_response = response.json()["Data"]["row"][0]["columns"]
    birth_year_data = []
    for obj in json_response:
        if birth_year in obj["key"]:
            birth_year_data.append(obj["value"])

    # Bruteforce all 99 possible NRIC
    possible_nric_array = []
    for guess in range(0, 100):
        double_digit_guess = f"{guess:02}"
        possible_nric = first_letter + birth_year[-2:] + double_digit_guess + last_four_char
        if nric_validator(possible_nric):
            possible_nric_array.append(possible_nric)

    # Calculate estimated births before you
    births_before_you = 0
    for i in range(1, int(birth_month)):
        births_before_you += int(birth_year_data[i-1])
    number_of_days_in_birth_month = monthrange(int(birth_year), int(birth_month))[1]
    births_before_you += (int(birth_year_data[int(birth_month) - 1]) / number_of_days_in_birth_month) * int(birth_day)
    
    # Calculate which possible NRIC has the minimum absolute difference with the estimated births before you.
    # If a possible NRIC is S96 12345 F and you are the 12323th person born, the absolute difference would be 22.
    # Since the absolute difference is so low, it is likely that we have guessed the NRIC correctly.
    array_of_differences = list(map(lambda test_nric: abs(births_before_you - int(test_nric[3:-1])), possible_nric_array))
    correct_index = array_of_differences.index(min(array_of_differences))

    return possible_nric_array[correct_index]

