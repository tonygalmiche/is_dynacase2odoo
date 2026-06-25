#!/usr/bin/env python3
"""
Création d'une fiche d'absence dans Kelio via Web Service SOAP.

Web Service : AbsenceFileService
Méthode     : importAbsenceFiles
WSDL        : <KELIO_BASE_URL>/open/services/AbsenceFileService?wsdl

Documentation : https://kelio.help.kelio.io/V5.1M6/fr-FR/webservices/absences.html

Modes de saisie disponibles :
  1. De date à date            : renseigner startDate + endDate
  2. Demi-journée              : renseigner en plus startInTheMorning / endingTheAfternoon
  3. D'heure à heure (partiel) : startDate = endDate + firstStartTime + firstEndTime
  4. Durée imputée (partiel)   : startDate = endDate + offset (en minutes)

Prérequis :
  pip install zeep requests
"""

import sys
import os
import re
import argparse
import calendar
import logging
import requests as req
from datetime import date, timedelta
logging.getLogger('zeep').setLevel(logging.WARNING)

# Ajout du dossier parent au path pour importer config.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import config

from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth

NS = "http://echange.service.open.bodet.com"


# =============================================================================
# Lecture des champs hérités stockés dans _raw_elements par zeep (strict=False)
# =============================================================================
def get_raw(obj, field_name):
    """Lit un champ depuis l'objet zeep, ou depuis _raw_elements si None."""
    val = getattr(obj, field_name, None)
    if val is not None:
        return val
    raw = getattr(obj, '_raw_elements', None)
    if raw:
        tag = f'{{{NS}}}{field_name}'
        for el in raw:
            if el.tag == tag:
                return el.text
    return None


# =============================================================================
# Construction du client SOAP avec authentification HTTP Basic
# =============================================================================
def get_client(service="AbsenceFileService", strict=True):
    wsdl_url = f"{config.KELIO_BASE_URL}/open/services/{service}?wsdl"
    session = Session()
    session.auth = HTTPBasicAuth(config.KELIO_USER, config.KELIO_PASSWORD)
    transport = Transport(session=session)
    settings = Settings(strict=strict, xml_huge_tree=True)
    client = Client(wsdl=wsdl_url, transport=transport, settings=settings)
    return client


# =============================================================================
# Lister les types d'absences disponibles dans Kelio
# =============================================================================
def lister_types_absences():
    """
    Récupère tous les types (motifs) d'absences configurés dans Kelio.
    Web Service : TypeService  Méthode : exportAbsenceTypes
    """
    # strict=False : ignore les champs inconnus dans la réponse (ex: defaultExternalReferenceType)
    client = get_client("TypeService", strict=False)
    result = client.service.exportAbsenceTypes()
    # zeep retourne directement une liste
    if isinstance(result, list):
        return result
    return result.exportedAbsenceTypes if result and result.exportedAbsenceTypes else []


# =============================================================================
# Lire les fiches d'absences existantes pour un salarié
# =============================================================================
def lire_absences(start_date, end_date, matricule=None):
    """
    Lit les fiches d'absence entre deux dates.
    Si matricule est None : retourne toutes les absences de la population.
    Méthode : exportAbsenceFiles
    """
    client = get_client(strict=False)
    result = client.service.exportAbsenceFiles(
        populationFilter=None,
        groupFilter=None,
        startDate=start_date,
        endDate=end_date,
    )
    # zeep retourne directement une liste ou un objet avec exportedAbsenceFiles
    if isinstance(result, list):
        absences = result
    else:
        absences = result.exportedAbsenceFiles if result and result.exportedAbsenceFiles else []
    # Filtrage optionnel par matricule
    if matricule:
        absences = [a for a in absences if get_raw(a, 'employeeIdentificationNumber') == matricule]
    return absences


