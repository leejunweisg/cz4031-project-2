import psycopg2
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

nodeTypeList = []


def getAllNodeType(queryPlan):
    nodeTypeList.append(queryPlan.get("Node Type"))

    if queryPlan.get("Plans") != None:
        for plan in queryPlan.get("Plans"):
            getAllNodeType(plan)
    return nodeTypeList


def getImptPlanDetails(queryPlan):
    interResult = {"text": {"name": ""}}

    # get all key:value pair with string value
    for attr, value in queryPlan.items():
        if isinstance(value, str):
            if (
                attr.find("Alias")
                == -1 & attr.find("Parent")
                == -1 & attr.find("Direction")
                == -1
            ):
                interResult["text"]["name"] += value + " "

    # remove last space from string
    interResult["text"]["name"] = interResult["text"]["name"][:-1]

    childrenDetails = []

    if queryPlan.get("Plans") != None:
        for plan in queryPlan.get("Plans"):
            childrenDetails.append(getImptPlanDetails(plan))

    if len(childrenDetails) != 0:
        interResult["children"] = childrenDetails

    return interResult


def getAltQueryPlan(queryPlan, queryResult, cur):

    # Get all node type from Query Plan Result
    getAllNodeType(queryResult[0][0][0].get("Plan"))

    queryConfigParamList = []

    # Get list of query config settings parameters
    for nodeType in nodeTypeList:
        queryConfigParamList.append(queryPlanConfigParam(nodeType))

    # Remove None from list
    filteredQueryConfigParamList = list(
        filter(lambda x: x != None, queryConfigParamList)
    )

    for item in filteredQueryConfigParamList:
        query = "SET LOCAL {} TO off;".format(item)
        cur.execute(query)

    cur.execute(queryPlan)
    altPlanResult = cur.fetchall()

    # Reset query plan configuration
    cur.execute("RESET ALL;")

    # Clear all list to prepare for next alternative query plan
    filteredQueryConfigParamList.clear()
    nodeTypeList.clear()
    queryConfigParamList.clear()

    return altPlanResult


def queryPlanConfigParam(param):
    match param:
        case "bitmapscan":
            return "enable_bitmapscan"
        case "hashagg":
            return "enable_hashagg"
        case "Hash Join":
            return "enable_hashjoin"
        case "Index Scan":
            return "enable_indexscan"
        case "Index Only Scan":
            return "enable_indexonlyscan"
        case "Materialize":
            return "enable_material"
        case "Merge Join":
            return "enable_mergejoin"
        case "Nested Loop":
            return "enable_nestloop"
        case "Seq Scan":
            return "enable_seqscan"
        case "Sort":
            return "enable_sort"
        case "Tid Scan":
            return "enable_tidscan"
        case _:
            return None


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="TPC-H",
        user="postgres",
        password="password123",
        port="5432",
    )
    return conn


conn = get_db_connection()


@app.after_request
def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


@app.route("/example")
def example():
    # data to generate the graph
    graph_data = {
        "Plan 1": {
            "text": {"name": "I am the parent (plan 1)!"},
            "children": [
                {"text": {"name": "I am the left child!"}},
                {"text": {"name": "I am the right child!"}},
            ],
        },
        "plan2": {
            "text": {"name": "Limit"},
            "children": [{"text": {"name": "Index Scan customer_pkey customer"}}],
        },
    }

    # a dictionary of variables that we wish to pass to the template
    context = {"graph_data": graph_data}

    # render template
    return render_template("example.html", **context)


