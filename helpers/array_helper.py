def keys_exists(dictionary, keys):
    nested_dict = dictionary
    for key in keys:
        try:
            nested_dict = nested_dict[key]
        except KeyError:
            return False
    return True
