from flask import Blueprint, request, jsonify
import pyodbc
import datetime
from datetime import datetime
from typing import List
import json
import requests
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
#import pyodbc
import sys
sys.path.append("../")
from config import MYSQL_REPONSE,LIENAPISMS
import threading

class clsMouvementcomptable:
    def __init__(self):
        self.AG_CODEAGENCE = ''
        self.MC_DATEPIECE = '01/01/1900'
        self.MC_NUMPIECE = ''
        self.MC_NUMSEQUENCE = 0
        self.NUMEROBORDEREAU = ''
        self.PL_CODENUMCOMPTE = ''
class clsAgence:
    def __init__(self):
        self.SO_CODESOCIETE = ''
        self.AG_AGENCECODE = ''
        self.VL_CODEVILLE = ''
        self.AG_RAISONSOCIAL = ''
        self.AG_BOITEPOSTAL = ''
        self.AG_ADRESSEGEOGRAPHIQUE = ''
        self.AG_TELEPHONE = ''
        self.AG_FAX = ''
        self.AG_EMAIL = ''
        self.AG_NUMEROAGREMENT = ''
        self.AG_REFERENCE = ''
        self.AG_DATECREATION = ''
        self.AG_ACTIF = ''
        self.OP_CODEOPERATEUR = ''
class clsSmsout:
    def __init__(self):
        self.SL_RESULTAT = ''
        self.SL_MESSAGE = ''
        self.SM_TELEPHONE = ''
        self.SM_MESSAGE = ''
        self.SM_DATEPIECE = ''
        self.SM_NUMSEQUENCE = ''
class clsParams:
    def __init__(self):
        self.LibelleMouchard = ""
        self.LibelleEcran = ""
        self.LG_CODELANGUE = "FR"
        self.SL_LIBELLE1 = ""
        self.SL_LIBELLE2 = ""
        self.CO_CODECOMPTE = ""
        self.LO_LOGICIEL = "1"
        self.OB_NOMOBJET = ""
        self.SL_VALEURRETOURS = ""
        self.INDICATIF = ""
        self.RECIPIENTPHONE = ""
        self.PV_CODEPOINTVENTE = ""
        self.CodeOperateur = ""
        self.SM_DATEPIECE = ""
        self.SM_RAISONNONENVOISMS = ""
        self.TYPEOPERATION = ""
        self.SMSTEXT = ""
        self.MB_IDTIERS = ""
        self.EJ_IDEPARGNANTJOURNALIER = ""
        self.CL_IDCLIENT = ""
        self.TE_CODESMSTYPEOPERATION = ""
        self.SM_NUMSEQUENCE = ""
        self.SM_DATEEMISSIONSMS = ""
        self.MC_NUMPIECE = ""
        self.MC_NUMSEQUENCE = ""
        self.SM_STATUT = ""
        self.SM_NUMSEQUENCE = ""
        self.SMSTEXT = ""
        self.RECIPIENTPHONE = ""
        self.SL_CODEMESSAGE = ""
        self.SL_MESSAGE = ""
        self.SL_RESULTAT = ""
        self.CodeAgence = ""        
class clsParametre:
    def __init__(self):
        self.PP_LIBELLE = ""
        self.PP_BORNEMIN = 0.0
        self.PP_BORNEMAX = 0.0
        self.PP_MONTANTMINI = 0.0
        self.PP_MONTANTMAXI = 0.0
        self.PP_TAUX = 0.0
        self.PP_MONTANT = 0.0
        self.PP_VALEUR = ""
        self.PL_CODENUMCOMPTE = ""
        self.PP_AFFICHER = ""       
def execute_stored_procedure(connection, stored_procedure_name, params):
    try:
        cursor = connection.cursor()
        cursor.execute(stored_procedure_name, params)
        result = cursor.fetchone()
        return result
    except pyodbc.Error as e:
        MYSQL_REPONSE = f"Error executing stored procedure '{stored_procedure_name}': {e.args[0]}"
        raise Exception(MYSQL_REPONSE)
    
def pvgNumeroPiece(connection, *vppCritere):
    # Préparation des paramètres
    AG_CODEAGENCE, MC_DATEPIECE,OP_CODEOPERATEUR,TABLENAME = vppCritere[0], vppCritere[1],vppCritere[2],vppCritere[3]
    datepiece_str = MC_DATEPIECE
    date_pieces = datetime.strptime(datepiece_str, "%d/%m/%Y")
    params = {
        'AG_CODEAGENCE': AG_CODEAGENCE,
        'MC_DATEPIECE': date_pieces,
        'TABLE_NAME': TABLENAME,#'MOUVEMENTCOMPTABLE',
        'IN_VALEURID': OP_CODEOPERATEUR,
        'NB_ID': 0,
        'MC_NUMPIECE': '',
        'MC_REFERENCEPIECE': ''
    }

    # Exécution de la procédure stockée
    try:
        cursor = connection
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Exécution de la procédure stockée
    try:
        cursor.execute("EXEC PS_INCREMENTNEW ?, ?, ?, ?, ?, ?, ?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        #connection.commit()
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
      
    # Récupération des résultats
    try:
       
        resultatIncrement = recup_info_incrementclientresultat(connection, OP_CODEOPERATEUR)
         
        return resultatIncrement    
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    
def pvgTestJournee(connection, clsObjetEnvoi):
    # Appeler la fonction pvgValueScalarRequeteCount avec le paramètre AG_CODEAGENCE et récupérer la réponse dans l'objet clsAgence
    vlpResultat = pvgValueScalarRequeteCount(connection, clsObjetEnvoi.OE_A,clsObjetEnvoi.OE_J,"O")
    # Vérifier si la première instruction s'est terminée avec succès
    if vlpResultat != 0:
        # Appeler à nouveau la fonction pvgTableLabelOperateur avec le paramètre clsAgence.clsObjetEnvoi.OE_A et OE_Y et récupérer la réponse dans l'objet clsParametre
        clsOperateur = pvgTableLabelOperateur(connection, clsObjetEnvoi.OE_A, clsObjetEnvoi.OE_Y)

        # Appliquer la logique en Python la recuperation de OP_JOURNEEOUVERTE == "N" && clsOperateur.OP_CAISSIER == "O"
        if clsOperateur is not None:
            if clsOperateur['OP_JOURNEEOUVERTE'] == "N" and clsOperateur['OP_CAISSIER'] == "O":
                vlpResultat = '0'
                raise Exception('La journée est fermée ou non encore ouverte !!!') 
    # Retourner vlpResultat
        return vlpResultat
    else :
        raise Exception('La journée est fermée ou non encore ouverte !!!')
    

    
def pvg_comptabilisation_tontine(connection, cls_mouvement_comptable):
    # Convertir la valeur de MC_DATEPIECE en datetime
    date_piece_str = cls_mouvement_comptable['MC_DATEPIECE']
    date_piece = datetime.strptime(date_piece_str, "%d/%m/%Y")

    # Paramètres de la procédure stockée
    params = {
        'AG_CODEAGENCE': cls_mouvement_comptable['AG_CODEAGENCE'],
        'PV_CODEPOINTVENTE': cls_mouvement_comptable['PV_CODEPOINTVENTE'],
        'CO_CODECOMPTE': cls_mouvement_comptable['CO_CODECOMPTE'],
        'CT_IDCARTE': cls_mouvement_comptable['TI_IDTIERS'],
        'MC_CONTACTTIERS': "2250788635251",#cls_mouvement_comptable['MI_CODEMISE'],
        'MC_NUMPIECE': cls_mouvement_comptable['MC_NUMPIECE'],
        'MC_REFERENCEPIECE': cls_mouvement_comptable['MC_REFERENCEPIECE'],
        'MC_LIBELLEOPERATION': cls_mouvement_comptable['MC_LIBELLEOPERATION'],
        'PL_CODENUMCOMPTE': cls_mouvement_comptable['PL_CODENUMCOMPTE'],
        'MONTANT': cls_mouvement_comptable['MC_MONTANTDEBIT'],
        'DATEJOURNEE': date_piece,#cls_mouvement_comptable['MC_DATEPIECE'],
        'MC_NOMTIERS': "",#cls_mouvement_comptable['MC_NOMTIERS'],
        'PI_CODEPIECE': cls_mouvement_comptable['PI_CODEPIECE'],
        'MC_NUMPIECETIERS': cls_mouvement_comptable['MC_NUMPIECETIERS'],
        'OP_CODEOPERATEUR': cls_mouvement_comptable['OP_CODEOPERATEUR'],
        'TS_CODETYPESCHEMACOMPTABLE': cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],
        'ALPHA': 'Y}@128eVIXfoi7',
        'MC_TERMINAL': cls_mouvement_comptable['MC_TERMINAL'],
        'MC_AUTRE1': "",
        'MC_AUTRE2': "",
        'MC_AUTRE3': ""
    }

     # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = connection
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_COMPTABILISATIONTONTINENEW  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        #connection.commit()
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        #cursor.execute("ROLLBACK")
        MYSQL_REPONSE = e.args[1]
        raise Exception(MYSQL_REPONSE)
       # return {'error': f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'}
    
  
    # Récupération des résultats
    try:
        # Assurez-vous que la valeur est une chaîne de caractères pour pouvoir la convertir en entier
        montant_debit_str = cls_mouvement_comptable['MC_MONTANTDEBIT']

        # Convertir la chaîne de caractères en entier
        montant_debit_int = int(montant_debit_str)
        resultat = recup_info_versement_client(connection, cls_mouvement_comptable['AG_CODEAGENCE'], cls_mouvement_comptable['TI_IDTIERS'], date_piece, cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'], cls_mouvement_comptable['CO_CODECOMPTE'], cls_mouvement_comptable['OP_CODEOPERATEUR'], montant_debit_int, 'Y}@128eVIXfoi7')
        """
        if resultat:
           result= recup_info_apisms_clientpiece(connection,cls_mouvement_comptable['OP_CODEOPERATEUR'])
           resultat["MC_NUMPIECE"]= result
        """   
        return resultat    
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Retour des résultats
   # return rows
