from flask import Flask, request, render_template

from preprocessing import get_plans

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
        "graph_data": None,
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
                context["graph_data"] = result["graph_data"]
        else:
            context["errors"].append("No query provided!")

    return render_template("index.html", **context)


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


# @app.route("/testGetPlan", methods=["POST"])
# def testGetPlan():
#     cur = conn.cursor()
#     data = request.get_json()
#
#     queryInput = data["queryInput"]
#
#     queryPlan = """
#     EXPLAIN (ANALYZE false, SETTINGS true, FORMAT JSON) {};
#     """.format(
#         queryInput
#     )
#
#     result = {
#         "plan_data": {"Plan 1": {}, "Plan 2": {}, "Plan 3": {}},
#         "graph_data": {"Plan 1": {}, "Plan 2": {}, "Plan 3": {}},
#     }
#
#     try:
#         cur.execute(queryPlan)
#         planResult1 = cur.fetchall()
#
#         planResult2 = getAltQueryPlan(queryPlan, planResult1, cur)
#
#         planResult3 = getAltQueryPlan(queryPlan, planResult2, cur)
#
#         planResultDiagram1 = getImptPlanDetails(planResult1[0][0][0].get("Plan"))
#
#         planResultDiagram2 = getImptPlanDetails(planResult2[0][0][0].get("Plan"))
#
#         planResultDiagram3 = getImptPlanDetails(planResult3[0][0][0].get("Plan"))
#
#         print(planResultDiagram1 == planResultDiagram2)
#
#         result["plan_data"]["Plan 1"] = planResult1[0][0][0]
#         result["graph_data"]["Plan 1"] = planResultDiagram1
#
#         # check if there are repeated query plans
#         if planResultDiagram2 != planResultDiagram1:
#             result["plan_data"]["Plan 2"] = planResult2[0][0][0]
#             result["graph_data"]["Plan 2"] = planResultDiagram2
#
#         if (
#                 planResultDiagram3 != planResultDiagram1
#                 and planResultDiagram3 != planResultDiagram2
#         ):
#             result["plan_data"]["Plan 3"] = planResult3[0][0][0]
#             result["graph_data"]["Plan 3"] = planResultDiagram3
#
#         cur.close()
#     except:
#         # rollback when theres error
#         conn.rollback()
#         cur.close()
#         return "Error", 400
#
#     return jsonify(result)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
