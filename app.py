from flask import Flask,jsonify,request,render_template
from flask_cors import CORS
from utils import connect_database
import logging as logger
logger.basicConfig(level="DEBUG")
from routes import api_bp

app = Flask(__name__)
CORS(app)

# Connexion à la base de données au démarrage de l'application Flask
#@app.teardown_appcontext

#def connect_to_database(exception):
    #global db_connection
    #db_connection = connect_database()

    #if not db_connection:
        # Si la connexion échoue, vous pouvez prendre des mesures appropriées, par exemple, arrêter l'application
    #print("Impossible de se connecter à la base de données. Arrêt de l'application.")
    #    exit(1)

# Exemple de route pour tester la connexion à la base de données

@app.route('/')
def hello():
    #global db_connection
    
    #cursor = db_connection.cursor()
    #insert_query = "INSERT INTO TABLEINSERTION (IDTABLEINSET, LIBELLETABLEINSET) VALUES (3,'euloge')"
    #cursor.execute(insert_query)
    # Exécuter une requête SQL
    # cursor.execute('SELECT * FROM SOCIETE') 

    # Récupérer les résultats de la requête
    # rows = cursor.fetchall()
    # Exécution de la commande
    #db_connection.commit()
    # Fermer la connexion à la base de données
    #db_connection.close()
    #return 'ok'
    return render_template('home.html')


# Enregistrer le blueprint API
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)
    #app.run(debug=True)