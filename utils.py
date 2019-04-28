def query_to_dict(query, name, id_names):
    """
    Converts the result of a SQL query to a jsonifiable dictionary.

    {name: [...]}

    :param query: List of tuples (result of SQL select)
    :param name: Name of the main dict field
    :param id_names: (id, name) pairs for each index to be taken from the query, and a correpsonding name
    :return:
    """
    res_dict = {name: []}

    for row in query:
        part_dict = {}
        for (id_, name_) in id_names:
            part_dict[name_] = row[id_]

        res_dict[name].append(part_dict)

    return res_dict
