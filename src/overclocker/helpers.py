# Strip characters
def strip_chars(a_dict):
    """
    Strip whitespace and other characters
    as well as '+' to make accurate comparisons
    between new and old links
    """
    strips = " \t\n\r+"
    for key, value in a_dict.items():
        a_dict[key] = value.rstrip(strips)
    print(a_dict)
    return a_dict