# =============================================================================
# Envoi d'un SOAP brut (bypasse zeep pour les champs hérités non sérialisés)
# =============================================================================
def _import_absence_soap_brut(absence_xml_items):
    """
    Envoie importAbsenceFiles via HTTP directement (pas via zeep type_factory).
    absence_xml_items : liste de chaînes XML représentant chaque <AbsenceFile>.
    Retourne le texte XML de la réponse.
    """
    items_xml = "\n".join(absence_xml_items)
    body = f"""<?xml version='1.0' encoding='utf-8'?>
<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
  <soap-env:Body>
    <ns0:importAbsenceFiles xmlns:ns0="{NS}">
      <ns0:absenceFilesToImport>
{items_xml}
      </ns0:absenceFilesToImport>
    </ns0:importAbsenceFiles>
  </soap-env:Body>
</soap-env:Envelope>"""
    url = f"{config.KELIO_BASE_URL}/open/services/AbsenceFileService"
    headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "urn:importAbsenceFiles"}
    response = req.post(
        url, data=body.encode("utf-8"), headers=headers,
        auth=(config.KELIO_USER, config.KELIO_PASSWORD),
        timeout=30,
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code} — {response.text[:2000]}")
    return response.text


def _absence_file_xml(matricule, start_date, end_date, type_absence,
                      start_in_morning=True, ending_the_afternoon=True, comment=None):
    """Construit le XML d'un élément <AbsenceFile> pour importAbsenceFiles."""
    def b(v): return "true" if v else "false"
    comment_xml = f"<ns0:comment>{comment}</ns0:comment>" if comment else ""
    return f"""        <ns0:AbsenceFile xmlns:ns0="{NS}">
          <ns0:employeeIdentificationNumber>{matricule}</ns0:employeeIdentificationNumber>
          <ns0:startDate>{start_date}</ns0:startDate>
          <ns0:endDate>{end_date}</ns0:endDate>
          <ns0:absenceTypeAbbreviation>{type_absence}</ns0:absenceTypeAbbreviation>
          <ns0:startInTheMorning>{b(start_in_morning)}</ns0:startInTheMorning>
          <ns0:endingTheAfternoon>{b(ending_the_afternoon)}</ns0:endingTheAfternoon>
          {comment_xml}
        </ns0:AbsenceFile>"""


def creer_absence_date_a_date(
    matricule,
    start_date,
    end_date,
    type_absence,
    matin_debut=True,
    aprem_fin=True,
    comment=None,
):
    """Crée une fiche d'absence dans Kelio pour un salarié identifié par son matricule."""
    xml_item = _absence_file_xml(matricule, start_date, end_date, type_absence,
                                  start_in_morning=matin_debut,
                                  ending_the_afternoon=aprem_fin,
                                  comment=comment)
    return _import_absence_soap_brut([xml_item])


def creer_absence_demi_journee(
    matricule,
    start_date,
    end_date,
    type_absence,
    start_in_morning=True,
    end_in_afternoon=False,
    comment=None,
):
    """Crée une fiche d'absence sur une ou plusieurs demi-journées."""
    xml_item = _absence_file_xml(matricule, start_date, end_date, type_absence,
                                  start_in_morning=start_in_morning,
                                  ending_the_afternoon=end_in_afternoon,
                                  comment=comment)
    return _import_absence_soap_brut([xml_item])


# =============================================================================
# Récupérer la clé (absenceFileKey) d'une absence après création
# =============================================================================
def get_absence_key(matricule, start_date, end_date, type_absence):
    """
    Relit les absences et retourne absenceFileKey pour le triplet
    (matricule, startDate, endDate, type). Retourne None si non trouvée.
    """
    absences = lire_absences(start_date, end_date)
    for a in absences:
        mat = get_raw(a, 'employeeIdentificationNumber') or ''
        if (mat == matricule
                and str(a.startDate) == str(start_date)
                and str(a.endDate) == str(end_date)
                and getattr(a, 'absenceTypeAbbreviation', '') == type_absence):
            return getattr(a, 'absenceFileKey', None)
    return None


