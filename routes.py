from flask import Blueprint,request, jsonify,current_app
from service.comptabilisation import pvgComptabilisationVersement
from models.models import clsObjetEnvoi
from utils import connect_database
from config import MYSQL_REPONSE
api_bp = Blueprint('api', __name__)

@api_bp.route('/pvgAjouterComptabilisation', methods=['POST'])
def OperationVersementRetrait():
    # Récupérer les données du corps de la requête
    
    request_data = request.json
    # Extraire les données nécessaires pour l'appel à la fonction
    Objet = request_data['Objet']
   # billetages = request_data['Objet']['clsBilletages']
   
    clsEtatmouvementacomptabiliserss = []
    clsBilletagess = []
    
   # clsObjetEnvoi.OE_A = request_data['Objet'].clsObjetEnvoi.OE_A
   ## clsObjetEnvoi.OE_Y = request_data['Objet'].clsObjetEnvoi.OE_Y
    
    for row in request_data['Objet']:
        clsEtatmouvementacomptabilisers = {}
        clsObjetEnvoi.OE_A = row['clsObjetEnvoi']['OE_A']
        clsObjetEnvoi.OE_Y = row['clsObjetEnvoi']['OE_Y']
        clsObjetEnvoi.OE_J = row['clsObjetEnvoi']['OE_J']
        clsObjetEnvoi.OE_U = row['clsObjetEnvoi']['OE_U']
        clsObjetEnvoi.OE_G = row['clsObjetEnvoi']['OE_G']
        clsObjetEnvoi.OE_T = row['clsObjetEnvoi']['OE_T']
        clsEtatmouvementacomptabilisers['AG_CODEAGENCE'] = row['AG_CODEAGENCE']
        clsEtatmouvementacomptabilisers['CO_CODECOMPTE'] = row['CO_CODECOMPTE1']
        clsEtatmouvementacomptabilisers['MC_DATEPIECE'] = row['MC_DATEPIECE']
        clsEtatmouvementacomptabilisers['MC_LIBELLEOPERATION'] = row['MC_LIBELLEOPERATION']
        clsEtatmouvementacomptabilisers['MC_MONTANTDEBIT'] = row['MC_MONTANTDEBIT']
       # clsEtatmouvementacomptabilisers['EM_NOMOBJET'] = row['EM_NOMOBJET']
       # clsEtatmouvementacomptabilisers['EM_NUMEROSEQUENCE'] = row['EM_NUMEROSEQUENCE']
        clsEtatmouvementacomptabilisers['MC_NUMPIECETIERS'] = row['MC_NUMPIECE']
        clsEtatmouvementacomptabilisers['MC_REFERENCEPIECE'] = row['MC_REFERENCEPIECE']
       # clsEtatmouvementacomptabilisers['EM_SCHEMACOMPTABLECODE'] = row['EM_SCHEMACOMPTABLECODE']
        clsEtatmouvementacomptabilisers['MC_SENSBILLETAGE'] = row['MC_SENSBILLETAGE']
        clsEtatmouvementacomptabilisers['TI_IDTIERS'] = row['TI_IDTIERS']
        clsEtatmouvementacomptabilisers['OP_CODEOPERATEUR'] = row['OP_CODEOPERATEUR']
        clsEtatmouvementacomptabilisers['PI_CODEPIECE'] = row['PI_CODEPIECE']
        clsEtatmouvementacomptabilisers['PL_CODENUMCOMPTE'] = row['PL_CODENUMCOMPTE']
        clsEtatmouvementacomptabilisers['PV_CODEPOINTVENTE'] = row['PV_CODEPOINTVENTE']
        clsEtatmouvementacomptabilisers['MC_TERMINAL'] = ""
        clsEtatmouvementacomptabilisers['TS_CODETYPESCHEMACOMPTABLE'] = row['TS_CODETYPESCHEMACOMPTABLE']
        clsEtatmouvementacomptabiliserss.append(clsEtatmouvementacomptabilisers)
    
    # Parcourir les éléments de la liste Objet
    for objet in request_data['Objet']:
        # Vérifier si l'élément contient la clé 'clsBilletages'
        if 'clsBilletages' in objet:
            # Récupérer la liste des billetages
            billetages = objet['clsBilletages']

            # Parcourir les billetages en utilisant une boucle for
            if billetages is not None:
                for row in billetages:
                    clsBilletages = {}
                    clsBilletages['AG_CODEAGENCE'] = row['AG_CODEAGENCE']
                    clsBilletages['BI_NUMPIECE'] = row['BI_NUMPIECE']
                    clsBilletages['BI_NUMSEQUENCE'] = row['BI_NUMSEQUENCE']
                    clsBilletages['BI_NUMSEQUENCE'] = row['BI_NUMSEQUENCE']
                    clsBilletages['BI_QUANTITEENTREE'] = row['BI_QUANTITEENTREE']
                    clsBilletages['BI_QUANTITESORTIE'] = row['BI_QUANTITESORTIE']
                    clsBilletages['CB_CODECOUPURE'] = row['CB_CODECOUPURE']
                    clsBilletages['MC_DATEPIECE'] = row['MC_DATEPIECE']
                    clsBilletages['MC_NUMPIECE'] = row['MC_NUMPIECE']
                    clsBilletages['MC_NUMSEQUENCE'] = row['MC_NUMSEQUENCE']
                    clsBilletages['PL_CODENUMCOMPTE'] = row['PL_CODENUMCOMPTE']
                    clsBilletages['TYPEOPERATION'] = row['TYPEOPERATION']
                    clsBilletagess.append(clsBilletages)
    
   
    # Récupérer la connexion à la base de données depuis current_app
   # db_connection = current_app.db_connection
    
   # db_connection.begin()
    #try:
        db_connection = connect_database()
        db_connection = db_connection.cursor()
        db_connection.execute("BEGIN TRANSACTION")
        #db_connection.begin()
         # Appeler la fonction avec les données récupérées
        response = pvgComptabilisationVersement(db_connection, clsEtatmouvementacomptabiliserss, clsBilletagess, clsObjetEnvoi)
        
        # Retourner la réponse au client
        if response['SL_RESULTAT'] == "TRUE":
            #db_connection.close()
            return jsonify({"NUMEROBORDEREAUREGLEMENT":str(response['NUMEROBORDEREAU']),"SL_MESSAGE":"Comptabilisation éffectuée avec success !!! / " + response['MESSAGEAPI'] ,"SL_RESULTAT": 'TRUE'}) 
        else:
            #db_connection.close()
            return jsonify({"SL_MESSAGE":response['SL_MESSAGE'] ,"SL_RESULTAT": 'FALSE'}) 
    #except Exception as e:
       # En cas d'erreur, annuler la transaction
        #db_connection.execute("ROLLBACK")
        #db_connection.close()
        #return jsonify({"SL_MESSAGE":str(e),"SL_RESULTAT": 'FALSE'})
        #return jsonify({"SL_MESSAGE":str(e),"SL_RESULTAT": 'FALSE'})    