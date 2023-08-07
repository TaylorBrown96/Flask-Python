from flask import Flask, session, render_template, request, redirect, url_for
import csv

app = Flask(__name__)
app.secret_key = "Its a secret duh"

@app.route("/", methods=['GET','POST'])
def index():
    if 'username' in session:
        return render_template("index.html")
    else:
        return redirect(url_for('userLogin'))
    

@app.route("/Login", methods=['POST','GET'])
def userLogin():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        createSession(username, password)
        return redirect(url_for('index'))  
    else:
        return render_template("login.html")
    

@app.route("/Signout")
def signout():
    if "username" in session:
        session.pop("USID", None)
        session.pop("username", None)
        session.pop("accountType", None)
        return redirect(url_for("userLogin"))
    else:
        return redirect(url_for("userLogin"))
    

@app.route("/Signup", methods=['POST','GET'])
def signup():
    return render_template("signup.html")

###################################### METHODS ######################################
def createSession(username, password):
    with open("Users.csv", "r") as file:
        csvReader = csv.reader(file)
        
        users = []
        passwords = []
        accountType = []

        for row in csvReader:
            users.append(row[0].lower())
            passwords.append(row[1])
            accountType.append(row[2])

        if username in users:
            if password == passwords[users.index(username)]:
                session['username'] = username
                session['accountType'] = accountType[users.index(username)]
                return 
            else:
                print('fail password')
                return 
        else:
            print('fail username')
            return        


if __name__ == "__main__":
    app.run(debug=True)
