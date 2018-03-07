from flask import Flask, request
app = Flask(__name__)

def sub():
    return 4


def util():
    a = sub()
    return a


@app.route("/", methods=['GET', 'POST', 'DELETE'])
def hello():
    print("====================================")
    print(request.query_string)
    for key in request.values:
        print("%s = %s" % (key, request.values[key]))
    util()
    if 'vads_identifier' in request.values:
        print("token=%s" % request.values['vads_identifier'])
    if 'vads_amount' in request.values:
        print("vads_amount=%s" % request.values['vads_amount'])
        
    return "you're welcome"
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)