# =============================================================================
# Supprimer une absence par sa clé (absenceFileKey)
# =============================================================================
def supprimer_absence(absence_file_key):
    """
    Supprime une fiche d'absence identifiée par sa clé Kelio.
    Utilise deleteAbsenceFiles avec le champ absenceFileKey.
    """
    body = f"""<?xml version='1.0' encoding='utf-8'?>
<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
  <soap-env:Body>
    <ns0:deleteAbsenceFiles xmlns:ns0="{NS}">
      <ns0:absenceFilesToDelete>
        <ns0:AbsenceFile xmlns:ns0="{NS}">
          <ns0:absenceFileKey>{absence_file_key}</ns0:absenceFileKey>
        </ns0:AbsenceFile>
      </ns0:absenceFilesToDelete>
    </ns0:deleteAbsenceFiles>
  </soap-env:Body>
</soap-env:Envelope>"""
    url = f"{config.KELIO_BASE_URL}/open/services/AbsenceFileService"
    headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "urn:deleteAbsenceFiles"}
    response = req.post(
        url, data=body.encode("utf-8"), headers=headers,
        auth=(config.KELIO_USER, config.KELIO_PASSWORD),
        timeout=30,
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code} — {response.text[:2000]}")
    return response.text


# =============================================================================
# Lister les employés (version simplifiée)
# =============================================================================
def lister_employes():
    """
    Récupère la liste simplifiée des salariés.
    Web Service : LightEmployeeService  Méthode : exportLightEmployeesList
    Signature : exportFilter: ArrayOfAskedPopulation
    """
    client = get_client("LightEmployeeService", strict=False)
    factory = client.type_factory(NS)
    today = date.today()
    # populationMode=1 = un salarié précis → erreur
    # Essai avec populationMode=0 = toute la population, sans salarié ciblé
    filtre = factory.AskedPopulation(
        populationMode=0,
        populationStartDate=date(today.year, 1, 1),
        populationEndDate=date(today.year, 12, 31),
    )
    result = client.service.exportLightEmployeesList(
        exportFilter={'AskedPopulation': [filtre]}
    )
    if isinstance(result, list):
        return result
    return result.exportedLightEmployees if result and result.exportedLightEmployees else []


