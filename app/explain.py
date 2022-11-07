bold = {"START": "<b>", "END": "</b>"}


def bold_string(string):
    return bold["START"] + string + bold["END"]


def aggregate_explain(query_plan):
    strategy = query_plan["Strategy"]
    if strategy == "Sorted":
        result = f"{bold_string('Aggregate')} operation is perfomed on the rows based on their keys."
        if "Group Key" in query_plan:
            result += f" The {bold_string('aggregated')} key(s) are: "
            for key in query_plan["Group Key"]:
                result += bold_string(key) + ","
            result = result[:-1] + "."
        if "Filter" in query_plan:
            result += " The rows are also filtered by " + bold_string(
                query_plan["Filter"].replace("::text", "")
            )
            result += "."
        return result
    elif strategy == "Hashed":
        result = f"{bold_string('Aggregate')} operation is performed by hashing on all rows based on the following key(s): "
        for key in query_plan["Group Key"]:
            result += bold_string(key.replace("::text", "")) + ", "
        result += f"then the results are {bold_string('aggregated')} into bucket(s) accordung to the hashed key."
        return result
    elif strategy == "Plain":
        return (
            f"Normal {bold_string('Aggregate')} operation is performed on the result."
        )
    else:
        return "Aggregation is performed."


def append_explain():
    result = f"{bold_string('Append')} operation is performed with multiple sub-operations. All the rows that are returned as one set as the result."
    return result


def cte_explain(query_plan):
    result = (
        f"A {bold_string('CTE scan')} operation is performed on the table "
        + bold_string(str(query_plan["CTE Name"]))
        + " which is stored in memory "
    )
    if "Index Cond" in query_plan:
        result += " with the condition(s) " + bold_string(
            query_plan["Index Cond"].replace("::text", "")
        )
    if "Filter" in query_plan:
        result += " the result is then filtered by " + bold_string(
            query_plan["Filter"].replace("::text", "")
        )
    result += "."
    return result


def function_scan_explain(query_plan):
    return "The function {} is run and returns all the recordset(s) that it created.".format(
        bold_string(query_plan["Function Name"])
    )


def group_explain(query_plan):
    result = f"The result from the previous operation is {bold_string('grouped')} by the following key(s): "
    for i, key in enumerate(query_plan["Group Key"]):
        result += bold_string(key.replace("::text", ""))
        if i == len(query_plan["Group Key"]) - 1:
            result += "."
        else:
            result += ", "
    return result


def index_scan_explain(query_plan):
    result = ""
    result += (
        f"{bold_string('Index Scan')} operation is performed using "
        + bold_string(query_plan["Index Name"])
        + " index table "
    )
    if "Index Cond" in query_plan:
        result += " with the following condition(s): " + bold_string(
            query_plan["Index Cond"].replace("::text", "")
        )
    result += ", and the {} table and fetches rows that matches the conditions.".format(
        bold_string(query_plan["Relation Name"])
    )

    if "Filter" in query_plan:
        result += (
            " The result is then filtered by "
            + bold_string(query_plan["Filter"].replace("::text", ""))
            + "."
        )
    return result


def index_only_scan_explain(query_plan):
    result = ""
    result += (
        f"An {bold_string('Index Scan')} operation is done using "
        + bold_string(query_plan["Index Name"])
        + " index table"
    )
    if "Index Cond" in query_plan:
        result += " with the condition(s) " + bold_string(
            query_plan["Index Cond"].replace("::text", "")
        )
    result += ". Matches are then returned as the result."
    if "Filter" in query_plan:
        result += (
            " The result is finally filtered by: "
            + bold_string(query_plan["Filter"].replace("::text", ""))
            + "."
        )

    return result


def limit_explain(query_plan):
    result = f"A scan is performed with a {bold_string('limit')} of {query_plan['Plan Rows']} entries."
    return result


def materialize_explain():
    result = "The results of previous operation(s) are stored in physical memory/disk for faster access."
    return result


def unique_explain():
    result = f"A scan is performed on previous results to remove {bold_string('un-unique')} values."
    return result


