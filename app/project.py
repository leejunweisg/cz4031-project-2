from flask import Flask, request, render_template, jsonify
from preprocessing import get_plans

from collections import deque
import psycopg2
from annotation import (
    natural_explain,
    get_from_subquery,
    get_where_subquery,
    get_query_plan_annotation,
)

import re

app = Flask(__name__)


@app.after_request
def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    # context for rendering the page
    context = {
        "query": None,
        "errors": [],
        "plan_data": None,
        "summary_data": None,
    }

    # handle POST request
    if request.method == "POST":
        # get query from the POST request
        query = request.form["query"]

        if query:
            context["query"] = query

            # get query result
            has_error, result = get_plans(query)

            # add results to context
            if has_error:
                context["errors"].append(result["msg"])
            else:
                context["summary_data"] = result["summary_data"]
                context["plan_data"] = result["plan_data"]
                context["natural_explain"] = result["natural_explain"]
        else:
            context["errors"].append("No query provided!")

    return render_template("index.html", **context)


# def get_db_connection():
#     conn = psycopg2.connect(
#         host="localhost",
#         database="TPC-H",
#         user="postgres",
#         password="password123",
#         port="5432",
#     )
#     return conn


# conn = get_db_connection()

# nodeTypeList = []


# def getAllNodeType(queryPlan):

#     nodeTypeList.append(queryPlan.get("Node Type"))

#     if queryPlan.get("Plans") != None:
#         for plan in queryPlan.get("Plans"):
#             getAllNodeType(plan)
#     return nodeTypeList


# def getNaturalExplanation(query_plan):
#     naturalExplanation = []
#     # queue for bfs
#     q = deque([query_plan])
#     while q:
#         n = len(q)
#         for _ in range(n):
#             node = q.popleft()
#             naturalExplanation.append(natural_explain(node))
#             if "Plans" in node:
#                 for child in node["Plans"]:
#                     q.append(child)

#     return naturalExplanation[::-1]


# def queryPlanConfigParam(param):
#     match param:
#         case "bitmapscan":
#             return "enable_bitmapscan"
#         case "hashagg":
#             return "enable_hashagg"
#         case "Hash Join":
#             return "enable_hashjoin"
#         case "Index Scan":
#             return "enable_indexscan"
#         case "Index Only Scan":
#             return "enable_indexonlyscan"
#         case "Materialize":
#             return "enable_material"
#         case "Merge Join":
#             return "enable_mergejoin"
#         case "Nested Loop":
#             return "enable_nestloop"
#         case "Seq Scan":
#             return "enable_seqscan"
#         case "Sort":
#             return "enable_sort"
#         case "Tid Scan":
#             return "enable_tidscan"
#         case _:
#             return None


# def getImptPlanDetails(queryPlan):
#     # interResult = {"text": {"name": ""}}
#     interResult = {}

#     # get all key:value pair with string value
#     for attr, value in queryPlan.items():
#         if isinstance(value, str) or attr == "Group Key" or attr == "Sort Key":
#             if (
#                 attr.find("Alias")
#                 == -1 & attr.find("Parent")
#                 == -1 & attr.find("Direction")
#                 == -1 & attr.find("Join Type")
#                 == -1
#             ):
#                 # interResult["text"]["name"] += value + " "
#                 interResult[attr] = value

#     # remove last space from string
#     # interResult["text"]["name"] = interResult["text"]["name"][:-1]

#     childrenDetails = []

#     if queryPlan.get("Plans") != None:
#         for plan in queryPlan.get("Plans"):
#             childrenDetails.append(getImptPlanDetails(plan))

#     if len(childrenDetails) != 0:
#         interResult["children"] = childrenDetails

#     return interResult


# def getAltQueryPlan(queryPlan, queryResult, cur):

#     # Get all node type from Query Plan Result
#     getAllNodeType(queryResult[0][0][0].get("Plan"))

#     queryConfigParamList = []

#     # Get list of query config settings parameters
#     for nodeType in nodeTypeList:
#         queryConfigParamList.append(queryPlanConfigParam(nodeType))

