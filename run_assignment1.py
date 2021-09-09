'''
COL772 A1 - Shubham Mittal 2018EE10957

Rule-based system
-----------------

    How to make such a system?
    --------------------------
        find out the categories that need conversion
        analyse the pattern by training the human neural network with some examples from given dataset
        write the rule corresponding to the pattern

    rules = [sil, abbreviation, dates2words, time2words, num2words, units2words, currency2words]
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

# rule-based system for converting each input-token (in a sentence/input tokens)
def findOT(inp_tok, rules):
    # if any of the rules doesn't apply then apply <self> token
    out_tok = '<self>'

    for rule in rules:
        out_tok = rule(inp_tok)
        
        if out_tok != None:
            break
    
    return '<self>' if out_tok == None else out_tok

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
        2000 two thousand; 2006 two thousand six; 1984 nineteen eighty four; 1201 twelve o one; 1200 twelve hundred
        March 2011 march twenty eleven; September 2008 september two thousand eight
        14 June 2014 the fourteenth of june twenty fourteen
        January 14, 2008 january fourteenth two thousand eight; May 29, 2013 may twenty ninth twenty thirteen; November 20, 2013
        2008-01-08 the eighth of january two thousand eight
    '''
    # check if it is date or not by checking presence of year
    regex = r"[1-2]\d{3}"
    match = re.search(regex, string)
    if match == None:
        return None

    # only year
    match = re.fullmatch(regex, string)
    if match != None:
        return _convertyear(match.group()) 
    
    # month_year
    # regex = r"([A-Za-z]+) ([1-2]\d{3})"
    regex = r"(january|february|march|april|may|june|july|august|september|october|november|december) ([1-2]\d{3})"
    match = re.fullmatch(regex, string, re.IGNORECASE)
    if match != None:
        return match.group(1).lower() + " " + _convertyear(match.group(2))
    
    # date_month_year
    # regex = r"(\d{1,2}) ([A-Za-z]+) ([1-2]\d{3})"
    regex = r"(\d{1,2}) (january|february|march|april|may|june|july|august|september|october|november|december) ([1-2]\d{3})"
    match = re.fullmatch(regex, string, re.IGNORECASE)
    if match != None:
        return "the " + _number_to_ordinal(match.group(1)) + " of " + match.group(2).lower() + " " + _convertyear(match.group(3))
    
    # date_month_year
    # regex = r"([A-Za-z]+) (\d{1,2}),? ([1-2]\d{3})"
    regex = r"(january|february|march|april|may|june|july|august|september|october|november|december) (\d{1,2}),? ([1-2]\d{3})"
    match = re.fullmatch(regex, string, re.IGNORECASE)
    if match != None:
        return match.group(1).lower() + " " + _number_to_ordinal(match.group(2)) + " " + _convertyear(match.group(3))

    # 2008-01-21
    regex = r"(\d{4})-(\d{2})-(\d{2})"
    match = re.fullmatch(regex, string)
    if match != None:
        return "the " + _number_to_ordinal(match.group(3)) + " of " + _months[int(match.group(2))] + " " + _convertyear(match.group(1))
    
    return None

def _convertyear(year):
    if int(year)%1000 == 0:
        return _number_to_word(year[0]) + " thousand"
    
    if 2000 < int(year) < 2009:
        return "two thousand " + _number_to_word(year[-1])
    
    if 2010 <= int(year) < 2100:
        return "twenty " + _number_to_word(year[2:])
    
    if 1100 <= int(year) < 2000:
        word = _number_to_word(year[:2])
        if int(year[2:]) == 0:
            word += " hundred"
        elif 0 < int(year[2:]) < 10:
            word += (" o " + _number_to_word(year[-1]))
        else:
            word = word + ' ' + _number_to_word(year[2:])
        return word

