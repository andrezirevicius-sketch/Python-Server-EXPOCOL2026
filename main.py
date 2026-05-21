import MySQLdb
from flask import Flask, Blueprint, request
from flask import current_app

app = Flask(__name__)

#bancão de dados MySQL, configurado para aplicação
connection = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="1236547890", #isso n pode ficar aqui, é pireculoso.
    db="mydatabase"
)

app.config['DB_CONN'] = connection

bp_routes = Blueprint('routes', __name__)

def search_user_data(column, data):
    # segurança básica
    allowed_columns = ["email", "id", "User_Name", "User_Password"]
    if column not in allowed_columns:
        return None
    connection = current_app.config['DB_CONN']
    cursor = connection.cursor()
    query = f"SELECT * FROM users WHERE {column} = %s"
    cursor.execute(query, (data,))
    usuario = cursor.fetchone()
    cursor.close()
    return usuario

def insert_new_user(username, email, password):
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

@bp_routes.route('/loginPage', methods=['GET', 'POST'])
def LoginPage():

    if request.method == "GET":
        return "Página de login"
    #pega da web
    email = request.form.get("email")
    password = request.form.get("password")
    #pega do banco de dados
    Email_usuario = search_user_data("email", email)
    Password_usuario = search_user_data("User_Password", password)

    if Email_usuario and Password_usuario:
        return "Login OK"

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
        return "Erro ao realizar cadastro. O e-mail já pode estar em uso.", 400

app.register_blueprint(bp_routes)

if __name__ == "__main__":
    app.run(debug=True)     
