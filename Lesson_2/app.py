from flask import Flask, session, render_template, request, redirect, url_for
from markupsafe import Markup
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = "Its a secret duh"

@app.route("/", methods=['GET','POST'])
def index():
    if 'username' in session:
        posts = populatePosts()
        return render_template("index.html", posts = posts)
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
        session.pop("profilePicture", None)
        session.pop("title", None)
        session.pop("accountType", None)
        session.pop("likedPosts", None)
        return redirect(url_for("userLogin"))
    else:
        return redirect(url_for("userLogin"))
    

@app.route("/Signup", methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        title = request.form['title']
        password = request.form['password']

        connection = sqlite3.connect('Website_DB.db')
        connection.execute("INSERT INTO Users (Username, Title, Password) VALUES (?,?,?)", (username, title, password,))
        connection.commit()
        connection.close()

        return redirect(url_for('index'))
    else:
        return render_template("signup.html")


@app.route("/Post", methods=['POST','GET'])
def addPost():
    if request.method == 'POST':
        connection = sqlite3.connect('Website_DB.db')

        USID = session['USID']
        text = request.form['postText']
        time = datetime.datetime.now().strftime("%x %X")

        connection.execute("INSERT INTO Posts VALUES(NULL,?,?,?,?)", (str(USID), text, time, 0,))
        connection.commit()
        connection.close()
        
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))  


###################################### METHODS ######################################
def createSession(username, password):
    connection = sqlite3.connect('Website_DB.db')
    try:
        cursor = connection.execute("SELECT * FROM Users WHERE LOWER(Username) = ?", (username,))
        row = cursor.fetchone()
        
        if password == row[4]:
            session['USID'] = row[0]
            session['username'] = row[1]
            session['profilePicture'] = row[2]
            session['title'] = row[3]
            session['accountType'] = row[5]
            session['likedPosts'] = row[6]
        
        connection.close()
        return True
    except:
        connection.close()
        return False    
      

def populatePosts():
    connection = sqlite3.connect('Website_DB.db')
    postCursor = connection.execute("SELECT * from Posts ORDER BY PID DESC LIMIT 12")

    posts = ""

    for row in postCursor:
        cursor = connection.execute("Select USID, Username, ProfilePicture, title FROM Users WHERE USID = ?", (row[1],))
        user = cursor.fetchone()

        posts += Markup( """
                            <div class="col mb-4">
                                <div class="d-flex flex-column align-items-center align-items-sm-start" style="background: #27262e;border-radius: 16px;">
                                    <div class="d-flex" style="padding: 0px;padding-bottom: 0px;padding-left: 25px;padding-top: 16px;">
                                        <img class="rounded-circle flex-shrink-0 me-3 fit-cover" width="50" height="50" src="static/team/"""+ user[2] +""" ">
                                        <div>
                                            <p class="fw-bold text-primary mb-0">"""+ user[1] +"""</p>
                                            <p class="text-muted mb-0">"""+ user[3] +"""</p>
                                        </div>
                                    </div>

                                    <p class="bg-dark border rounded border-dark p-4" style="margin-bottom: 0px;">"""+ row[2] +"""</p>

                                    <div style="padding-left: 21px;padding-bottom: 0px;margin-bottom: -23px;">
                                        <button href="" class="btn btn-primary" type="button" style="padding-right: 16px;padding-left: 16px;">
                                            <i class="fa fa-thumbs-o-up" aria-hidden="true"></i>
                                        </button>
                                        <p style="margin-bottom: 16px;transform: translateX(57px) translateY(-34px);">"""+ row[4] +""" Likes</p>
                                    </div>
                                </div>
                            </div>
                        """) 
    
    connection.close()
    return posts


if __name__ == "__main__":
    app.run(debug=True)