# ============================================================================================


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        """Renders the home page"""
        print("Renders the home page")
        return render_template(
            "index.html",
            query="",
        )
    else:
        """Process the query"""
        print("Process the query")
        query = request.form["query"]
        queryResult = getPlan(query)

        # a dictionary of variables that we wish to pass to the template
        # plan_data = {
        #     "Plan 1": queryResult["QueryPlan1"],
        #     "Plan 2": queryResult["QueryPlan2"],
        #     "Plan 3": queryResult["QueryPlan3"],
        # }
        # graph_data = {
        #     "Plan 1": queryResult["planResultDiagram1"],
        #     "Plan 2": queryResult["planResultDiagram2"],
        #     "Plan 3": queryResult["planResultDiagram3"],
        # }
        # print(graph_data["Plan 1"])
        # plan_data = [
        #     queryResult["QueryPlan1"],
        #     queryResult["QueryPlan2"],
        #     queryResult["QueryPlan3"]
        # ]
        # graph_data = [
        #     queryResult["planResultDiagram1"],
        #     queryResult["planResultDiagram2"],
        #     queryResult["planResultDiagram3"]
        # ]

        if queryResult == "Invalid Query Input":
            return render_template(
                "index.html",
                plan_data={
                    "Plan 1": {},
                    "Plan 2": {},
                    "Plan 3": {},
                },
                graph_data={
                    "Plan 1": {},
                    "Plan 2": {},
                    "Plan 3": {},
                },
            )
        else:
            return render_template(
                "index.html",
                query=query,
                plan_data=queryResult["plan_data"],
                graph_data=queryResult["graph_data"],
            )


def getPlan(queryInput):
    cur = conn.cursor()

    queryPlan = """
    EXPLAIN (ANALYZE true, SETTINGS true, FORMAT JSON) {};
    """.format(
        queryInput
    )

    try:
        cur.execute(queryPlan)
        planResult1 = cur.fetchall()

        planResult2 = getAltQueryPlan(queryPlan, planResult1, cur)

        planResult3 = getAltQueryPlan(queryPlan, planResult2, cur)

        planResultDiagram1 = getImptPlanDetails(planResult1[0][0][0].get("Plan"))

        planResultDiagram2 = getImptPlanDetails(planResult2[0][0][0].get("Plan"))

        planResultDiagram3 = getImptPlanDetails(planResult3[0][0][0].get("Plan"))

        print(planResultDiagram1 == planResultDiagram2)

        result = {"plan_data": {}, "graph_data": {}}

        result["plan_data"]["Plan 1"] = planResult1[0][0][0]
        result["graph_data"]["Plan 1"] = planResultDiagram1

        # check if there are repeated query plans
        if planResultDiagram2 != planResultDiagram1:
            result["plan_data"]["Plan 2"] = planResult2[0][0][0]
            result["graph_data"]["Plan 2"] = planResultDiagram2
        if (
            planResultDiagram3 != planResultDiagram1
            and planResultDiagram3 != planResultDiagram2
        ):
            result["plan_data"]["Plan 3"] = planResult3[0][0][0]
            result["graph_data"]["Plan 3"] = planResultDiagram3

        cur.close()
    except:
        # rollback when theres error
        conn.rollback()
        cur.close()
        return "Invalid Query Input"

    return result


@app.route("/testGetPlan", methods=["POST"])
def testGetPlan():
    cur = conn.cursor()
    data = request.get_json()

    queryInput = data["queryInput"]

    queryPlan = """
    EXPLAIN (ANALYZE true, SETTINGS true, FORMAT JSON) {};
    """.format(
        queryInput
    )

    try:
        cur.execute(queryPlan)
        planResult1 = cur.fetchall()

        planResult2 = getAltQueryPlan(queryPlan, planResult1, cur)

        planResult3 = getAltQueryPlan(queryPlan, planResult2, cur)

        planResultDiagram1 = getImptPlanDetails(planResult1[0][0][0].get("Plan"))

        planResultDiagram2 = getImptPlanDetails(planResult2[0][0][0].get("Plan"))

        planResultDiagram3 = getImptPlanDetails(planResult3[0][0][0].get("Plan"))

        print(planResultDiagram1 == planResultDiagram2)

        result = {"plan_data": {}, "graph_data": {}}

        result["plan_data"]["Plan 1"] = planResult1[0][0][0]
        result["graph_data"]["Plan 1"] = planResultDiagram1

        # check if there are repeated query plans
        if planResultDiagram2 != planResultDiagram1:
            result["plan_data"]["Plan 2"] = planResult2[0][0][0]
            result["graph_data"]["Plan 2"] = planResultDiagram2
        if (
            planResultDiagram3 != planResultDiagram1
            and planResultDiagram3 != planResultDiagram2
        ):
            result["plan_data"]["Plan 3"] = planResult3[0][0][0]
            result["graph_data"]["Plan 3"] = planResultDiagram3

        cur.close()
    except:
        # rollback when theres error
        conn.rollback()
        cur.close()
        return "Error", 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
