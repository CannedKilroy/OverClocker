
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


def dict_differentiate(old_dict: dict, new_dict: dict, logger):
    """
    
    """
    old_dict = strip_chars(old_dict)
    new_dict = strip_chars(new_dict)

    return_dict = {}
    common_keys = old_dict.keys() & new_dict.keys()
    for key in common_keys:

        if old_dict[key] != new_dict[key]:
            return_dict[key] = new_dict[key] + "+"
            logger.info(f"Link updated {new_dict[key]}")
        else:
            # If they are equal put new link back in without "+"
            return_dict[key] = new_dict[key]
    return_dict.update({k: old_dict[k] for k in old_dict.keys() - new_dict.keys()})
    return_dict.update({k: new_dict[k] for k in new_dict.keys() - old_dict.keys()})
    return return_dict