# =============================================================================
# Programme principal
# =============================================================================
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Gestion des absences Kelio")
    parser.add_argument("--employes", action="store_true", help="Afficher uniquement la liste des employés")
    parser.add_argument("--absences", action="store_true", help="Afficher uniquement la liste des absences")
    parser.add_argument("--supprimer-matricule", metavar="MATRICULE", help="Supprimer toutes les absences d'un matricule donné")
    args = parser.parse_args()

    print(f"Serveur Kelio : {config.KELIO_BASE_URL}")
    print("=" * 60)

    if args.employes:
        print("\n[0] Liste des employés :")
        try:
            employes = lister_employes()
            if employes:
                print(f"  {'Matricule':12s} {'Badge':12s} {'Nom':20s} {'Prénom'}")
                print(f"  {'-'*12} {'-'*12} {'-'*20} {'-'*15}")
                for e in employes:
                    mat    = get_raw(e, 'employeeIdentificationNumber') or '?'
                    badge  = get_raw(e, 'employeeBadgeCode') or '?'
                    nom    = get_raw(e, 'employeeSurname') or '?'
                    prenom = get_raw(e, 'employeeFirstName') or '?'
                    print(f"  {str(mat):12s} {str(badge):12s} {str(nom):20s} {prenom}")
            else:
                print("  Aucun employé retourné.")
        except Exception as e:
            print(f"  Erreur lecture employés : {e}")
        sys.exit(0)

    if args.supprimer_matricule:
        matricule = args.supprimer_matricule
        DATE_DEBUT = date(date.today().year, 1, 1)
        DATE_FIN   = date(date.today().year, 12, 31)
        print(f"\nSuppression de toutes les absences du matricule {matricule} ({DATE_DEBUT} → {DATE_FIN}) :")
        try:
            absences = lire_absences(DATE_DEBUT, DATE_FIN, matricule=matricule)
            if not absences:
                print("  Aucune absence trouvée pour ce matricule.")
            else:
                nb_ok = 0
                nb_err = 0
                for a in absences:
                    key = getattr(a, 'absenceFileKey', None)
                    type_abs = getattr(a, 'absenceTypeAbbreviation', '?')
                    if key is None:
                        print(f"  [{type_abs} {a.startDate}] IGNORÉE — absenceFileKey introuvable")
                        nb_err += 1
                        continue
                    try:
                        supprimer_absence(key)
                        print(f"  [clé {key} / {type_abs} {a.startDate}] Supprimée")
                        nb_ok += 1
                    except Exception as ex:
                        print(f"  [clé {key} / {type_abs} {a.startDate}] ERREUR : {ex}")
                        nb_err += 1
                print(f"\n  Résultat : {nb_ok} supprimée(s), {nb_err} erreur(s).")
        except Exception as e:
            print(f"  Erreur : {e}")
        sys.exit(0)

    if args.absences:
        DATE_DEBUT = date(date.today().year, 1, 1)
        DATE_FIN   = date(date.today().year, 12, 31)
        print(f"\nListe des absences ({DATE_DEBUT} → {DATE_FIN}) :")
        try:
            absences = lire_absences(DATE_DEBUT, DATE_FIN)
            if absences:
                print(f"  {'Clé':6s} {'Matricule':12s} {'Nom':20s} {'Prénom':15s} {'Type':10s} {'Début':12s} {'Fin'}")
                print(f"  {'-'*6} {'-'*12} {'-'*20} {'-'*15} {'-'*10} {'-'*12} {'-'*12}")
                for a in absences:
                    key      = str(getattr(a, 'absenceFileKey', '?'))
                    mat      = get_raw(a, 'employeeIdentificationNumber') or get_raw(a, 'employeeBadgeCode') or '?'
                    nom      = get_raw(a, 'employeeSurname') or '?'
                    prenom   = get_raw(a, 'employeeFirstName') or '?'
                    type_abs = getattr(a, 'absenceTypeAbbreviation', '?')
                    print(f"  {key:6s} {str(mat):12s} {str(nom):20s} {str(prenom):15s} {str(type_abs):10s} {str(a.startDate):12s} {a.endDate}")
            else:
                print("  Aucune absence trouvée.")
        except Exception as e:
            print(f"  Erreur lecture absences : {e}")
        sys.exit(0)

    # --- 0. Lister les employés ---
    print("\n[0] Liste des employés :")
    try:
        employes = lister_employes()
        if employes:
            print(f"  {'Matricule':12s} {'Badge':12s} {'Nom':20s} {'Prénom'}")
            print(f"  {'-'*12} {'-'*12} {'-'*20} {'-'*15}")
            for e in employes:
                mat    = get_raw(e, 'employeeIdentificationNumber') or '?'
                badge  = get_raw(e, 'employeeBadgeCode') or '?'
                nom    = get_raw(e, 'employeeSurname') or '?'
                prenom = get_raw(e, 'employeeFirstName') or '?'
                print(f"  {str(mat):12s} {str(badge):12s} {str(nom):20s} {prenom}")
        else:
            print("  Aucun employé retourné.")
    except Exception as e:
        print(f"  Erreur lecture employés : {e}")

    # --- 1. Lister les types d'absences disponibles ---
    print("\n[1] Types d'absences disponibles :")
    try:
        types = lister_types_absences()
        if types:
            print(f"  {'Abrégé':10s} | Libellé")
            print(f"  {'-'*10}-+-{'-'*30}")
            for t in types:
                abrev = get_raw(t, 'typeAbbreviation') or '?'
                label = get_raw(t, 'typeDescription') or '?'
                print(f"  {str(abrev):10s} | {label}")
        else:
            print("  Aucun type d'absence retourné.")
    except Exception as e:
        print(f"  Erreur lecture types : {e}")

    # --- 2. Créer des absences ---
    MATRICULE = "0000000970"  # BONVALOT EMMANUEL
    absences_a_creer = [
        ("CP",  date(2026, 7, 7),  date(2026, 7, 7)),   # Mar → Ven 07/08
        ("RTT", date(2026, 7, 14), date(2026, 7, 14)),  # Mar → Ven 14/08
        ("RCR", date(2026, 7, 21), date(2026, 7, 21)),  # Mar → Ven 21/08
    ]

    print(f"\n[2] Création de {len(absences_a_creer)} absence(s) pour matricule {MATRICULE} :")
    # cles_creees : liste de (absenceFileKey, type, new_deb, new_fin) pour la modif suivante
    cles_creees = []
    for type_absence, deb, fin in absences_a_creer:
        try:
            result_xml = creer_absence_date_a_date(MATRICULE, deb, fin, type_absence)
            errors = re.findall(r'<(?:ns\d+:)?errorMessage>(.+?)</(?:ns\d+:)?errorMessage>', result_xml)
            if errors:
                print(f"  [{type_absence} {deb}] ERREUR : {errors}")
            else:
                key = get_absence_key(MATRICULE, deb, fin, type_absence)
                print(f"  [{type_absence} {deb}] OK — absenceFileKey={key}")
                cles_creees.append((key, type_absence, deb, fin))
        except Exception as e:
            print(f"  ERREUR {type_absence} {deb} : {e}")

    def afficher_absences(titre):
        DATE_DEBUT = date(2026, 1, 1)
        DATE_FIN   = date(2026, 12, 31)
        print(f"\n{titre} ({DATE_DEBUT} → {DATE_FIN}) :")
        try:
            absences = lire_absences(DATE_DEBUT, DATE_FIN)
            if absences:
                print(f"  {'Clé':6s} {'Matricule':12s} {'Nom':20s} {'Prénom':15s} {'Type':10s} {'Début':12s} {'Fin'}")
                print(f"  {'-'*6} {'-'*12} {'-'*20} {'-'*15} {'-'*10} {'-'*12} {'-'*12}")
                for a in absences:
                    key      = str(getattr(a, 'absenceFileKey', '?'))
                    mat      = get_raw(a, 'employeeIdentificationNumber') or get_raw(a, 'employeeBadgeCode') or '?'
                    nom      = get_raw(a, 'employeeSurname') or '?'
                    prenom   = get_raw(a, 'employeeFirstName') or '?'
                    type_abs = getattr(a, 'absenceTypeAbbreviation', '?')
                    print(f"  {key:6s} {str(mat):12s} {str(nom):20s} {str(prenom):15s} {str(type_abs):10s} {str(a.startDate):12s} {a.endDate}")
            else:
                print("  Aucune absence trouvée.")
        except Exception as e:
            print(f"  Erreur lecture absences : {e}")

    # --- 3. Relire toutes les absences après création ---
    afficher_absences("[3] Absences après création")

    # --- 4. Modifier les absences créées en [2] → décaler de 7 jours ---
    print(f"\n[4] Modification des absences créées (décalage +7 jours) pour matricule {MATRICULE} :")
    for key, type_abs, old_deb, old_fin in cles_creees:
        new_deb = old_deb + timedelta(days=7)
        new_fin = old_fin + timedelta(days=7)
        try:
            supprimer_absence(key)
            # Supprimer aussi une éventuelle absence déjà existante à la date cible
            existing_key = get_absence_key(MATRICULE, new_deb, new_fin, type_abs)
            if existing_key is not None:
                supprimer_absence(existing_key)
            result_xml = creer_absence_date_a_date(MATRICULE, new_deb, new_fin, type_abs)
            errors = re.findall(r'<(?:ns\d+:)?errorMessage>(.+?)</(?:ns\d+:)?errorMessage>', result_xml)
            if errors:
                print(f"  [clé {key} / {type_abs}] ERREUR création : {errors}")
            else:
                new_key = get_absence_key(MATRICULE, new_deb, new_fin, type_abs)
                print(f"  [clé {key} / {type_abs}] {old_deb} → {new_deb} OK (nouvelle clé {new_key})")
        except Exception as e:
            print(f"  ERREUR [clé {key} / {type_abs}] : {e}")

    # --- 5. Relire après modification ---
    afficher_absences("[5] Absences après modification")
