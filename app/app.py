
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

nodeTypeList = []

def getAllNodeType(queryPlan): 
    nodeTypeList.append(queryPlan.get("Node Type"))
    
    if queryPlan.get("Plans") != None:
        for plan in queryPlan.get("Plans"):
            getAllNodeType(plan)
    return 

def getImptPlanDetails(queryPlan): 
    interResult ={"text" : ""}
    
    # get all key:value pair with string value
    for attr, value in queryPlan.items():
        if (isinstance(value, str)):
            if( attr.find("Alias") == -1 
                & attr.find("Parent") == -1 
                    & attr.find("Direction") == -1):
                interResult["text"] += value + " "
    
    # remove last space from string
    interResult["text"] = interResult["text"][:-1]
    
    childrenDetails = []
     
    if queryPlan.get("Plans") != None:
        for plan in queryPlan.get("Plans"):
            childrenDetails.append(getImptPlanDetails(plan))
    
    if len(childrenDetails) != 0:
        interResult["children"] = childrenDetails
    
    # dict(sorted(interResult.items(), key=lambda interResult: interResult[1]))
    
    return interResult



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

def getAltQueryPlan(queryPlan, queryResult, cur):
    
    # Get all node type from Query Plan Result
    getAllNodeType(queryResult[0][0][0].get("Plan"))
    
    queryConfigParamList = []
    
    # Get list of query config settings parameters
    for nodeType in nodeTypeList:
        queryConfigParamList.append(queryPlanConfigParam(nodeType))
        
    # Remove None from list
    filteredQueryConfigParamList = list(filter(lambda x: x != None, queryConfigParamList))
     
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

@app.route('/getPlan', methods=['POST'])
def getPlan():
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

if __name__ == '__main__':
    app.run(debug=True)