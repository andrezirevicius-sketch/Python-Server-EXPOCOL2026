from flask import Flask, Blueprint, request, render_template, current_app, flash, redirect, url_for
import pymysql as MySQLdb
import os
from dotenv import load_dotenv

#Variáveis ambiente
load_dotenv('passwords.env')

envsecret_key: str = os.getenv('secret_key', 'testkey')
envhost: str = os.getenv('host', '')
envuser: str = os.getenv('user', '')
envpassword: str | bytes  = os.getenv('password', '')
envdatabase: str | bytes = os.getenv('database', '')

app = Flask(__name__)
app.secret_key = envsecret_key #requisito para o flash

bp_routes = Blueprint('routes', __name__)

#Conexão com o database
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
        flash("Campos vazios!!", "warning")
        return render_template('login.html')
    
    usuario = login_user(email, password)
    
    if usuario:
        flash("Login efetuado com sucesso!", "success")
        return redirect(url_for('routes.homePage'))
    
    flash("Erro: Usuário ou senha incorretos.", "danger")
    return render_template('login.html')  
@bp_routes.route('/registerPage', methods=['GET', 'POST'])
def registerPage():
    if request.method == 'GET':
        return render_template('register.html')
    
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    
    if not email or not password or not username:
        flash("Campos vazios!!")
        return render_template('register.html')
    register_success = insert_new_user(username, email, password)

    if register_success:
        flash("Cadastro realizado com sucesso!")
        return redirect(url_for('routes.homePage'))
    else:
        flash("Erro ao realizar cadastro. O e-mail ou o usuário podem já estar em uso.", "danger")
        return render_template('register.html')
    
app.register_blueprint(bp_routes)

if __name__ == "__main__":
    app.run()