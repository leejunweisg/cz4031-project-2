
import psycopg2
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

nodeTypeList = []


def getAllNodeType(queryPlan):
    nodeTypeList.append(queryPlan.get("Node Type"))

    if queryPlan.get("Plans") != None:
        for plan in queryPlan.get("Plans"):
            getAllNodeType(plan)
    return


def getImptPlanDetails(queryPlan):
    interResult = {"text": {"name": ""}}

    # get all key:value pair with string value
    for attr, value in queryPlan.items():
        if (isinstance(value, str)):
            if (attr.find("Alias") == -1
                & attr.find("Parent") == -1
                    & attr.find("Direction") == -1):
                interResult["text"]["name"] += value + " "

    # remove last space from string
    interResult["text"]["name"] = interResult["text"]["name"][:-1]

    childrenDetails = []

    if queryPlan.get("Plans") != None:
        for plan in queryPlan.get("Plans"):
            childrenDetails.append(getImptPlanDetails(plan))

    if len(childrenDetails) != 0:
        interResult["children"] = childrenDetails

    # dict(sorted(interResult.items(), key=lambda interResult: interResult[1]))

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
        filter(lambda x: x != None, queryConfigParamList))

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
    conn = psycopg2.connect(host='localhost',
                            database="TPC-H",
                            user="postgres",
                            password="password123",
                            port="5432")
    return conn


conn = get_db_connection()


@app.after_request
def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


@app.route("/")  # When to call this function
# @app.route("/home")  # @ is a decorator which is used to call this function
def index():
    """ Renders the home page """
    print("Renders the home page")
    return render_template(
        "index.html"
    )


@app.route("/example")
def example():
    # data to generate the graph
    graph_data = {
        "plan1": {
            "text": {"name": "I am the parent (plan 1)!"},
            "children": [
                {"text": {"name": "I am the left child!"}},
                {"text": {"name": "I am the right child!"}}
            ]
        },
        "plan2": {
            "children": [
                {
                    "children": [
                        {
                            "text": {
                                "name": "Bitmap Index Scan region_pkey (r_regionkey = 1)"
                            }
                        }
                    ],
                    "text": {
                        "name": "Bitmap Heap Scan region (r_regionkey = 1)"
                    }
                },
                {
                    "children": [
                        {
                            "text": {
                                "name": "Seq Scan customer"
                            }
                        },
                        {
                            "children": [
                                {
                                    "text": {
                                        "name": "Index Scan nation_pkey nation (n_regionkey = 1)"
                                    }
                                }
                            ],
                            "text": {
                                "name": "Hash"
                            }
                        }
                    ],
                    "text": {
                        "name": "Hash Join Inner (customer.c_nationkey = nation.n_nationkey)"
                    }
                }
            ],
            "text": {
                "name": "Nested Loop Inner"
            }
        }

    }

    # a dictionary of variables that we wish to pass to the template
    context = {
        "graph_data": graph_data
    }

    # render template
    return render_template("example.html", **context)


# Flask by default supports only get method, so we need to add post inside the method's parameter
@app.route('/getPlan', methods=['POST'])
def getPlan():
    cur = conn.cursor()
    # var queryInput = goes to the current request, into the form, and get the parameter called query
    queryInput = request.form["query"]

    queryPlan = """
    EXPLAIN (ANALYZE true, SETTINGS true, FORMAT JSON) {};
    """.format(queryInput)

    cur.execute(queryPlan)
    planResult1 = cur.fetchall()

    planResult2 = getAltQueryPlan(queryPlan, planResult1, cur)

    planResult3 = getAltQueryPlan(queryPlan, planResult2, cur)

    planResultDiagram1 = getImptPlanDetails(planResult1[0][0][0].get("Plan"))

    planResultDiagram2 = getImptPlanDetails(planResult2[0][0][0].get("Plan"))

    planResultDiagram3 = getImptPlanDetails(planResult3[0][0][0].get("Plan"))

    cur.close()

    # return jsonify({"QueryPlan1": planResult1[0][0][0],
    #                 "QueryPlan2": planResult2[0][0][0],
    #                 "QueryPlan3": planResult3[0][0][0],
    #                 "planResultDiagram1": planResultDiagram1,
    #                 "planResultDiagram2": planResultDiagram2,
    #                 "planResultDiagram3": planResultDiagram3})

    # return jsonify({"QueryPlan1": planResult1[0][0][0], "QueryPlan2": planResult2[0][0][0]})
    # Can take more than 1 argument, if it takes another arg, you can pass in the name of any variable you want.
    # LHS = RHS; LHS is the name of a var I want to give to the template, RHS is the value of that var.
    return render_template(
        "index.html",
        queryInput=queryInput,
        planResult1=planResult1[0][0][0],
        planResult2=planResult2[0][0][0]
    )


@app.route('/testGetPlan', methods=['POST'])
def testGetPlan():
    cur = conn.cursor()
    data = request.get_json()

    queryInput = data["queryInput"]

    queryPlan = """
    EXPLAIN (ANALYZE true, SETTINGS true, FORMAT JSON) {};
    """.format(queryInput)

    cur.execute(queryPlan)
    planResult1 = cur.fetchall()

    planResult2 = getAltQueryPlan(queryPlan, planResult1, cur)

    planResult3 = getAltQueryPlan(queryPlan, planResult2, cur)

    planResultDiagram1 = getImptPlanDetails(planResult1[0][0][0].get("Plan"))

    planResultDiagram2 = getImptPlanDetails(planResult2[0][0][0].get("Plan"))

    planResultDiagram3 = getImptPlanDetails(planResult3[0][0][0].get("Plan"))

    cur.close()

    return jsonify({"QueryPlan1": planResult1[0][0][0],
                    "QueryPlan2": planResult2[0][0][0],
                    "QueryPlan3": planResult3[0][0][0],
                    "planResultDiagram1": planResultDiagram1,
                    "planResultDiagram2": planResultDiagram2,
                    "planResultDiagram3": planResultDiagram3})


# @app.route('/test', methods=['GET'])
# def test():

#     cur = conn.cursor()

#     queryInput = """SELECT c_name, c_address
#                     FROM customer
#                     LEFT JOIN nation ON nation.n_nationkey=customer.c_nationkey
#                     LEFT JOIN region ON nation.n_regionkey=region.r_regionkey
#                     WHERE region.r_regionkey=1;"""

#     queryPlan1 = """
#     EXPLAIN (ANALYZE true, COSTS true, SETTINGS true, FORMAT JSON) {};
#     """.format(queryInput)

#     queryPlan2 = """
#     SET LOCAL enable_nestloop TO off;
#     SET LOCAL enable_hashjoin TO off;
#     EXPLAIN (ANALYZE true, COSTS true, SETTINGS true, FORMAT JSON) {};
#     """.format(queryInput)

#     cur.execute(queryPlan1)
#     planResult1 = cur.fetchall()
#     cur.execute(queryPlan2)
#     planResult2 = cur.fetchall()

#     # Reset query plan configuration
#     cur.execute("ROLLBACK")

#     # Query result
#     # cur.execute(queryInput)
#     # queryResult = cur.fetchall()
#     # print(f"[-] Query results:")
#     # # convert Decimal to string
#     # # currently convert ther whole result instead of just the Decimal
#     # json_str = json.dumps(queryResult, cls=DecimalEncoder)
#     # print(queryResult)

#     cur.close()

#     return jsonify({"QueryPlan1": planResult1[0][0][0], "QueryPlan2": planResult2[0][0][0]})


if __name__ == '__main__':
    app.run(debug=True)
