def convert_list_of_lists_to_single_list(list_of_lists):
    """
    Converts a list of lists to a single list.
    """
    single_list = []
    try:
        if isinstance(list_of_lists[0], list):  # if list is a list of lists
            for list_ in list_of_lists:
                single_list.extend(list_)
            return single_list
        
        else: 
            return list_of_lists # return original input
    except:
        return list_of_lists
