from flask import Flask, session, render_template, request, redirect, url_for
#Add appropriate imports

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
    pass


@app.route("/Post", methods=['POST','GET'])
def addPost():
    pass


###################################### METHODS ######################################
def createSession(username, password):
    pass
      

def populatePosts():
    pass

if __name__ == "__main__":
    app.run(debug=True)
