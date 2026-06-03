from flask import Flask, Blueprint, request, render_template, current_app
import pymysql as MySQLdb

app = Flask(__name__)

bp_routes = Blueprint('routes', __name__)

# database connection
connection = MySQLdb.connect(
    host="localhost",
    user="root",
    password="1236547890",
    database="mydatabase"
)

app.config['DB_CONN'] = connection


# -------------------------
# FUNCTIONS
# -------------------------

def login_user(email: str, password: str):

    connection = current_app.config['DB_CONN']
    cursor = connection.cursor()

    query = """
        SELECT * FROM users
        WHERE email = %s AND User_Password = %s
    """

    cursor.execute(query,(email, password))

    usuario = cursor.fetchone()

    cursor.close()

    return usuario

def insert_new_user(username: str, email: str, password: str):
    connection = current_app.config['DB_CONN']
    cursor = connection.cursor()
    query = "INSERT INTO users (User_Name, email, User_Password) VALUES (%s, %s, %s)"
    #usar bcript no futuro
        
    try:
        cursor.execute(query, (username, email, password))
        connection.commit()
        print("Usuário cadastrado com sucesso!")
        return True
        
    except Exception as e:
        connection.rollback()
        print(f"Erro ao cadastrar: {e}")
        return False
        
    finally:
        cursor.close()
# -------------------------
# ROUTES
# -------------------------

@bp_routes.route('/loginPage', methods=['GET', 'POST'])
def LoginPage():

    if request.method == "GET":
        return render_template("expocol.html")

    elif request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        usuario = login_user(email, password)

        if usuario:
            return render_template("expocol.html")

        return "Erro"

@bp_routes.route('/registerPage', methods=['POST'])
def RegisterPage():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    success = insert_new_user(username, email, password)

    if success:
        return "Cadastro realizado com sucesso!", 201
    else:
        return "Erro ao realizar cadastro. O e-mail ou o usuário podem já estar em uso.", 400
app.register_blueprint(bp_routes)

if __name__ == "__main__":
    app.run()