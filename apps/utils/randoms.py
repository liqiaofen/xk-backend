import random
import string

string_punctuation = '!#$%&()*+,-.:;<=>?@[]^_{}~'


def random_string(length=6, digit=True, upper=True, special_char=True):
    chars = string.ascii_lowercase
    if upper:
        chars += string.ascii_uppercase
    if digit:
        chars += string.digits
    random_str = list(random.choice(chars) for i in range(length))

    if special_char:
        spc = random.choice(string_punctuation)
        i = random.randint(0, length)
        random_str[i] = spc
    random_str = ''.join(random_str)
    return random_str
