from flask import Flask, jsonify, request


app = Flask(__name__) 

from data import df as csvdata

# Represent data by default
@app.route('/index/') 
def index():
    '''
        Method that displays data on screen ( browser) as a JSON document.

        @returns A JSON document
    '''
    prod_json = csvdata.to_dict(orient= 'records')
    return jsonify({"Products": prod_json})

#GET data product by ID
@app.route('/products/product_id/<id>') 
def getById(id):
     '''
        Method that displays a specific product data found by ID on screen 

        @param - Passed from URL 
            -id : ID of product 
        @returns A JSON document with the product.  If not found a message is returned instead
    '''
    id = int(id)
    idx = csvdata[csvdata['id'] == id].index
    product =csvdata.ix[idx]
    if not product.empty :
        prod_json = product.to_dict(orient= 'records')
        return jsonify({"product": prod_json})

    return jsonify({"message":"Not found product with id {}".format(id)})

#GET data product by name 
@app.route('/products/product_name/<name>') 
def getByName(name):
     '''
        Method that displays a specific product data found by name on screen 

        @param - Passed from URL 
            -name : name of product 
        @returns A JSON document with the product. If not found a message is returned instead
    '''
    idx = csvdata[csvdata['name'] == name].index
    product =csvdata.ix[idx]
    if not product.empty :
        prod_json = product.to_dict(orient= 'records')
        return jsonify({"product": prod_json})

    return jsonify({"message":"Not found product with name {}".format(name)})

# GET data product by type-> value
@app.route('/products/<string:type>/<value>') 
def getByTypeValue(type,value):
    '''
        Method that displays specific product/prodcuts data found by type>value on screen 

        @param - Passed from URL 
            -type : Type to search for the value. Example : color, name, ID.
            -value : Value itself corresponding to that type. Example : blue, laptop, 15
        @returns A JSON document with the product/s. If not found a message is returned instead
    '''
    print(csvdata.head(5))
    if type == 'id': # ID search 
        value = int(value)
    idx = csvdata[csvdata[type] == value].index
    product =csvdata.ix[idx]
    if not product.empty :
        prod_json = product.to_dict(orient= 'records')
        return jsonify({"product": prod_json})

    return jsonify({"message":"Not found product with {} {}".format(type,value)})

# POST new data into the database
@app.route('/products/add/', methods=['POST']) 
def addProduct():
    '''
        Method that adds specific product to database (internally)

        ********     The .csv is never modified     ********

        The request has to contain a JSON with the information of new product.
        @returns A JSON document with the all the products including the new one. 
    '''
    
    global csvdata # Tells function csvdata is a GLOBAL VARIABLE ! 
    
    id = request.json['id']
    idx = csvdata[csvdata['id'] == id].index
    product =csvdata.ix[idx]
    msg_warning = ""
    
    if not product.empty: # In case ID already exists.
        id = csvdata['id'].max() + 1 # Possible solution.
        msg_warning = "Warning :  Product ID changed from {} to {}".format(request.json['id'],id)
        
    # Append product to database
    new_product = { 'id' : id,'name':request.json['name'],'price': request.json['price'],'quantity' : request.json['quantity'],'color':request.json['color'],'unique':request.json['unique'],'city' : request.json['city']} 
    csvdata =  csvdata.append(new_product,ignore_index=True)
    prod_json = csvdata.to_dict(orient= 'records')

    msg = " Product {} added correctly".format(id)
    if msg_warning :
        return jsonify({"message" : msg, "warning": msg_warning, "products": prod_json})
    return jsonify({"message" : msg, "products": prod_json})

#PUT new data to already existing data
@app.route('/products/edit/<int:id_prod>/', methods=['PUT'])
def editProduct(id_prod):
    '''
        Method that EDITS an specific product via ID 

        ********     The .csv is never modified     ********

        The request has to contain a JSON with the information of new information product.
        IMPORTANT : the ID is not modified in this method.

        @paramenter:
            - id_prod : ID of product to be modified. 
        @returns A JSON document with the the modified product. 
    '''
    idx = csvdata[csvdata['id'] == id_prod].index
    product =csvdata.ix[idx]

    if not product.empty:

        for property in request.get_json(): # Get every property to be changed 
            if property != "id":
                csvdata.loc[idx,property] = request.json[property] # Property edit

        prod_json = csvdata.loc[idx].to_dict(orient= 'records')
        return jsonify({"message": "Product with ID {} changed successfully".format(id_prod),"Product":prod_json})
    
    return jsonify({"message" : "WARNING! Product with ID {} is not in the database!".format(id_prod)})
    
#DELETE data from database
@app.route('/products/delete/<int:id_prod>/', methods=['DELETE'])
def deleteProduct(id_prod):
    '''
        Method that DELETES a specific product via ID 

        ********     The .csv is never modified     ********

        @paramenter:
            - id_prod : ID of product to be deleted. 
        @returns A JSON document with the database. If not found a message is returned instead 
    '''
    global csvdata 

    idx = csvdata[csvdata['id'] == id_prod].index
    product =csvdata.ix[idx]

    if not product.empty:
        prod_json = csvdata.loc[idx].to_dict(orient= 'records')
        csvdata = csvdata.drop(csvdata.index[idx])
        csvdata = csvdata.reset_index(drop=True)
        return jsonify({"message": "Product with ID {} deleted successfully".format(id_prod),"Product":prod_json})
    
    return jsonify({"message" : "WARNING! Product with ID {} is not in the database!".format(id_prod)})
    
if __name__  == '__main__':
    app.run(debug= True, port = 5000)