def pvgDecisionEnvoiSMS(connection, *vppCritere):
    # Appeler la fonction pvgTableLabel avec le paramètre AG_CODEAGENCE et récupérer la réponse dans l'objet clsAgence
    clsAgence = pvgTableLabelAgence(connection, *vppCritere)
    # Vérifier si la première instruction s'est terminée avec succès
    vlpEnvoyerSms = False
    if clsAgence:
        # Appeler à nouveau la fonction pvgTableLabel avec le paramètre clsAgence.SO_CODESOCIETE et "ENVS" et récupérer la réponse dans l'objet clsParametre
        clsParametre = pvgTableLabel(connection, clsAgence.SO_CODESOCIETE, "ENVS")

        # Appliquer la logique en Python
        
        if clsParametre is not None:
            if clsParametre['PP_VALEUR'] in ["2", "3"]:
                vlpEnvoyerSms = True

    # Retourner vlpEnvoyerSms
    return vlpEnvoyerSms


def pvgTableLabelOperateur(connection, *vppCritere):
    cursor = connection
    # Convertir en int
    nombre_int = int(vppCritere[1])
    if len(vppCritere) == 2:
        vapCritere = "FROM OPERATEUR WHERE AG_CODEAGENCE=? AND OP_CODEOPERATEUR=?"
        vapNomParametre = ('@AG_CODEAGENCE','@OP_CODEOPERATEUR')
        vapValeurParametre = (vppCritere[0],nombre_int)
    else:
        vapCritere = ""
        vapNomParametre = ()
        vapValeurParametre = ()

    vapRequete = f"SELECT AG_CODEAGENCE,OP_JOURNEEOUVERTE,OP_CAISSIER {vapCritere}"
    try:
        cursor.execute(vapRequete, vapValeurParametre)
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    
    try:
        rows = cursor.fetchall()

        cls_parametreOperateur =  {}

        for row in rows:
            cls_parametreOperateur['AG_CODEAGENCE'] = str(row[0])
            cls_parametreOperateur['OP_JOURNEEOUVERTE'] = str(row[1])
            cls_parametreOperateur['OP_CAISSIER'] = str(row[2])

        # Retourne l'objet
        return cls_parametreOperateur
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
def pvgTableLabel(connection, *vppCritere):
    cursor = connection

    if len(vppCritere) == 2:
        vapCritere = " WHERE SO_CODESOCIETE=? AND PP_CODEPARAMETRE=?"
        vapNomParametre = ('@SO_CODESOCIETE','PP_CODEPARAMETRE')
        vapValeurParametre = (vppCritere[0],vppCritere[1])
    else:
        vapCritere = ""
        vapNomParametre = ()
        vapValeurParametre = ()

    vapRequete = f"SELECT PP_LIBELLE,PP_BORNEMIN,PP_BORNEMAX,PP_MONTANTMINI,PP_MONTANTMAXI,PP_TAUX,PP_MONTANT,PP_VALEUR,PL_CODENUMCOMPTE,PP_AFFICHER FROM PARAMETRE {vapCritere}"
    try:
        cursor.execute(vapRequete, vapValeurParametre)
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    
    try:
        rows = cursor.fetchall()

        cls_parametre =  {}

        for row in rows:
            cls_parametre['PP_LIBELLE'] = str(row[0])
            cls_parametre['PP_BORNEMIN'] = float(row[1])
            cls_parametre['PP_BORNEMAX'] = float(row[2])
            cls_parametre['PP_MONTANTMINI'] = float(row[3])
            cls_parametre['PP_MONTANTMAXI'] = float(row[4])
            cls_parametre['PP_TAUX'] = str(row[5])
            cls_parametre['PP_MONTANT'] = float(row[6])
            cls_parametre['PP_VALEUR'] = str(row[7])
            cls_parametre['PL_CODENUMCOMPTE'] = str(row[8])
            cls_parametre['PP_AFFICHER'] = str(row[9])

        # Retourne l'objet
        return cls_parametre
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)


