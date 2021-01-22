""" utility functions for manipulating strings """

def after(substring, string):
    """
    returns everything after substring in string
    substring must occur only once in string 
    """
    return assert_non_empty(unique_split(substring, string)[1])

def after_first(substring, string):
    """ returns everything after first substring in string """
    return assert_non_empty(first_split(substring, string)[1])

def after_last(substring, string):
    """ returns everything after last substring in string """
    return assert_non_empty(last_split(substring, string)[1])



def before(substring, string):
    """
    returns everything before substring in string
    substring must occur only once in string 
    """
    return assert_non_empty(unique_split(substring, string)[0])

def before_first(substring, string):
    """ returns everything before first substring in string """
    return assert_non_empty(first_split(substring, string)[0])

def before_last(substring, string):
    """ returns everything before last substring in string """
    return assert_non_empty(last_split(substring, string)[0])



def between(from_, to, string):
    """
    returns everything between to and from_ in string
    both to and from_ must be unique in string
    """
    try:
        return after(from_, before(to, string))

    except AssertionError: # try each order to see if one works
        return before(to, after(from_, string))



# utility functions for the utility functions
def safe_split(substring, string):
    assert substring in string, f'"{substring}" not found in "{string}"'
    return string.split(substring)

def last_split(substring, string):
    parts = safe_split(substring, string)
    return substring.join(parts[:-1]), parts[-1]

def first_split(substring, string):
    parts = safe_split(substring, string)
    return parts[0], substring.join(parts[1:])

def unique_split(substring, string):
    """ returns string split by substring while checking that substring is unique in string """
    parts = safe_split(substring, string)
    assert len(parts) == 2, f'more than one substring "{substring}" in string "{string}"'
    return parts

def assert_non_empty(string):
    assert len(string) > 0, f'string is empty: {string}'
    return string