#     # Remove None from list
#     filteredQueryConfigParamList = list(
#         filter(lambda x: x != None, queryConfigParamList)
#     )

#     for item in filteredQueryConfigParamList:
#         query = "SET LOCAL {} TO off;".format(item)
#         cur.execute(query)

#     cur.execute(queryPlan)
#     altPlanResult = cur.fetchall()

#     # Reset query plan configuration
#     cur.execute("RESET ALL;")

#     # Clear all list to prepare for next alternative query plan
#     filteredQueryConfigParamList.clear()
#     nodeTypeList.clear()
#     queryConfigParamList.clear()

#     return altPlanResult


# @app.route("/testGetPlan", methods=["POST"])
# def testGetPlan():
#     cur = conn.cursor()
#     data = request.get_json()

#     queryInput = data["queryInput"]

#     # annotationListWhere = splitWhere.split("and")
#     # print(annotationListWhere)

#     queryPlan = """
#     EXPLAIN (ANALYZE false, SETTINGS true, FORMAT JSON) {};
#     """.format(
#         queryInput
#     )

#     result = {
#         "natural": {"naturalLang1": [], "naturalLang2": [], "naturalLang3": []},
#         "plan_data": {"Plan 1": {}, "Plan 2": {}, "Plan 3": {}},
#         "graph_data": {"Plan 1": {}, "Plan 2": {}, "Plan 3": {}},
#         "annotation": {},
#         "subquery": {},
#     }

#     try:
#         cur.execute(queryPlan)
#         planResult1 = cur.fetchall()

#         planResult2 = getAltQueryPlan(queryPlan, planResult1, cur)

#         planResult3 = getAltQueryPlan(queryPlan, planResult2, cur)

#         planResultDiagram1 = getImptPlanDetails(planResult1[0][0][0].get("Plan"))

#         planResultDiagram2 = getImptPlanDetails(planResult2[0][0][0].get("Plan"))

#         planResultDiagram3 = getImptPlanDetails(planResult3[0][0][0].get("Plan"))

#         naturalLang1 = getNaturalExplanation(planResult1[0][0][0].get("Plan"))

#         naturalLang2 = getNaturalExplanation(planResult2[0][0][0].get("Plan"))

#         naturalLang3 = getNaturalExplanation(planResult3[0][0][0].get("Plan"))

#         # annotation

#         fromSubQuery = get_from_subquery(queryInput)

#         whereSubQuery = get_where_subquery(queryInput)

#         result["subquery"]["from"] = fromSubQuery
#         result["subquery"]["where"] = whereSubQuery

#         result["annotation"]["Plan 1"] = get_query_plan_annotation(
#             fromSubQuery, naturalLang1
#         )

#         result["plan_data"]["Plan 1"] = planResult1[0][0][0]
#         result["graph_data"]["Plan 1"] = planResultDiagram1
#         result["natural"]["naturalLang1"] = naturalLang1

#         # check if there are repeated query plans
#         if planResultDiagram2 != planResultDiagram1:
#             result["plan_data"]["Plan 2"] = planResult2[0][0][0]
#             result["graph_data"]["Plan 2"] = planResultDiagram2
#             result["natural"]["naturalLang2"] = naturalLang2
#             result["annotation"]["Plan 2"] = get_query_plan_annotation(
#                 fromSubQuery, naturalLang2
#             )

#         if (
#             planResultDiagram3 != planResultDiagram1
#             and planResultDiagram3 != planResultDiagram2
#         ):
#             result["plan_data"]["Plan 3"] = planResult3[0][0][0]
#             result["graph_data"]["Plan 3"] = planResultDiagram3
#             result["natural"]["naturalLang3"] = naturalLang3
#             result["annotation"]["Plan 3"] = get_query_plan_annotation(
#                 fromSubQuery, naturalLang3
#             )

#         cur.close()
#     except Exception as e:
#         # rollback when theres error
#         conn.rollback()
#         cur.close()
#         print(e)
#         return "Error", 400

#     return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