def pvgValueScalarRequeteCount(connection, *vppCritere):
    cursor = connection
    date_jour = vppCritere[1]
    date_journee = datetime.strptime(date_jour, "%d/%m/%Y")
    if len(vppCritere) == 3:
        vapCritere = " WHERE AG_CODEAGENCE=? AND JT_DATEJOURNEETRAVAIL=? AND JT_STATUT=?"
        vapNomParametre = ('@AG_CODEAGENCE','@JT_DATEJOURNEETRAVAIL','@JT_STATUT')
        vapValeurParametre = (vppCritere[0],date_journee,vppCritere[2])
    else:
        vapCritere = ""
        vapNomParametre = ()
        vapValeurParametre = ()

    vapRequete = f"SELECT COUNT(JT_DATEJOURNEETRAVAIL) AS JT_DATEJOURNEETRAVAIL  FROM JOURNEETRAVAIL {vapCritere}"
    try:
        cursor.execute(vapRequete, vapValeurParametre)
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    
    try:
        rows = cursor.fetchall()

        RetourSelect = {}

        for row in rows:
            RetourSelect['STATUT'] = row[0]
            
        # Retourne l'objet
        return RetourSelect['STATUT']
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)

    
def pvgTableLabelAgence(connection, *vppCritere):
    cursor = connection

    if len(vppCritere) == 1:
        vapCritere = " WHERE AG_CODEAGENCE=? AND AG_ACTIF='O'"
        vapNomParametre = ('@AG_CODEAGENCE',)
        vapValeurParametre = (vppCritere[0],)
    else:
        vapCritere = ""
        vapNomParametre = ()
        vapValeurParametre = ()

    vapRequete = f"SELECT SO_CODESOCIETE, AG_AGENCECODE, VL_CODEVILLE, AG_RAISONSOCIAL, AG_BOITEPOSTAL, AG_ADRESSEGEOGRAPHIQUE, AG_TELEPHONE, AG_FAX, AG_EMAIL, AG_NUMEROAGREMENT, AG_REFERENCE, AG_DATECREATION, AG_ACTIF, OP_CODEOPERATEUR FROM AGENCE {vapCritere}"
    try:
        cursor.execute(vapRequete, vapValeurParametre)
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    
    try:
        rows = cursor.fetchall()

        clsAgenceObj = clsAgence()

        for row in rows:
            clsAgenceObj.SO_CODESOCIETE = row[0]
            clsAgenceObj.AG_AGENCECODE = row[1]
            clsAgenceObj.VL_CODEVILLE = row[2]
            clsAgenceObj.AG_RAISONSOCIAL = row[3]
            clsAgenceObj.AG_BOITEPOSTAL = row[4]
            clsAgenceObj.AG_ADRESSEGEOGRAPHIQUE = row[5]
            clsAgenceObj.AG_TELEPHONE = row[6]
            clsAgenceObj.AG_FAX = row[7]
            clsAgenceObj.AG_EMAIL = row[8]
            clsAgenceObj.AG_NUMEROAGREMENT = row[9]
            clsAgenceObj.AG_REFERENCE = row[10]
            clsAgenceObj.AG_DATECREATION = row[11]
            clsAgenceObj.AG_ACTIF = row[12]
            clsAgenceObj.OP_CODEOPERATEUR = row[13]

        # Retourne l'objet
        return clsAgenceObj
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

def pvgMobileSms(connection, clsParams):
    clsSmss = []
    resulttel = clsParams['RECIPIENTPHONE'] if clsParams['RECIPIENTPHONE'] != None else ""
    resultidclient = clsParams['CL_IDCLIENT'] if clsParams['CL_IDCLIENT'] != None else ""
    # Paramètres de la procédure stockée
    params = {
        'LG_CODELANGUE': 'fr',
        'PV_CODEPOINTVENTE': clsParams['PV_CODEPOINTVENTE'],
        'CO_CODECOMPTE': clsParams['CO_CODECOMPTE'],
        'CL_TELEPHONE': resulttel,#clsParams['RECIPIENTPHONE'],
        'SM_RAISONNONENVOISMS': clsParams['SM_RAISONNONENVOISMS'],
        'SL_MESSAGECLIENT': clsParams['SMSTEXT'],
        'SM_DATEPIECE': clsParams['SM_DATEPIECE'],
        'LO_LOGICIEL': clsParams['LO_LOGICIEL'],
        'OB_NOMOBJET': clsParams['OB_NOMOBJET'],
        'EJ_IDEPARGNANTJOURNALIER': clsParams['EJ_IDEPARGNANTJOURNALIER'],
        'MB_IDTIERS': clsParams['MB_IDTIERS'],
        'CL_IDCLIENT': resultidclient,#clsParams['CL_IDCLIENT'],
        'TE_CODESMSTYPEOPERATION': clsParams['TE_CODESMSTYPEOPERATION'],
        'SM_NUMSEQUENCE': clsParams['SM_NUMSEQUENCE'],
        'SM_DATEEMISSIONSMS': clsParams['SM_DATEEMISSIONSMS'],
        'MC_NUMPIECE': clsParams['MC_NUMPIECE'],
        'MC_NUMSEQUENCE': '',
        'SM_STATUT': clsParams['SM_STATUT'],
        'TYPEOPERATION': clsParams['TYPEOPERATION'],
        'SL_LIBELLE1': clsParams['SL_LIBELLE1'],
        'SL_LIBELLE2': clsParams['SL_LIBELLE2'],
        'CODECRYPTAGE': 'Y}@128eVIXfoi7'
    }

     # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = connection
    except Exception as e:
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        cursor.close()
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_APISMSNEW ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?,?, ?, ?, ?, ?, ?,?, ?, ?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        #connection.commit()
    except Exception as e:
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        cursor.close()
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
       # return {'error': f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'}
    clsSmss = recup_info_apisms_client(connection, clsParams['CO_CODECOMPTE'])
    
    return clsSmss
   


def pvpPreparationSms(connection, AG_CODEAGENCE, PV_CODEPOINTVENTE, CO_CODECOMPTE, OB_NOMOBJET, CL_TELEPHONE, OP_CODEOPERATEUR, CL_DATECREATION, MB_IDTIERS, CL_IDCLIENT, EJ_IDEPARGNANTJOURNALIER, SMSTEXT, TE_CODESMSTYPEOPERATION, SM_NUMSEQUENCE, SM_DATEEMISSIONSMS, MC_NUMPIECE, MC_NUMSEQUENCE, SM_STATUT, TYPEOPERATION, SL_LIBELLE1, SL_LIBELLE2) -> List[clsParams]:
    clsParamss = []
    #clsParamss: List[clsParams] = []
    clsParams = {}

    clsParams['SL_LIBELLE1'] = SL_LIBELLE1
    clsParams['SL_LIBELLE2'] = SL_LIBELLE2
    clsParams['CO_CODECOMPTE'] = CO_CODECOMPTE
    clsParams['LO_LOGICIEL'] = "1"
    clsParams['OB_NOMOBJET'] = OB_NOMOBJET
    clsParams['SL_VALEURRETOURS'] = ""
    clsParams['INDICATIF'] = ""
    clsParams['RECIPIENTPHONE'] = CL_TELEPHONE
    clsParams['PV_CODEPOINTVENTE'] = PV_CODEPOINTVENTE
    clsParams['CodeOperateur'] = OP_CODEOPERATEUR
    clsParams['SM_DATEPIECE'] = CL_DATECREATION #CL_DATECREATION.strftime("%d-%m-%Y")
    clsParams['SM_RAISONNONENVOISMS'] = ""
    clsParams['TYPEOPERATION'] = TYPEOPERATION
    clsParams['SMSTEXT'] = SMSTEXT
    clsParams['MB_IDTIERS'] = MB_IDTIERS
    clsParams['EJ_IDEPARGNANTJOURNALIER'] = EJ_IDEPARGNANTJOURNALIER
    clsParams['CL_IDCLIENT'] = CL_IDCLIENT
    clsParams['TE_CODESMSTYPEOPERATION'] = TE_CODESMSTYPEOPERATION
    clsParams['SM_NUMSEQUENCE'] = SM_NUMSEQUENCE
    clsParams['SM_DATEEMISSIONSMS'] = SM_DATEEMISSIONSMS #SM_DATEEMISSIONSMS.strftime("%d-%m-%Y") #datetime.strptime(SM_DATEEMISSIONSMS, "%d-%m-%Y")
    clsParams['MC_NUMPIECE'] = MC_NUMPIECE
    clsParams['MC_NUMSEQUENCE'] = MC_NUMSEQUENCE
    clsParams['SM_STATUT'] = SM_STATUT

    # Appel à une fonction externe pour l'envoi des SMS
    clsSmsouts = pvgMobileSms(connection, clsParams)

    # Traitement des résultats des SMS envoyés
    if clsSmsouts:
        clsParams['SM_NUMSEQUENCE'] = clsSmsouts[0]['SM_NUMSEQUENCE']
        clsParams['SMSTEXT'] = clsSmsouts[0]['SM_MESSAGE']
        clsParams['RECIPIENTPHONE'] = clsSmsouts[0]['SM_TELEPHONE']
        clsParams['SL_CODEMESSAGE'] = clsSmsouts[0]['SL_CODEMESSAGE']
        clsParams['SL_MESSAGE']= clsSmsouts[0]['SL_MESSAGE']
        clsParams['SL_RESULTAT'] = clsSmsouts[0]['SL_RESULTAT']
        clsParams['CodeAgence'] = AG_CODEAGENCE

    clsParamss.append(clsParams)

    return clsParamss

