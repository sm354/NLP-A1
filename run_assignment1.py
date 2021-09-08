'''
COL772 A1 - Shubham Mittal 2018EE10957

Rule-based system
-----------------

    How to make such a system?
    --------------------------
        find out the categories that need conversion
        analyse the pattern by training the human neural network with some examples from given dataset
        write the rule corresponding to the pattern

    Rules
    -----
    silent tokens (sil)

    converting honorifics - Mr Mrs Dr ? probably NO
'''

import argparse
import json
import re
import subprocess # remove this line before final submission

# parse arguments
def add_args(parser):
    parser.add_argument('--input_path', default='assignment_1_data/input.json', type=str, help='Path to input file')
    parser.add_argument('--solution_path', default='assignment_1_data/prediction.json', type=str, help='Path to solution file')
    parser.add_argument('--debug', action='store_true', help='print the wrong predictions along with input and gold output')
    return parser

# rule-based system for converting each input-token (in a sentence/input tokens)
def findOT(inp_tok, rules):
    # if any of the rules doesn't apply then apply <self> token
    out_tok = '<self>'

    for rule in rules:
        out_tok = rule(inp_tok)
        
        if out_tok != None:
            break
    
    return '<self>' if out_tok == None else out_tok

# create solution for provided input tokens
def solution(input_tokens):
    output_tokens = []

    rules = [sil, abbreviation, dates2words, time2words, num2words, units2words, currency2words]

    for input_token in input_tokens:
        output_token = findOT(input_token, rules)
        output_tokens.append(output_token)

    assert len(output_tokens) == len(input_tokens)
    # return ['<self>']*len(input_tokens) #todo: write your own solution
    return output_tokens

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

def sil(string):
    regex = r"^\W$"
    return None if re.match(regex, string) == None else "sil"

def abbreviation(string):
    regex = r"([A-Z](\.)?(\s)*)+" # this regex includes the roman numerals as well => precision would be high (FP would be high)
    match = re.fullmatch(regex, string)

    if match == None:
        return None
    
    # split the string about [^A-Z] into lower case characters
    split_str = re.split(r'[^A-Z]+', match.group())
    split_str = ''.join(split_str).strip().lower()
    # now we have got the letters, just insert spaces in between them
    out = ""
    for ch in split_str:
        out += ch
        out += " "
    return out.strip()

def dates2words(string):
    '''
    possible formats
    ----------------
        2011-01-25
        March 2011 march twenty eleven
        14 June 2014 the fourteenth of june twenty fourteen
        2006 two thousand six
        January 14, 2008 january fourteenth two thousand eight
        1984 nineteen eighty four
        1878 eighteen seventy eight
        1201 twelve o one
        1200 twelve hundred
        1806 eighteen o six
        2000 two thousand
    '''
    # first find year
    regex_year = r"[1-2]\d{3}"
    match = re.search(regex_year, string)
    
    if match == None:
        return None
    out = ""
    
    year = match.group()
    # 1921 -> nineteen twenty one
    
    return out

def time2words(string):

    pass

def num2words(string):
    '''
    possible formats
    ----------------
        num
            123141512, 0, 199, -123
        comma_num
            12,000 twelve thousand
        dec_perc_num
            123.123
            90.0 ninety point zero
            0.63% zero point six three percent
            99.05% ninety nine point o five percent
            0.32% zero point three two percent
            IMPORTANT ------- 1,565.0 one thousand five hundred sixty five point zero
            25.520 twenty five point five two o
            13.0088 thirteen point o o eight eight
        frac_num    
            7/283 : seven two hundred eighty thirds
            1 1/2 one and a half
        hyp_num
            978-0-304-35252-4 nine seven eight sil o sil three o four sil three five two five two sil four
            1-881089-97-5 one sil eight eight one o eight nine sil nine seven sil five
            0-8387-1972-4 o sil eight three eight seven sil one nine seven two sil four

        EDGE-CASE:
            106 (2003) 203-214 one o six sil two o o three sil two o three sil two one four
            0 7506 0625 8 o sil seven five o six sil o six two five sil eight
    '''
    # regex_num = r"(-?)\d+"
    # match = re.fullmatch(regex_num, string)
    # if match != None:
    #     return _number_to_word(match.group())
    
    regex_comma_num = r"(-?)((,?)\d{1,3})+" # this includes some false weird examples also like '90,0', ',123,1,1', etc BUT it also includes all the numbers
    match = re.fullmatch(regex_comma_num, string)
    if match != None:
        return _number_to_word(''.join(match.group().split(',')))

    # regex_dec_perc = r"(-?)(\d*)(\.)(\d)" # this includes some false weird examples also like '90,0', ',123,1,1', etc
    # match = re.fullmatch(regex_dec_perc, string)
    
    regex_hyp_num = r"(\d+-)+(\d+)" # this includes dates also -- NEED TO FIX THIS IMPORTANT!
    match = re.fullmatch(regex_hyp_num, string)
    if match != None:
        return _hyphen_num_to_word(match.group())

    return None

