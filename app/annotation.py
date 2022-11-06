from collections import deque


def get_graph_data(plan):
    inter_result = {"text": {"name": ""}}

    # get all key:value pair with string value
    for attr, value in plan.items():
        if isinstance(value, str):
            if (
                    attr.find("Alias")
                    == -1 & attr.find("Parent")
                    == -1 & attr.find("Direction")
                    == -1
            ):
                inter_result["text"]["name"] += value + " "

    # remove last space from string
    inter_result["text"]["name"] = inter_result["text"]["name"][:-1]

    children_details = []

    if plan.get("Plans") is not None:
        for plan in plan.get("Plans"):
            children_details.append(get_graph_data(plan))

    if len(children_details) != 0:
        inter_result["children"] = children_details

    return inter_result


def get_plan_summary(plan):
    """
    Produces a summary given a query plan.
    - Total cost of all nodes
    - Total number of nodes
    """

    summary = {
        "total_cost": 0,
        "nodes_count": 0,
    }

    # queue for bfs
    q = deque([plan])
    while q:
        n = len(q)
        for _ in range(n):
            node = q.popleft()
            summary["nodes_count"] += 1
            summary["total_cost"] += (node["Total Cost"])
            if "Plans" in node:
                for child in node["Plans"]:
                    q.append(child)

    return summary