def pvgTraitementSms(clsDonnee, AG_CODEAGENCE, PV_CODEPOINTVENTE, CO_CODECOMPTE, OB_NOMOBJET, SM_TELEPHONE, OP_CODEOPERATEUR, SM_DATEPIECE, MB_IDTIERS, CL_IDCLIENT, EJ_IDEPARGNANTJOURNALIER, SMSTEXT, TE_CODESMSTYPEOPERATION, SM_NUMSEQUENCE, SM_DATEEMISSIONSMS, MC_NUMPIECE, MC_NUMSEQUENCE, SM_STATUT, TYPEOPERATION, SL_LIBELLE1, SL_LIBELLE2):
    # Processus d'envoi du SMS
    clsParams = {}  # BOJ modèle de retour
    clsParamss = []  # Liste BOJ selon modèle retourné
    Objet = []  # BOJ ou liste BOJ envoyée
    #clsSmsoutWSDAL = clsSmsoutWSDAL()  # Remplacez clsSmsoutWSDAL par la classe réelle
    date_piece_str = SM_DATEPIECE
    date_piece = datetime.strptime(date_piece_str, "%d/%m/%Y")
    SM_DATEPIECE = date_piece
    
    
    date_piece_str1 = SM_DATEEMISSIONSMS
    date_piece1 = datetime.strptime(date_piece_str1, "%d/%m/%Y")
    SM_DATEEMISSIONSMS = date_piece1
    # Préparation de l'envoi du SMS
    Objet = pvpPreparationSms(clsDonnee, AG_CODEAGENCE, PV_CODEPOINTVENTE, CO_CODECOMPTE, OB_NOMOBJET, SM_TELEPHONE, OP_CODEOPERATEUR, SM_DATEPIECE, MB_IDTIERS, CL_IDCLIENT, EJ_IDEPARGNANTJOURNALIER, SMSTEXT, TE_CODESMSTYPEOPERATION, SM_NUMSEQUENCE, SM_DATEEMISSIONSMS, MC_NUMPIECE, None, SM_STATUT, TYPEOPERATION, SL_LIBELLE1, SL_LIBELLE2)
    if Objet:    
        try:
            # Préparation de l'appel à l'API SMS et mise à jour du SMS
            LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"
            # Appel de l'API SMS
            if Objet[0]["SL_RESULTAT"] != "TRUE":
                return Objet[0]

            if not IsValidateIP(LIENDAPISMS):
                Objet[0]["SL_RESULTAT"] = "FALSE"
                Objet[0]["SL_MESSAGE"] = "L'API SMS doit être configurée !!!"
                #pvgMobileSmsUpdateStatut(clsDonnee, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEPIECE, Objet[0]["SM_NUMSEQUENCE"], "N", "L'API SMS doit être configurée !!!",OP_CODEOPERATEUR)
                return Objet[0]
            Objet[0]['SM_DATEPIECE'] = date_piece_str
            Objet[0]['SM_DATEEMISSIONSMS'] = date_piece_str1
            Objet[0]['RECIPIENTPHONE'] = SM_TELEPHONE#'2250788635251'
            Objet[0]['CL_IDCLIENT'] = ""
            Objet[0]['MC_NUMSEQUENCE'] = ""
            clsParams = excecuteServiceWeb(clsParams, Objet, "post", LIENDAPISMS)

            if clsParams:
                # Mise à jour du statut du SMS
                if clsParams[0]["SL_RESULTAT"] == "TRUE":
                    pvgMobileSmsUpdateStatut(clsDonnee, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEPIECE, Objet[0]["SM_NUMSEQUENCE"], "E", "OK",OP_CODEOPERATEUR)
                elif clsParams[0]["SL_RESULTAT"] == "FALSE":
                    pvgMobileSmsUpdateStatut(clsDonnee, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEPIECE, Objet[0]["SM_NUMSEQUENCE"], "N", clsParams[0]["SL_MESSAGE"],OP_CODEOPERATEUR)
                    Objet[0]["SL_RESULTAT"] = clsParams[0]["SL_RESULTAT"]
                    Objet[0]["SL_MESSAGE"] = clsParams[0]["SL_MESSAGE"]
        except requests.exceptions.RequestException as e:
            Objet[0]["SL_RESULTAT"] = "FALSE"
            Objet[0]["SL_MESSAGE"] = str(e)
            pvgMobileSmsUpdateStatut(clsDonnee, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEPIECE, Objet[0]["SM_NUMSEQUENCE"], "N", str(e),OP_CODEOPERATEUR)
        except Exception as ex:
            clsParams = {
                "SL_RESULTAT": "FALSE",
                "SL_MESSAGE": str(ex)
            }
            clsParamss.append(clsParams)
            pvgMobileSmsUpdateStatut(clsDonnee, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEPIECE, Objet[0]["SM_NUMSEQUENCE"], "N", str(ex),OP_CODEOPERATEUR)

    return Objet[0]


def pvgMobileSmsUpdateStatut(connection, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEEMISSIONSMS, SM_NUMSEQUENCE, SM_STATUT, SM_RAISONNONENVOISMS,OP_CODEOPERATEUR):
    params = {}
    #return clsSmsouts
    params = {
        'AG_CODEAGENCE': AG_CODEAGENCE,
        'SM_DATEPIECE': SM_DATEPIECE,
        'SM_DATEEMISSIONSMS': SM_DATEEMISSIONSMS,
        'SM_NUMSEQUENCE': SM_NUMSEQUENCE,
        'SM_STATUT': SM_STATUT,
        'SM_RAISONNONENVOISMS': SM_RAISONNONENVOISMS,
        'OP_CODEOPERATEUR': OP_CODEOPERATEUR,
        'CODECRYPTAGE':'Y}@128eVIXfoi7'
    }

     # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = connection
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_MOBILESMSUPDATESTATUTNEW  ?, ?, ?, ?, ?, ?, ?,?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        #connection.commit()
    except Exception as e:
        MYSQL_REPONSE = str(e)
        raise Exception(MYSQL_REPONSE)

    # Récupération des résultats
    try:
        # Assurez-vous que la valeur est une chaîne de caractères pour pouvoir la convertir en entier
         recup_info_apisms_clientresultat(connection, OP_CODEOPERATEUR)
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)


