from flask import Flask, session, render_template, request, redirect, url_for
from markupsafe import Markup
from dotenv import load_dotenv
import sqlite3
import datetime
import bcrypt
import os
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/", methods=['GET','POST'])
def index():
    if 'username' in session:
        posts,modals = populatePosts()
        return render_template("index.html", posts = posts, modals=modals)
    else:
        return redirect(url_for('userLogin'))
    

@app.route("/Login", methods=['POST','GET'])
def userLogin():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        result = createSession(username, password) 

        print(result)
        if result == False:
            modal = populateErrorModal("The password or email you have entered is incorrect")
            return render_template("login.html", modal=modal) 
        else:
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
        cursor = connection.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        row = cursor.fetchone()
        connection.close
        
        if row != None:
            modal = populateErrorModal("The username you choose is already taken")
            return render_template("signup.html", modal=modal)

        verified = passwordSecurityCheck(password)
        if verified == False:
            modal = populateErrorModal("Password doesn't contain an uppercase, lowercase, and a symbol.")
            return render_template("signup.html", modal=modal)
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) # Default passes is 12 prefix is 2b

        connection = sqlite3.connect('Website_DB.db')
        connection.execute("INSERT INTO Users (Username, Title, Password) VALUES (?,?,?)", (username, title, hashed,))
        connection.commit()
        connection.close()

        return redirect(url_for('index'))
    else:
        return render_template("signup.html")


@app.route("/Post", methods=['POST','GET'])
def addPost():
    if request.method == 'POST':
        USID = session['USID']
        text = request.form['postText']
        time = datetime.datetime.now().strftime("%x %X")

        connection = sqlite3.connect('Website_DB.db')
        connection.execute("INSERT INTO Posts VALUES(NULL,?,?,?,?)", (str(USID), text, time, 0,))
        connection.commit()
        connection.close()
        
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))  
    

@app.route("/UpdatePost", methods=['POST','GET'])
def updatePost():
    if request.method == "POST":
        postID = request.form['custId']
        update = request.form['postText']

        connection = sqlite3.connect('Website_DB.db')
        connection.execute("UPDATE Posts SET PostContent = ? WHERE PID = ?", (update, postID))
        connection.commit()
        connection.close()
        return redirect(url_for('index'))  
    else:
        return redirect(url_for('index'))  


@app.route("/DeletePost", methods=['POST','GET'])
def deletePost():
    if request.method == "POST":
        postID = request.form['custId']

        connection = sqlite3.connect('Website_DB.db')
        connection.execute("DELETE FROM Posts WHERE PID = ?", (postID,))
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
        connection.close()

        dbpass = row[4]

        if bcrypt.checkpw(password.encode('utf-8'), dbpass):
            session['USID'] = row[0]
            session['username'] = row[1]
            session['profilePicture'] = row[2]
            session['title'] = row[3]
            session['accountType'] = row[5]
            session['likedPosts'] = row[6]
            return True
        else:
            return False
    except:
        return False 
      

def populatePosts():
    connection = sqlite3.connect('Website_DB.db')
    postCursor = connection.execute("SELECT * from Posts ORDER BY PID DESC LIMIT 12")

    posts = ""
    modals = ""

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
                        """) 
        if user[1] == session['username']:
            posts += Markup("""
                                        <button class="btn btn-primary" type="button" data-bs-target="#edit"""+ str(row[0]) +"""" data-bs-toggle="modal" style="margin-right: 0px;margin-bottom: 14px;padding-right: 16px;padding-left: 16px;margin-left: 304px;padding-bottom: 10.6px;margin-top: -62px;background: var(--bs-warning);border-color: var(--bs-emphasis-color);">
                                            <i class="fa fa-pencil-square-o" aria-hidden="true"></i>
                                        </button>
                                        <button class="btn btn-primary" type="button" data-bs-target="#delete"""+ str(row[0]) +"""" data-bs-toggle="modal" style="margin-right: 0px;margin-bottom: 17px;padding-right: 16px;padding-left: 16px;margin-left: 355px;padding-bottom: 10.6px;margin-top: -62px;background: var(--bs-red);border-color: var(--bs-emphasis-color);">
                                            <i class="fa fa-times-circle" aria-hidden="true"></i>
                                        </button>
                                    </div>
                                </div>
                            """)
            modals += Markup("""
                                <form method="POST" action="/UpdatePost">
                                    <div class="modal fade" role="dialog" tabindex="-1" id="edit"""+ str(row[0]) +"""">
                                        <div class="modal-dialog" role="document">
                                            <div class="modal-content">
                                                <div class="modal-header">
                                                    <h4 class="modal-title">Update Post</h4><button class="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal"></button>
                                                </div>
                                                <input type="hidden" id="custId" name="custId" value="""+ str(row[0]) +""">
                                                <div class="modal-body"><textarea name="postText" style="height: 150px;width: 100%;border-radius: 6px;padding: 10px;">"""+ str(row[2]) +"""</textarea></div>
                                                <div class="modal-footer"><button class="btn btn-light" type="button" data-bs-dismiss="modal">Close</button><button class="btn btn-primary" type="submit">Update</button></div>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                                <form method="POST" action="/DeletePost">
                                    <div class="modal fade" role="dialog" tabindex="-1" id="delete"""+ str(row[0]) +"""">
                                        <div class="modal-dialog" role="document">
                                            <div class="modal-content">
                                                <div class="modal-header">
                                                    <h4 class="modal-title">Delete Post</h4><button class="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal"></button>
                                                </div>
                                                <div class="modal-body">
                                                <input type="hidden" id="custId" name="custId" value="""+ str(row[0]) +""">
                                                    <p>Are you sure you want to delete this post?</p>
                                                </div>
                                                <div class="modal-footer"><button class="btn btn-light" type="button" data-bs-dismiss="modal">Cancel</button><button class="btn btn-primary" type="submit" style="background: var(--bs-danger);">Delete</button></div>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            """)
        else:
            posts += Markup("""
                                    </div>
                                </div>
                            """)
    
    connection.close()
    return posts,modals


def populateErrorModal(message):
    modal = Markup("""
                    <div class="modal fade" role="dialog" id="errorModal">
                            <div class="modal-dialog" role="document">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h4 class="modal-title">Oh No!</h4>
                                            <form>
                                                <button class="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal" onclick="history.back()"></button>
                                            </form>
                                    </div>
                                    <div class="modal-body">
                                        <p>"""+ message +"""</p>
                                    </div>
                                    <div class="modal-footer">
                                    <form>
                                        <button class="btn btn-light" type="button" data-bs-dismiss="modal" onclick="history.back()">Close</button>
                                    </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    """)
    return modal


def passwordSecurityCheck(password):
    """
        This method checks the passed variable to see if it is greater 
        than 6 characters long has an uppercase letter a 
        lowercase letter and a symbol.
    """
    result = False

    # Checks length
    if len(password) < 6:
        result = False 
    
    # Checks for uppercase
    for char in password:
        if char.isupper():
            result = True
            break
        else:
            result = False

    # Checks for lowercase    
    for char in password:
        if char.islower():
            result = True
            break
        else:
            result = False
        
    regex = re.compile('[-@_!#$%^&*()<>?/\|}{~:]')
    
    # Checks for a symbol
    if(regex.search(password) != None):
        result = True
    else:
        result = False
        
    return result


if __name__ == "__main__":
    app.run(debug=True)
