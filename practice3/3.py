def solve():
    to_digit = {
        "ZER": "0",
        "ONE": "1",
        "TWO": "2",
        "THR": "3",
        "FOU": "4",
        "FIV": "5",
        "SIX": "6",
        "SEV": "7",
        "EIG": "8",
        "NIN": "9"
    }
    to_triplet = {v: k for k, v in to_digit.items()}

    s = input().strip()

    for op in ['+', '-', '*']:
        if op in s:
            parts = s.split(op)
            operator = op
            break

    def str_to_num(triplets):
        res = ""
        for i in range(0, len(triplets), 3):
            res += to_digit[triplets[i:i+3]]
        return int(res)

    num1 = str_to_num(parts[0]) 
    num2 = str_to_num(parts[1])

    if operator == '+': result = num1 + num2
    elif operator == '-': result = num1 - num2
    else: result = num1 * num2 

    res_str = st(result)
    prefix = ""
    if res_str.startswith('-'):
        prefix = "MIN"
        res_str = res_str[1:]

    final_output = "".join(to_triplet[d] for d in res_str)
    print(final_output)

solve()