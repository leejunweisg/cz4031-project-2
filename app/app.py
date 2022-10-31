
import psycopg2
from flask import Flask, jsonify, request
from decimal import *

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database="TPC-H",
                            user="postgres",
                            password="password123",
                            port="5432")
    return conn

conn = get_db_connection()

@app.route('/getPlan', methods=['POST'])
def getPlan():
    cur = conn.cursor()
    data = request.get_json()
    
    queryInput = data["queryInput"]
    
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

    return jsonify({"QueryPlan1": planResult1[0][0][0], "QueryPlan2": planResult2[0][0][0]})


@app.route('/test', methods=['GET'])
def test():

    cur = conn.cursor()
    
    queryInput = """SELECT c_name, c_address 
                    FROM customer 
                    LEFT JOIN nation ON nation.n_nationkey=customer.c_nationkey 
                    LEFT JOIN region ON nation.n_regionkey=region.r_regionkey 
                    WHERE region.r_regionkey=1;"""
        
    queryPlan1 = """
    EXPLAIN (ANALYZE true, COSTS true, SETTINGS true, FORMAT JSON) {};
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

    # Query result
    # cur.execute(queryInput)
    # queryResult = cur.fetchall()
    # print(f"[-] Query results:")
    # # convert Decimal to string
    # # currently convert ther whole result instead of just the Decimal
    # json_str = json.dumps(queryResult, cls=DecimalEncoder)
    # print(queryResult)

    cur.close()

    return jsonify({"QueryPlan1": planResult1[0][0][0], "QueryPlan2": planResult2[0][0][0]})

@app.route('/hi', methods=['GET'])
def hi():
    return jsonify({"message": "Hello World!"})


if __name__ == '__main__':
    app.run(debug=True)