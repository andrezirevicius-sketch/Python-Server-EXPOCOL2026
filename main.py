from flask import Flask, Blueprint, request, render_template, current_app
import pymysql as MySQLdb
import os
from dotenv import load_dotenv

load_dotenv('passwords.env')

envhost: str = os.getenv('host', '')
envuser: str = os.getenv('user', '')
envpassword: str | bytes  = os.getenv('password', '')
envdatabase: str | bytes = os.getenv('database', '')

app = Flask(__name__)

bp_routes = Blueprint('routes', __name__)

# database connection
connection = MySQLdb.connect(
    host=envhost,
    user=envuser,
    password=envpassword,
    database=envdatabase
)

app.config['DB_CONN'] = connection


# -------------------------
# FUNCTIONS
# -------------------------

def login_user(email: str | None, password: str | None):

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

def insert_new_user(username: str | None, email: str | None, password: str | None):
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

@bp_routes.route('/', methods=['GET'])
def homePage():
    return render_template('home.html')
@bp_routes.route('/loginPage', methods=['GET', 'POST'])
def loginPage():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form.get("email")
    password = request.form.get("password")
    if not email or not password:
        return "Campos vazios!!"
    usuario = login_user(email, password)

    if usuario:
        return "Login efetuado", 201

    return "Erro", 400

@bp_routes.route('/registerPage', methods=['POST', 'GET'])
def registerPage():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    if not email or not password or not username:
        return "Campos vazios!!"
    register_success = insert_new_user(username, email, password)

    if register_success:
        return "Cadastro realizado com sucesso!", 201
    else:
        return "Erro ao realizar cadastro. O e-mail ou o usuário podem já estar em uso.", 400
app.register_blueprint(bp_routes)

if __name__ == "__main__":
    app.run()