from flask import Flask,jsonify,request
from werkzeug.utils import secure_filename
from flask_cors import CORS
from model.expense import Expense,ExpenseSchema
from model.income import Income,IncomeSchema
from model.transaction_type import TransactionType
from access_resources import upload_blob,get_blob_container_client,access_database
import os

app=Flask(__name__)
transactions=[

    Income('Salary',5000),
    Income('Reward',1000),
    Expense('ChatGPT',80),
    Expense('Wifi',20)
]
ALLOWED_EXTENSIONS=set(['xls','csv','png','jpg','jpeg','pdf'])
UPLOAD_FOLDER=os.path.abspath(os.path.join(os.path.dirname(__file__),'downloads'))
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH']=500*1000*1000
app.config['CORS_HEADER'] ='application/json'
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def index():
    return "<h1>Hello People</h1>"
if __name__=='__main__':
    app.run()
@app.route('/incomes')
def get_incomes():
    schema=IncomeSchema(many=True)
    incomes=schema.dump(
        filter(lambda t:t.type==TransactionType.INCOME,transactions)
    )
    return jsonify(incomes)

@app.route('/incomes',methods=['POST'])
def add_income():
    income=IncomeSchema().load(request.get_json())
    transactions.append(income)
    return '',204
@app.route('/expenses')
def get_expenses():
    schema=ExpenseSchema(many=True)
    expenses=schema.dump(
        filter(lambda t:t.type==TransactionType.EXPENSE,transactions)
    )
    return jsonify(expenses)
@app.route('/expenses',methods=['POST'])
def add_expense():
    expense=ExpenseSchema().load(request.get_json())
    transactions.append(expense)
    return '',204

@app.route('/upload',methods=['POST','GET'])
def upload_file():
    if request.method=='POST':
        file=request.files.getlist('files')
        filename=""
        print("Request Files :\n",request.files,"... \n")
        for f in file:
            print(f.filename)
            filename=secure_filename(f.filename)
            print(allowed_file(filename))
            if(allowed_file(filename)):
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                get_blob_container_client(container_name=os.environ['AZURE_STORAGE_CONTAINER']).upload_blob(name=filename,data=f.stream.read())
            else:
                return jsonify({'message':"File type not allowed"}),400
        return jsonify({'message':filename,'status':"Success"})
    return jsonify({'status':"API upload GET request running"})
@app.route('/database',methods=['GET'])
def get_data():
    results=access_database()
    return jsonify({"message":results,"status":"Successful"})
if __name__=="__main__":
    app.run(debug=True)
    