def time2words(string):
    '''
    possible formats
    ----------------
        NOT strictly time but Numbers --> there is no "hours", "minutes", "seconds" in the output tokens
            9:30 nine thirty; 1:54 one fifty four; 20: 43 twenty forty three ||| 11:00am eleven a m; 7:00 p.m. seven p m; 5:10PM; 5:00 PM; 9:00 AM
            two cases:
                am, pm is given --> 12:00pm, 11:02am, etc 
                am, pm not given --> 9:30, 20: 43, 11:00, 21:00; (21:00, twenty one hundred), (11:00, eleven o'clock), (00:00, zero hundred)
        Time format --> only one example found in data 
            2:27:07 two hours twenty seven minutes and seven seconds

    '''
    # NOT strictly time but Numbers
    regex = r"(\d{1,2}\s*):(\s*\d{1,2})(\s*[PpAa]\.?[Mm]\.?)?" # allowing too many white space as such errors may come in data
    match = re.fullmatch(regex, string)
    if match != None:
        if match.group(3) != None:
            num1 = _number_to_word(match.group(1).strip())
            num2 = _number_to_word(match.group(2).strip()) 
            num1 = num1 + " " + num2 if num2 != "zero" else num1
            num1+= (" " + abbreviation(match.group(3).strip().upper())) # pass upper case PM, AM, P.M., etc to abbreviation
            return num1

        num1 = _number_to_word(match.group(1).strip())
        num2 = _number_to_word(match.group(2).strip())         
        if num1 == "zero" and num2 != "zero":
            # TO DO --------------------------------------- REMAINING
            return None
        if num2 == "zero":
            if 0 < int(match.group(1).strip()) < 12:
                return num1 + "o'clock"
            return num1 + "hundred"
        return num1 + " " + num2
    
    # Time format
    regex = r"(\s*\d{1,2}\s*):(\s*\d{1,2}\s*):(\s*\d{1,2}\s*)" # allowing too many white space as such errors may come in data
    match = re.fullmatch(regex, string)
    if match != None:
        num = ""
        num1 = _number_to_word(match.group(1).strip())
        num2 = _number_to_word(match.group(2).strip()) 
        num3 = _number_to_word(match.group(3).strip()) 
        
        zero_time = True
        if num1 != "zero":
            num += (num1 + " hours ")
            zero_time = False
        if num2 != "zero":
            num += (num2 + " minutes ")
            zero_time = False
        if zero_time:
            num = num3 + "seconds"
        else:
            num += ("and " + num3 + " seconds")
        return num

    return None

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
            -3/5 minus three fifths
        hyp_num
            978-0-304-35252-4 nine seven eight sil o sil three o four sil three five two five two sil four
            1-881089-97-5 one sil eight eight one o eight nine sil nine seven sil five
            0-8387-1972-4 o sil eight three eight seven sil one nine seven two sil four
        ordinals 

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

    regex_ordinals = r"(\d+)(st|nd|rd|th)"
    match = re.fullmatch(regex_ordinals, string)
    if match != None:
        return _number_to_ordinal(match.group(1))  # (st|nd|rd|th) is not important

    return None

def _number_to_ordinal(number):
    '''
        get ordinals uptill 99
    '''
    if 0 <= int(number) <= 20:
        return _num2ordinal[int(number)]
    
    if int(number)%10 == 0 and 20 < int(number) < 100:
        return _num2ordinal[int(number)]
    
    if 20 < int(number) < 100:
        return _number_to_word(number[0]+'0') + " " + _num2ordinal[int(number[1])]

    if int(number)%100 == 0:
        return _number_to_word(number) + "th"
    
    if 100 < int(number) < 1000:
        return _number_to_word(number[0]+'00') + " " + _number_to_ordinal(number[1:])

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
    
    global _num2ordinal
    _num2ordinal = {}
    _list = ["zeroth", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
    _list+= ["eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth"]
    for i in range(0,21):
        _num2ordinal[i] = _list[i]
    for i in range(30, 100, 10):
        _num2ordinal[i] = _num2word[i][:-1] + "ieth"

    global _months
    _months = {}
    _list = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    for i in range(1,13):
        _months[i] = _list[i-1]

    # print(_num2word)
    # print(_placeValue)
    # print(_num2ordinal)
    # print(_months)

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