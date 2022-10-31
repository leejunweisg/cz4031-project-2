
import psycopg2
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

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

# Flask by default supports only get method, so we need to add post inside the method's parameter
@app.route('/getPlan', methods=['POST'])
def getPlan():
    cur = conn.cursor()
    # var queryInput = goes to the current request, into the form, and get the parameter called query
    queryInput = request.form["query"]
    
    queryPlan1 = """
    EXPLAIN (ANALYZE true, SETTINGS true, FORMAT JSON) {};
    """.format(queryInput)
    
    queryPlan2 = """
    SET LOCAL enable_nestloop TO off;
    SET LOCAL enable_hashjoin TO off;
    EXPLAIN (ANALYZE true, COSTS true, SETTINGS true, FORMAT JSON) {};
    """.format(queryInput)
    
    cur.execute(queryPlan1)
    planResult1 = cur.fetchall()
    cur.execute(queryPlan2)
    planResult2 = cur.fetchall()
    
    # Reset query plan configuration
    cur.execute("ROLLBACK")
        
    cur.close()

    # return jsonify({"QueryPlan1": planResult1[0][0][0], "QueryPlan2": planResult2[0][0][0]})
    # Can take more than 1 argument, if it takes another arg, you can pass in the name of any variable you want.
	# LHS = RHS; LHS is the name of a var I want to give to the template, RHS is the value of that var.
    return render_template(
        "plan.html",
        queryInput=queryInput,
        planResult1=planResult1[0][0][0],
        planResult2=planResult2[0][0][0]
    )


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