def _number_to_word(number):
    '''
    This will convert the given number (in any range) string to word string
    Numbers in [0,20] are instantly converted using _num2word
    Others are passed through an algorithm that splits the number in groups of 3

    '''
    negative_num = False
    if number[0] == '-':
        negative_num = True
        number = number[1:]
        
    if 0 <= int(number) <= 20:
        # this takes care of case when number == 0 (empty string is not returned)
        # -0 is returned as 0
        return _num2word[int(number)]
    
    final_word = []
    
    # now split the number in groups of 3 from last
    grps_of_3digits = []
    i = len(number)-3
    while i>=0:
        grps_of_3digits.append(number[i:i+3])
        i-=3
    if i+3 != 0: # avoid empty string insertion
        grps_of_3digits.append(number[0:i+3])
    
    # now convert each group one by one
    for i, num_3dig in enumerate(grps_of_3digits):
        num_3dig_wrd = _3dig_num2wrd(num_3dig)
        if num_3dig_wrd != '': # handles 1,000,000 -> the last two groups should not add _placeValue
            num_3dig_wrd += (" " + _placeValue[i])
        num_3dig_wrd = num_3dig_wrd.strip()
        
        if num_3dig_wrd != '':
            final_word.insert(0, num_3dig_wrd)
    
    if negative_num:
        final_word.insert(0, "minus")
    
    final_word = ' '.join(final_word)
    return final_word

def _3dig_num2wrd(num):
    '''
    this accepts num in [0, 999]
    empty string returned if int(num) is 0 
    
    there are three cases
        0 <= num <= 20 or num == 30, 40, ..., 90 --> these are hard coded
        20 < num < 100 and num != 30, 40, ..., 90
        100 <= num < 1000 --> this also gets split into cases
    '''
    num = int(num)
    final_word = None
    if num == 0:
        final_word = ""
    
    elif 0 < num <= 20 or (num%10 == 0 and num < 100): 
        final_word = _num2word[num]
    
    elif 20 < num < 100:
        tenths = 10 * (num // 10)
        ones = num % 10
        final_word = _num2word[tenths] + " " + _num2word[ones]
    
    else:
        hundredths = num//100
        final_word = _num2word[hundredths] + " hundred " + _3dig_num2wrd(str(num%100))
    return final_word.strip()

def _hyphen_num_to_word(hyph_num):
    final_word = []
    for ch in hyph_num:
        if ch == '-':
            final_word.append('sil') 
        elif ch == '0':
            final_word.append('o')
        else:
            final_word.append(_num2word[int(ch)])
    return ' '.join(final_word)

def units2words(string):

    pass

def currency2words(string):

    pass

def _make_vocab():
    # make dictionaries for hard-coded mappings like '1' -> 'one'

    global _num2word
    _num2word = {}
    _words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    _words+= ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
    for i in range(20):
        _num2word[i] = _words[i]
    _words = ['twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    for i in range(20, 100, 10):
        _num2word[i] = _words[i//10 - 2]
    
    global _placeValue
    _placeValue = {}
    _list = ['', 'thousand', 'million', 'billion', 'trillion', 'quadrillion']
    for i in range(len(_list)):
        _placeValue[i] = _list[i]
        
    # print(_num2word)
    # print(_placeValue)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='COL 772 Assignment 1 | 2018EE10957')
    parser = add_args(parser)
    args = parser.parse_args()
    
    _make_vocab()

    solution_dump(args)

    # remove the following lines before final submission
    python_cmd = "python run_checker.py --ground_truth_path assignment_1_data/output.json \
        --solution_path " + args.solution_path 
    if args.debug:
        python_cmd += " --debug"
    
    subprocess.call(python_cmd, shell=True) 


'''
References
----------

'''