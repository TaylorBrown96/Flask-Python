# Add imports here

app = Flask(__name__)
#Add a secret key

@app.route("/")
def index():
    pass
    

@app.route("/Login")
def userLogin():
    '''
        Important variable names (case sensitive):
            username
            password
    '''
    pass
    

@app.route("/Signout")
def signout():
    pass
    

@app.route("/Signup")
def signup():
    pass

###################################### METHODS ######################################
def createSession():
    pass     


if __name__ == "__main__":
    app.run(debug=True)