def merge_join_explain(query_plan):
    result = f"{bold_string('Merge Join')} operation is performed on results from sub-operations"

    if "Merge Cond" in query_plan:
        result += " on the condition " + bold_string(
            query_plan["Merge Cond"].replace("::text", "")
        )

    if "Join Type" == "Semi":
        result += " but only the rows from the left relation is returned as the result"

    result += "."
    return result


def setop_explain(query_plan):
    result = "Results are returned base on the"
    cmd_name = bold_string(str(query_plan["Command"]))
    if cmd_name == "Except" or cmd_name == "Except All":
        result += "differences "
    else:
        result += "similarities "
    result += (
        "between the two previously scanned tables using the {} operation.".format(
            bold_string(query_plan["Node Type"])
        )
    )

    return result


def subquery_scan_explain():
    result = f"{bold_string('Subquery scan')} operation is performed on results from sub-operations without any changes."
    return result


def values_scan_explain():
    result = f"A {bold_string('Values Scan')} operation is performed using the values given in query."
    return result


def seq_scan_explain(query_plan):
    sentence = f"{bold_string('Sequential Scan')} operation is performed on relation "
    if "Relation Name" in query_plan:
        sentence += bold_string(query_plan["Relation Name"])
    if "Alias" in query_plan:
        if query_plan["Relation Name"] != query_plan["Alias"]:
            sentence += " with the alias of {}".format(query_plan["Alias"])
    if "Filter" in query_plan:
        sentence += " and filtered by {}".format(
            query_plan["Filter"].replace("::text", "")
        )
    sentence += "."

    return sentence


def nested_loop_explain():
    result = f"The join results between the {bold_string('Nested Loop')} scans of the suboperations are returned."
    return result


def sort_explain(query_plan):
    result = f"The result is {bold_string('Sorted')} using the attribute "
    if "DESC" in query_plan["Sort Key"]:
        result += (
            bold_string(str(query_plan["Sort Key"].replace("DESC", "")))
            + " in descending order of "
        )
    elif "INC" in query_plan["Sort Key"]:
        result += (
            bold_string(str(query_plan["Sort Key"].replace("INC", "")))
            + " in ascending order of "
        )
    else:
        result += bold_string(str(query_plan["Sort Key"]))
    result += "."
    return result


def hash_explain():
    result = f"{bold_string('Hash')} function is used to make a memory {bold_string('hash')} using the table rows."
    return result


def hash_join_explain(query_plan):
    result = f"The result from previous operation is joined using {bold_string('Hash')} {bold_string(query_plan['Join Type'])} {bold_string('Join')}"
    if "Hash Cond" in query_plan:
        result += " on the condition: {}".format(
            bold_string(query_plan["Hash Cond"].replace("::text", ""))
        )
    result += "."
    return result


def explain(query_plan):
    match query_plan["Node Type"]:
        case "Aggregate":
            return aggregate_explain(query_plan)
        case "Append":
            return append_explain()
        case "CTE Scan":
            return cte_explain(query_plan)
        case "Function Scan":
            return function_scan_explain(query_plan)
        case "Group":
            return group_explain(query_plan)
        case "Index Scan":
            return index_scan_explain(query_plan)
        case "Index Only Scan":
            return index_only_scan_explain(query_plan)
        case "Limit":
            return limit_explain(query_plan)
        case "Materialize":
            return materialize_explain()
        case "Unique":
            return unique_explain()
        case "Merge Join":
            return merge_join_explain(query_plan)
        case "SetOp":
            return setop_explain(query_plan)
        case "Subquery Scan":
            return subquery_scan_explain()
        case "Values Scan":
            return values_scan_explain()
        case "Seq Scan":
            return seq_scan_explain(query_plan)
        case "Nested Loop":
            return nested_loop_explain()
        case "Sort":
            return sort_explain(query_plan)
        case "Hash":
            return hash_explain()
        case "Hash Join":
            return hash_join_explain(query_plan)
        case _:
            return query_plan["Node Type"]