def pvgBordereau(connection, *vppCritere):
    clsSmsouts = []
    cursor = connection

    #vapNomParametre = ["@AG_CODEAGENCE", "@TS_CODETYPESCHEMACOMPTABLE", "@MC_DATEPIECE", "@OP_CODEOPERATEUR"]
    vapValeurParametre = [vppCritere[0], vppCritere[1], vppCritere[2], vppCritere[3]]
    vapRequete = "SELECT * FROM [dbo].[FC_NUMEROBORDEREAU](@AG_CODEAGENCE,@TS_CODETYPESCHEMACOMPTABLE,@MC_DATEPIECE,@OP_CODEOPERATEUR) AS NUMEROBORDEREAU"
    vapCritere = ""
    cursor.execute(vapRequete, vapValeurParametre)
    rows = cursor.fetchall()

    for row in rows:
        clsMouvementcomptable.AG_CODEAGENCE = row['AG_CODEAGENCE']
        clsMouvementcomptable.MC_DATEPIECE = datetime.datetime.strptime(row['MC_DATEPIECE'].ToString(), '%Y-%m-%d %H:%M:%S')
        clsMouvementcomptable.MC_NUMPIECE = row['MC_NUMPIECE'].ToString()
        clsMouvementcomptable.MC_NUMSEQUENCE = row['MC_NUMSEQUENCE'].ToString()
        clsMouvementcomptable.NUMEROBORDEREAU = row['NUMEROBORDEREAU'].ToString()
        clsMouvementcomptable.PL_CODENUMCOMPTE = row['PL_CODENUMCOMPTE'].ToString()
    
    return clsSmsouts
def recup_info_versement_client(connection, ag_code_agence, ct_id_carte, mc_date_piece, ts_code_schema_comptable, co_code_compte, op_code_operateur, montant, alpha):
    try:
        cursor = connection

        # Exécution de la fonction SQL
        cursor.execute("SELECT * FROM dbo.FC_RECUPINFOVERSEMENTCLIENT(?, ?, ?, ?, ?, ?, ?, ?)",
                       (ag_code_agence, ct_id_carte, mc_date_piece, ts_code_schema_comptable, co_code_compte, op_code_operateur, montant, alpha))

        # Récupération des résultats
        rows = cursor.fetchall()
        # Création d'un dictionnaire pour stocker les données récupérées
        borderau = {}
        # Traitement des résultats
        for row in rows:
            borderau['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            borderau['MC_DATEPIECE'] = row.MC_DATEPIECE
            borderau['MC_NUMSEQUENCE'] = row.MC_NUMSEQUENCE
            borderau['NUMEROBORDEREAU'] = row.NUMEROBORDEREAU
            borderau['PL_CODENUMCOMPTE'] = row.PL_CODENUMCOMPTE
            borderau['CL_CODECLIENT'] = row.CL_CODECLIENT
            borderau['CL_IDCLIENT'] = row.CL_IDCLIENT
            borderau['EJ_TELEPHONE'] = row.EJ_TELEPHONE
            borderau['SL_MESSAGECLIENT'] = row.SL_MESSAGECLIENT
            borderau['SM_NUMSEQUENCERETOURS'] = row.SM_NUMSEQUENCERETOURS
            borderau['AG_EMAIL'] = row.AG_EMAIL
            borderau['AG_EMAILMOTDEPASSE'] = row.AG_EMAILMOTDEPASSE
            borderau['SL_MESSAGEOBJET'] = row.SL_MESSAGEOBJET
            borderau['EJ_EMAILCLIENT'] = row.EJ_EMAILCLIENT
            borderau['MC_NUMPIECE'] = row.MC_NUMPIECE
            # Faites ce que vous voulez avec les données récupérées
            return borderau
    except Exception as e:
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)

def recup_info_apisms_client(connection, co_codecompte):
    try:
        cursor = connection
        varreq="SELECT * FROM TEMPAPISMSRESULTAT"+co_codecompte
        # Exécution de la fonction SQL
        cursor.execute(varreq)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourSmss = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            clsSms = {}
            clsSms['SL_RESULTAT'] = row.SL_RESULTAT
            clsSms['SL_MESSAGE'] = row.SL_MESSAGE
            clsSms['SM_TELEPHONE'] = row.CL_TELEPHONE
            clsSms['SM_MESSAGE'] = row.SL_MESSAGECLIENT
            clsSms['SL_CODEMESSAGE'] = row.SL_CODEMESSAGE
            clsSms['SM_NUMSEQUENCE'] = row.SM_NUMSEQUENCERETOURS
            RetourSmss.append(clsSms)
            
        if not RetourSmss:
            clsSms = {}
            clsSms['SL_RESULTAT'] = "FALSE"
            clsSms['SL_MESSAGE'] = "Le formatage du Sms Client a échoué"
            clsSms['SM_TELEPHONE'] ='' # clsParams['RECIPIENTPHONE']
            clsSms['SM_MESSAGE'] = ""
            clsSms['SL_CODEMESSAGE'] = ""#datetime.datetime(1900, 1, 1)
            clsSms['SM_NUMSEQUENCE'] = "0"
            RetourSmss.append(clsSms)    
        # Faites ce que vous voulez avec les données récupérées
        return RetourSmss
    except Exception as e:
        cursor.execute("ROLLBACK")
        cursor.close()
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
        #print(f"Une erreur s'est produite : {str(e.args[1])}")   

