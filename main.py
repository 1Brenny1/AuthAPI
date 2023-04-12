import Utils, sqlite3
from flask import Flask, make_response, request

app = Flask(__name__)

DB = sqlite3.connect("Database.db")
DB.execute("""CREATE TABLE IF NOT EXISTS Tokens (
    Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    Token TEXT UNIQUE NOT NULL
)""")
DB.execute("""CREATE TABLE IF NOT EXISTS Auth (
    Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    Token TEXT UNIQUE NOT NULL,
    Label TEXT NOT NULL
)""")
DB.commit()
DB.close()

with open("Template.html", "r") as f:
    Template = f.read()

with open("AuthToken.html", "r") as f:
    AuthTokenTemplate = f.read()

Password = "Pass123"

@app.route("/login", methods=["POST", "GET"])
def login():
    Response = make_response()

    Token = request.cookies.get("Token")
    if Token != None:
        DB = sqlite3.connect("Database.db")
        TokenId = DB.execute(f"SELECT * FROM Tokens WHERE Token='{Token}'").fetchone()
        if TokenId != None:
            return "<script>location.href = '../'</script>"
    if request.method == "POST":
        if request.form.get("password") == Password:
            Token = Utils.GenToken()
            DB = sqlite3.connect("Database.db")
            DB.execute(f"""INSERT INTO Tokens(Token) VALUES('{Token}')""")
            DB.commit()
            DB.close()
            Response.set_cookie("Token", Token)
            Response.set_data("<script>location.href = '../'</script>")
            return Response
    
    with open("Login.html", "r") as f:
        Response.set_data(Utils.Format(Template, Content=f.read(), Title="Login"))
    return Response

@app.route("/", methods=['POST', 'GET'])
def index():
    Response = make_response()
    DB = sqlite3.connect("Database.db")

    Token = request.cookies.get("Token")
    if Token != None:
        TokenId = DB.execute(f"SELECT * FROM Tokens WHERE Token='{Token}'").fetchone()
        if TokenId == None:
            Response.set_data("<script>location.href = './login'</script>")
            Response.set_cookie("Token", "")
            return Response
    else:
        return "<script>location.href = './login'</script>"
    
    with open("Dashboard.html", "r") as f:
        Data = Utils.Format(Template, Title="Dashboard", Content=f.read())

    Alert = ""

    if request.method == "POST":
        Label = request.form.get("Label")
        if DB.execute(f"SELECT * FROM Auth WHERE Label='{Label}'").fetchone() == None:
            Token = Utils.GenToken()
            DB.execute(f"INSERT INTO Auth(Token, Label) VALUES('{Token}', '{Label}')")
            DB.commit()
            Alert = f"Token: {Token}"
        else:
            Alert = f"Token all ready exists with label '{Label}'"
    else:
        Delete = request.args.get("delete")
        if Delete != None:
            DB.execute(f"DELETE FROM Auth WHERE Id={Delete}")
            DB.commit()
            return "<script>location.href='/'</script>"

    AuthTokens = ""
    for Token in DB.execute("SELECT * FROM Auth").fetchall():
        AuthTokens += Utils.Format(AuthTokenTemplate, Id=Token[0], Label=Token[2], Token=Token[1])

    Response.set_data(Utils.Format(Data, Alert=Alert, AuthTokens=AuthTokens))
    return Response

@app.errorhandler(404)
def error404(e):
    return "<script>location.href='/'</script>"

@app.route("/auth/<token>")
def authToken(token):
    DB = sqlite3.connect("Database.db")
    TokenData = DB.execute(f"SELECT * FROM Auth WHERE Token='{token}'").fetchone()
    if TokenData != None:
        return "True"
    else:
        return "False"

app.run("localhost", 5000)