'''
COL772 A1 - Shubham Mittal 2018EE10957

Rule-based system
-----------------
    

    abbreviations
        All abbreviations are separated as they are spoken. Example, “U.S.” or “US” is converted to “u s”

    dates
        All dates are converted into words. Example, “29 March 2012” will be converted to “the
        twenty ninth of march twenty twelve”. “2011-01-25” will be converted to “the twenty fifth of
        january twenty eleven”

    times
        All times are converted into words. Example, “04:40 PM” is converted to “four forty p m”.
        “21:30:12” is converted to “twenty one hours thirty minutes and twelve seconds”

    numeric quanities
        All numeric quantities are converted to words using Western numbering system. Example,
        “10345” is converted to “ten thousand three hundred forty five”. “24349943” is converted to
        “twenty four million three hundred forty nine thousand nine hundred forty three”. “184.33” is
        converted to “one hundred eighty four point three three”. “-20” is converted to “minus twenty”.

    units
        All units are spelled out as spoken. “53.77 mm” is converted to “fifty three point seven
        seven millimeters”, “3 mA” is converted to “three milliamperes”, and “14 sq m” is converted to
        “fourteen square meters”.

    currency
        Currency is also spelled out. “$15.24” is converted to “fifteen dollars and twenty four cents”.
        “£11” is converted to “eleven pounds”.  

Appendix
--------
    converting honorifics - Mr Mrs Dr ? probably no
'''


import argparse
import json
import subprocess # remove this line before final submission

# parse arguments
def add_args(parser):
    parser.add_argument('--input_path', default='assignment_1_data/input.json', type=str, help='Path to input file')
    parser.add_argument('--solution_path', default='assignment_1_data/prediction.json', type=str, help='Path to solution file')
    return parser

# rule-based system for converting each sentence/input-tokens
def solution(input_tokens):











    return ['<self>']*len(input_tokens) #todo: write your own solution

# make solution using input sentences
def solution_dump(args):
    # load input data
    with open(args.input_path, 'r') as input_file:
        input_data = json.load(input_file)
        input_file.close()

    # pass each input sentence through rule-based system
    solution_data = []
    for input_sentence in input_data:
        solution_sid = input_sentence['sid']
        solution_tokens = solution(input_sentence['input_tokens'])
        solution_data.append({'sid':solution_sid,
                            'output_tokens':solution_tokens})

    # write the predicted sentences in args.solution
    with open(args.solution_path,'w') as solution_file:
        json.dump(solution_data, solution_file, indent=2, ensure_ascii=False)
        solution_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='COL 772 Assignment 1 | 2018EE10957')
    parser = add_args(parser)
    args = parser.parse_args()

    solution_dump(args)

    subprocess.call("python run_checker.py --ground_truth_path assignment_1_data/output.json \
        --solution_path " + args.solution_path, shell=True) # remove this line before final submission