def recup_info_apisms_clientresultat(connection, co_codeoperateur):
    try:
        cursor = connection
        varreq="SELECT * FROM TEMPAPISMSSTATUT"+co_codeoperateur
        # Exécution de la fonction SQL
        cursor.execute(varreq)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourSmssResultat = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            clsSms = {}
            clsSms['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            clsSms['SL_RESULTAT'] = row.SL_RESULTAT
            clsSms['SL_MESSAGE'] = row.SL_MESSAGE
            RetourSmssResultat.append(clsSms)
        # Faites ce que vous voulez avec les données récupérées
        #return RetourSmssResultat
    except Exception as e:
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
        #print(f"Une erreur s'est produite : {str(e)}")   
def recup_info_incrementclientresultat(connection, co_codeoperateur):
    try:
        cursor = connection
        varreq="SELECT * FROM TEMPINCREMENTRESULTAT"+co_codeoperateur
        # Exécution de la fonction SQL
        cursor.execute(varreq)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourNumResultat = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            clsSms = {}
            clsSms['MC_NUMPIECE'] = row.MC_NUMPIECE
            clsSms['MC_REFERENCEPIECE'] = row.MC_REFERENCEPIECE
            RetourNumResultat.append(clsSms)
        # Faites ce que vous voulez avec les données récupérées
        return RetourNumResultat
    except Exception as e:
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
def recup_info_apisms_clientpiece(connection, co_codeoperateur):
    try:
        cursor = connection
        varreq="SELECT * FROM TEMPCOMPTABILISATIONTONTINENEW"+co_codeoperateur
        # Exécution de la fonction SQL
        cursor.execute(varreq)

        # Récupération des résultats
        rowss = cursor.fetchall()
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for r in rowss:
            recup = {}
            recup['MC_NUMPIECE'] = r.MC_NUMPIECE
            # Faites ce que vous voulez avec les données récupérées
            return recup
    except Exception as e:
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
    
    
def traitement_asynchrone(connection, clsMouvementcomptable, listOperation):
    try:
         # Votre traitement asynchrone ici
            for idx in range(len(listOperation)):
                        vlpEnvoyerSms = pvgDecisionEnvoiSMS(connection, clsMouvementcomptable['AG_CODEAGENCE'])
                        if vlpEnvoyerSms:
                            clsParametreAppelApi = {}
                            clsParametreAppelApi['AG_CODEAGENCE'] = clsMouvementcomptable['AG_CODEAGENCE']
                            clsParametreAppelApi['PV_CODEPOINTVENTE'] = clsMouvementcomptable['PV_CODEPOINTVENTE']
                            clsParametreAppelApi['CL_CODECLIENT'] = listOperation[idx]["CL_CODECLIENT"]
                            clsParametreAppelApi['CL_IDCLIENT'] = listOperation[idx]["CL_IDCLIENT"]
                            clsParametreAppelApi['CO_CODECOMPTE'] = clsMouvementcomptable['CO_CODECOMPTE']
                            clsParametreAppelApi['OB_NOMOBJET'] = "FrmOperationGuichetTiersEpargnantJournalier"
                            clsParametreAppelApi['CL_CONTACT'] = listOperation[idx]["EJ_TELEPHONE"]
                            clsParametreAppelApi['OP_CODEOPERATEUR'] = clsMouvementcomptable['OP_CODEOPERATEUR']
                            clsParametreAppelApi['SM_DATEPIECE'] = str(clsMouvementcomptable['MC_DATEPIECE'])
                            clsParametreAppelApi['SL_MESSAGECLIENT'] = listOperation[idx]["SL_MESSAGECLIENT"]
                            clsParametreAppelApi['SM_NUMSEQUENCE'] = listOperation[idx]["SM_NUMSEQUENCERETOURS"]
                            clsParametreAppelApi['AG_EMAIL'] = listOperation[idx]["AG_EMAIL"]
                            clsParametreAppelApi['AG_EMAILMOTDEPASSE'] = listOperation[idx]["AG_EMAILMOTDEPASSE"]
                            clsParametreAppelApi['SL_MESSAGEOBJET'] = listOperation[idx]["SL_MESSAGEOBJET"]
                            clsParametreAppelApi['EJ_EMAILCLIENT'] = listOperation[idx]["EJ_EMAILCLIENT"]
                            clsParametreAppelApi['SL_LIBELLE1'] = ""
                            clsParametreAppelApi['SL_LIBELLE2'] = ""
                            clsParametreAppelApis = [clsParametreAppelApi]

                            TE_CODESMSTYPEOPERATION = "0005"
                            SL_LIBELLE1 = "C"
                            SL_LIBELLE2 = ""
                            clsParametreAppelApi['SL_LIBELLE1'] = SL_LIBELLE1
                            clsParams = pvgTraitementSms(
                                connection,
                                clsParametreAppelApi['AG_CODEAGENCE'],
                                clsParametreAppelApi['PV_CODEPOINTVENTE'],
                                clsParametreAppelApi['CO_CODECOMPTE'],
                                clsParametreAppelApi['OB_NOMOBJET'],
                                "2250788635251",#clsParametreAppelApi['CL_CONTACT'],
                                clsParametreAppelApi['OP_CODEOPERATEUR'],
                                clsParametreAppelApi['SM_DATEPIECE'],
                                "",
                                clsParametreAppelApi['CL_IDCLIENT'],
                                "",
                                clsParametreAppelApi['SL_MESSAGECLIENT'],
                                TE_CODESMSTYPEOPERATION,
                                "0",
                                "01/01/1900",
                                "0",
                                "0",
                                "N",
                                "0",
                                clsParametreAppelApi['SL_LIBELLE1'],
                                clsParametreAppelApi['SL_LIBELLE2']
                            )

                            clsParametreAppelApis[0]['SL_RESULTATAPI'] = clsParams['SL_RESULTAT']
                            clsParametreAppelApis[0]['SL_MESSAGEAPI'] = clsParams['SL_MESSAGE']
                            if clsParams['SL_RESULTAT'] == "FALSE":
                                clsParametreAppelApis[0]['SL_MESSAGE'] = clsParametreAppelApis[0]['SL_MESSAGE'] + " " + clsParametreAppelApis[0]['SL_MESSAGEAPI']
                            if clsParams['SL_RESULTAT'] == "TRUE":
                                clsParametreAppelApis[0]['SL_MESSAGEAPI'] = ""

                            if "@" in clsParametreAppelApis[0]['EJ_EMAILCLIENT']:
                                smtpServeur = "smtp.gmail.com"
                                portSmtp = 587
                                adresseEmail = clsParametreAppelApis[0]['AG_EMAIL']
                                motDePasse = clsParametreAppelApis[0]['AG_EMAILMOTDEPASSE']
                                destinataire = 'bolatykouassieuloge@gmail.com'#clsParametreAppelApis[0]['EJ_EMAILCLIENT']
                                sujet = "Code Validation"
                                corpsMessage = clsParametreAppelApis[0]['SL_MESSAGECLIENT']
                                message = MIMEMultipart()
                                message['From'] = adresseEmail
                                message['To'] = destinataire
                                message['Subject'] = sujet
                                message.attach(MIMEText(corpsMessage, 'plain'))
                                with smtplib.SMTP(smtpServeur, portSmtp) as server:
                                    server.starttls()
                                    server.login(adresseEmail, motDePasse)
                                    server.sendmail(adresseEmail, destinataire, message.as_string())
            connection.close() 
            pass
          
    except Exception as e:
        print("Erreur lors du traitement asynchrone:", e)


    
def pvgComptabilisationVersement(connection, clsMouvementcomptables, clsBilletages, clsObjetEnvoi):
        try:
            listOperation = []
            IsNetworkConnected()
            pvgTestJournee(connection, clsObjetEnvoi)
            vlpNumPiece = pvgNumeroPiece(connection, clsMouvementcomptables[0]['AG_CODEAGENCE'], str(clsMouvementcomptables[0]['MC_DATEPIECE']),clsMouvementcomptables[0]['OP_CODEOPERATEUR'],"MOUVEMENTCOMPTABLE")
            vlpBiNumPiece = pvgNumeroPiece(connection, clsMouvementcomptables[0]['AG_CODEAGENCE'], str(clsMouvementcomptables[0]['MC_DATEPIECE']),clsMouvementcomptables[0]['OP_CODEOPERATEUR'],"BILLETAGE")
            for clsMouvementcomptable in clsMouvementcomptables:
                ip_address = get_ip_address()
                public_ip_address = get_public_ip_address()
                mac_address = get_mac_address()

                # Mettre ensemble les informations de l'ordinateur et les séparer par des @
                sticker_code1 = ip_address + "@" + public_ip_address + "@" + mac_address
                clsMouvementcomptable['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                if clsMouvementcomptable['MC_REFERENCEPIECE'] == "":
                    clsMouvementcomptable['MC_REFERENCEPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                    clsMouvementcomptable['MC_TERMINAL'] = sticker_code1

                # 1- Exécution de la fonction pvg_comptabilisation_tontine pour la comptabilisation
                DataSet = pvg_comptabilisation_tontine(connection, clsMouvementcomptable)
                
                # Vérifier si la première instruction s'est terminée avec succès
                if DataSet:
                    listOperation.append(DataSet)
                    # 2- Exécution de la fonction pvgDecisionEnvoiSMS pour l'envoi ou non du sms
                    """
                    vlpEnvoyerSms = pvgDecisionEnvoiSMS(connection, clsMouvementcomptable['AG_CODEAGENCE'])
                    if vlpEnvoyerSms:
                        clsParametreAppelApi = {}
                        clsParametreAppelApi['AG_CODEAGENCE'] = clsMouvementcomptable['AG_CODEAGENCE']
                        clsParametreAppelApi['PV_CODEPOINTVENTE'] = clsMouvementcomptable['PV_CODEPOINTVENTE']
                        clsParametreAppelApi['CL_CODECLIENT'] = DataSet["CL_CODECLIENT"]
                        clsParametreAppelApi['CL_IDCLIENT'] = DataSet["CL_IDCLIENT"]
                        clsParametreAppelApi['CO_CODECOMPTE'] = clsMouvementcomptable['CO_CODECOMPTE']
                        clsParametreAppelApi['OB_NOMOBJET'] = "FrmOperationGuichetTiersEpargnantJournalier"
                        clsParametreAppelApi['CL_CONTACT'] = DataSet["EJ_TELEPHONE"]
                        clsParametreAppelApi['OP_CODEOPERATEUR'] = clsMouvementcomptable['OP_CODEOPERATEUR']
                        clsParametreAppelApi['SM_DATEPIECE'] = str(clsMouvementcomptable['MC_DATEPIECE'])
                        clsParametreAppelApi['SL_MESSAGECLIENT'] = DataSet["SL_MESSAGECLIENT"]
                        clsParametreAppelApi['SM_NUMSEQUENCE'] = DataSet["SM_NUMSEQUENCERETOURS"]
                        clsParametreAppelApi['AG_EMAIL'] = DataSet["AG_EMAIL"]
                        clsParametreAppelApi['AG_EMAILMOTDEPASSE'] = DataSet["AG_EMAILMOTDEPASSE"]
                        clsParametreAppelApi['SL_MESSAGEOBJET'] = DataSet["SL_MESSAGEOBJET"]
                        clsParametreAppelApi['EJ_EMAILCLIENT'] = DataSet["EJ_EMAILCLIENT"]
                        clsParametreAppelApi['SL_LIBELLE1'] = ""
                        clsParametreAppelApi['SL_LIBELLE2'] = ""
                        clsParametreAppelApis = [clsParametreAppelApi]

                        TE_CODESMSTYPEOPERATION = "0005"
                        SL_LIBELLE1 = "C"
                        SL_LIBELLE2 = ""
                        clsParametreAppelApi['SL_LIBELLE1'] = SL_LIBELLE1
                        clsParams = pvgTraitementSms(
                            connection,
                            clsParametreAppelApi['AG_CODEAGENCE'],
                            clsParametreAppelApi['PV_CODEPOINTVENTE'],
                            clsParametreAppelApi['CO_CODECOMPTE'],
                            clsParametreAppelApi['OB_NOMOBJET'],
                            "2250788635251",#clsParametreAppelApi['CL_CONTACT'],
                            clsParametreAppelApi['OP_CODEOPERATEUR'],
                            clsParametreAppelApi['SM_DATEPIECE'],
                            "",
                            clsParametreAppelApi['CL_IDCLIENT'],
                            "",
                            clsParametreAppelApi['SL_MESSAGECLIENT'],
                            TE_CODESMSTYPEOPERATION,
                            "0",
                            "01/01/1900",
                            "0",
                            "0",
                            "N",
                            "0",
                            clsParametreAppelApi['SL_LIBELLE1'],
                            clsParametreAppelApi['SL_LIBELLE2']
                        )

                        clsParametreAppelApis[0]['SL_RESULTATAPI'] = clsParams['SL_RESULTAT']
                        clsParametreAppelApis[0]['SL_MESSAGEAPI'] = clsParams['SL_MESSAGE']
                        if clsParams['SL_RESULTAT'] == "FALSE":
                            clsParametreAppelApis[0]['SL_MESSAGE'] = clsParametreAppelApis[0]['SL_MESSAGE'] + " " + clsParametreAppelApis[0]['SL_MESSAGEAPI']
                        if clsParams['SL_RESULTAT'] == "TRUE":
                            clsParametreAppelApis[0]['SL_MESSAGEAPI'] = ""

                        if "@" in clsParametreAppelApis[0]['EJ_EMAILCLIENT']:
                            smtpServeur = "smtp.gmail.com"
                            portSmtp = 587
                            adresseEmail = clsParametreAppelApis[0]['AG_EMAIL']
                            motDePasse = clsParametreAppelApis[0]['AG_EMAILMOTDEPASSE']
                            destinataire = 'bolatykouassieuloge@gmail.com'#clsParametreAppelApis[0]['EJ_EMAILCLIENT']
                            sujet = "Code Validation"
                            corpsMessage = clsParametreAppelApis[0]['SL_MESSAGECLIENT']
                            message = MIMEMultipart()
                            message['From'] = adresseEmail
                            message['To'] = destinataire
                            message['Subject'] = sujet
                            message.attach(MIMEText(corpsMessage, 'plain'))
                            with smtplib.SMTP(smtpServeur, portSmtp) as server:
                                server.starttls()
                                server.login(adresseEmail, motDePasse)
                                server.sendmail(adresseEmail, destinataire, message.as_string())
                    """
                    # 3- Exécution de la fonction pvpGenererMouchard pour l'insertion dans le mouchard
                    pvpGenererMouchard(connection, clsObjetEnvoi, DataSet["MC_NUMPIECE"], "A", sticker_code1)

                    # 4- Exécution de la fonction pvgBordereau pour obtenir les informations du mouvement comptable
                    clsMouvementcomptable = DataSet  # pvgBordereau(connection, clsMouvementcomptable['AG_CODEAGENCE'], clsMouvementcomptable['TS_CODETYPESCHEMACOMPTABLE'], clsMouvementcomptable['MC_DATEPIECE'].ToShortDateString(), clsMouvementcomptable['AG_COP_CODEOPERATEURDEAGENCE'])
                    
            # 2- Mise à jour du billetage
            if clsBilletages is not None:
                    for idx in range(len(clsBilletages)):
                        clsBilletages[idx]['AG_CODEAGENCE'] = clsMouvementcomptable['AG_CODEAGENCE']
                        clsBilletages[idx]['MC_DATEPIECE'] = clsMouvementcomptable['MC_DATEPIECE']
                        clsBilletages[idx]['BI_NUMPIECE'] = vlpBiNumPiece[0]['MC_NUMPIECE']
                        clsBilletages[idx]['MC_NUMPIECE'] = clsMouvementcomptable['MC_NUMPIECE']
                        clsBilletages[idx]['MC_NUMSEQUENCE'] = clsMouvementcomptable['MC_NUMSEQUENCE']
                        clsBilletages[idx]['PL_CODENUMCOMPTE'] = clsMouvementcomptable['PL_CODENUMCOMPTE']
                        pvgInsert(connection, clsBilletages[idx])
            
            # 3- Ajout du numéro de bordereau à SL_MESSAGEAPI
                    # Test du lien de l'API SMS
                    LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"
                    clsMouvementcomptable['NUMEROBORDEREAU'] = clsMouvementcomptable['NUMEROBORDEREAU'] #+ "/" + clsParametreAppelApis[0]['SL_MESSAGEAPI']
                    Retour = {}
                    Retour['NUMEROBORDEREAU'] = clsMouvementcomptable['NUMEROBORDEREAU']
                    Retour['MESSAGEAPI'] = ""#clsParametreAppelApis[0]['SL_MESSAGEAPI']
                    if not IsValidateIP(LIENDAPISMS):
                        Retour['MESSAGEAPI']  = "L'API SMS doit être configurée !!!"
                    Retour['SL_RESULTAT'] = "TRUE"
                    
            # Démarrer le traitement asynchrone dans un thread
            if listOperation is not None:
                        thread_traitement = threading.Thread(target=traitement_asynchrone, args=(connection, clsMouvementcomptables[0], listOperation))
                        thread_traitement.daemon = True  # Définir le thread comme démon
                        thread_traitement.start()
            # 4- Retourner le numéro de bordereau
            return Retour #clsMouvementcomptable['NUMEROBORDEREAU']

        except Exception as e:
            #connection.execute("ROLLBACK")
            #connection.close()
            Retour = {}
            Retour['SL_MESSAGE'] = str(e.args[0])
            Retour['SL_RESULTAT'] = "FALSE"
            return Retour
        
def pvpGenererMouchard(connection,clsObjetEnvoi, vppAction, vppTypeAction,TERMINALIDENTIFIANT):
    clsMouchard = {}
    clsMouchard['AG_CODEAGENCE'] = clsObjetEnvoi.OE_A
    clsMouchard['OP_CODEOPERATEUR'] = clsObjetEnvoi.OE_Y
    
    if vppTypeAction == "A":
        clsMouchard['MO_ACTION'] = "MOUVEMENTCOMPTABLE (Ajout) : " + vppAction
    elif vppTypeAction == "M":
        clsMouchard['MO_ACTION'] = "MOUVEMENTCOMPTABLE (Modification) : " + vppAction
    elif vppTypeAction == "S":
        clsMouchard['MO_ACTION'] = "MOUVEMENTCOMPTABLE (Suppression) : " + vppAction
    elif vppTypeAction == "E":
        clsMouchard['MO_ACTION'] = "MOUVEMENTCOMPTABLE (Edition de l'etat) : " + vppAction

    if clsMouchard['OP_CODEOPERATEUR'] == "":
        clsMouchard['OP_CODEOPERATEUR'] = None
    # Préparation des paramètres
        
    params = {}
    #return clsSmsouts
    params = {
        'CODEAGENCE': clsMouchard['AG_CODEAGENCE'],
        'CODEOPERATEUR': clsMouchard['OP_CODEOPERATEUR'],
        #'DATEACTION': datetime.today(),
        #'MO_HEUREACTION': datetime.now().time(),
        'MO_ACTION': clsMouchard['MO_ACTION'],
        'CODECRYPTAGE':'Y}@128eVIXfoi7',
        'MO_TERMINALIDENTIFIANT': TERMINALIDENTIFIANT,
        'MO_TERMINALDESCRIPTION':  TERMINALIDENTIFIANT,
        'SL_CODECOMPTEWEB':None ,
        'OP_CODEOPERATEURAPPLICATIONMOBILE':None 
    }

     # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = connection
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_AJOUTMOUCHARDNEW  ?, ?, ?, ?, ?, ?, ?,?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        #connection.commit()
    except Exception as e:
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

   














def IsValidateIP(ipaddress):
    ValidateIP = False
    ipaddress = ipaddress.replace("/ZenithwebClasse.svc/", "")
    ipaddress = ipaddress.replace("/Service/wsApisms.svc/SendMessage", "")

    if not ipaddress:
        return ValidateIP

    if "http://" in ipaddress:
        ipaddress = ipaddress.replace("http://", "")

    if "https://" in ipaddress:
        ipaddress = ipaddress.replace("https://", "")

    adresse = ipaddress.split(':')

    if len(adresse) != 2:
        return ValidateIP

    HostURI = adresse[0]
    PortNumber = adresse[1].replace("/", "")

    ValidateIP = PingHost(HostURI, int(PortNumber))
    return ValidateIP

def PingHost(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Timeout de 1 seconde
        result = sock.connect_ex((host, port))
        if result == 0:
            return True
        else:
            return False
    except Exception as e:
        print("Erreur lors de la tentative de ping :", e)
        return False

def excecuteServiceWeb(data, Objetenv, method, url):
    objList = []
    Objet={}
    headers = {'Content-Type': 'application/json'}
    try:
        Objet={
            "Objet": [
                {
                    "CO_CODECOMPTE": "",
                    "CodeAgence": Objetenv[0]['CodeAgence'],#"1002",
                    "RECIPIENTPHONE": Objetenv[0]['RECIPIENTPHONE'],#"2250759588384",
                    "SM_RAISONNONENVOISMS": Objetenv[0]['SM_RAISONNONENVOISMS'],#"xxx" a voir,
                    "SM_DATEPIECE": Objetenv[0]['SM_DATEPIECE'],#"12-05-2022",
                    "LO_LOGICIEL": "01",
                    "OB_NOMOBJET": Objetenv[0]['OB_NOMOBJET'],#"test",
                    "SMSTEXT": Objetenv[0]['SMSTEXT'],#"TEST",
                    "INDICATIF": "225",
                    "SM_NUMSEQUENCE": Objetenv[0]['SM_NUMSEQUENCE'],#"1",
                    "SM_STATUT": Objetenv[0]['SM_STATUT'],#"E" a voir
                }
            ]
        }
        response = requests.request(method, url, json=Objet, headers=headers)
        if response.status_code == 200:
            objList = response.json()
    except requests.exceptions.RequestException as e:
        # Log.Error("Testing log4net error logging - Impossible d'atteindre le service Web")
        pass
    except Exception as ex:
        # Log.Error("Testing log4net error logging - " + str(ex))
        pass
    return objList

def IsNetworkConnected():
    try:
        response = requests.get("http://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        MYSQL_REPONSE = f'Opération impossible veuillez revoir la connexion internet'
        raise Exception(MYSQL_REPONSE)   


def pvgInsert(connection, clsBilletage):
    params = {}
    #return clsSmsouts
    params = {
        'AG_CODEAGENCE1': clsBilletage['AG_CODEAGENCE'],
        'MC_DATEPIECE1': clsBilletage['MC_DATEPIECE'],
        'BI_NUMPIECE1': clsBilletage['BI_NUMPIECE'],
        'BI_NUMSEQUENCE1': clsBilletage['BI_NUMSEQUENCE'],
        'CB_CODECOUPURE1': clsBilletage['CB_CODECOUPURE'],
        'PL_CODENUMCOMPTE1': clsBilletage['PL_CODENUMCOMPTE'],
        'MC_NUMPIECE1': clsBilletage['MC_NUMPIECE'],
        'MC_NUMSEQUENCE1': clsBilletage['MC_NUMSEQUENCE'],
        'BI_QUANTITESORTIE1': clsBilletage['BI_QUANTITESORTIE'],
        'BI_QUANTITEENTREE1': clsBilletage['BI_QUANTITEENTREE'],
        'CODECRYPTAGE1': 'Y}@128eVIXfoi7', 
        'TYPEOPERATION': clsBilletage['TYPEOPERATION'],
        
    }

     # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = connection
    except Exception as e:
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        cursor.close()
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Exécution de la procédure stockée
    try:
        connection.commit()
        cursor.execute("EXECUTE PC_BILLETAGE  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        connection.commit()
    except Exception as e:
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        cursor.close()
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
def get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print("Adresse IP locale : " + ip_address)
        return ip_address
    except Exception as e:
        print("Erreur lors de la récupération de l'adresse IP : " + str(e))
        return None

def get_public_ip_address():
    try:
        response = requests.get('http://icanhazip.com/')
        ip_address = response.text.strip()
        print("Adresse IP publique : " + ip_address)
        return ip_address
    except Exception as e:
        print("Erreur lors de la récupération de l'adresse IP publique : " + str(e))
        return None

def get_mac_address():
    try:
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff)
                                for i in range(0,8*6,8)][::-1])
        print("Adresse MAC : " + mac_address)
        return mac_address
    except Exception as e:
        print("Erreur lors de la récupération de l'adresse MAC : " + str(e))
        return None