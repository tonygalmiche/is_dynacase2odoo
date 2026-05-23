# API Kelio — Gestion des absences via Web Services SOAP

Documentation basée sur Kelio V5.1M6.  
Référence officielle : https://kelio.help.kelio.io/V5.1M6/fr-FR/webservices/absences.html

---

## Prérequis

```bash
pip install zeep requests
```

Authentification : **HTTP Basic Auth** (login/mot de passe du compte Web Service Kelio).

```python
KELIO_BASE_URL = "https://xxx.kelio.io"
KELIO_USER     = "xxx"
KELIO_PASSWORD = "..."
```

---

## Points importants / pièges

### 1. zeep ne sérialise pas les champs hérités

`AbsenceFile` hérite de `EmployeeInformation`. zeep ne sérialise pas les champs de la classe parente via `type_factory` → la requête XML est envoyée vide.

**Solution** : construire le XML SOAP à la main et l'envoyer via `requests` directement.

### 2. SOAPAction obligatoire

Sans l'en-tête `SOAPAction`, Kelio route la requête vers le portail web et retourne une page HTML (HTTP 500).

Chaque méthode a sa propre valeur :

| Méthode                        | SOAPAction                              |
|--------------------------------|-----------------------------------------|
| `importAbsenceFiles`           | `urn:importAbsenceFiles`                |
| `deleteAbsenceFiles`           | `urn:deleteAbsenceFiles`                |
| `exportAbsenceFiles`           | `urn:exportAbsenceFiles`                |
| `deleteAbsenceFilesBetweenTwoDates` | `urn:deleteAbsenceFilesBetweenTwoDates` |

### 3. Champs hérités dans les réponses zeep (strict=False)

En lecture avec `strict=False`, les champs de la classe parente (`employeeIdentificationNumber`, `employeeSurname`, etc.) sont dans `_raw_elements` et retournent `None` par `getattr`. Utiliser une fonction helper :

```python
NS = "http://echange.service.open.bodet.com"

def get_raw(obj, field_name):
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
```

### 4. Pas de méthode update

Il n'existe pas de `updateAbsenceFiles`. Pour modifier une absence, il faut :
1. `deleteAbsenceFiles` avec la clé de l'absence existante
2. `importAbsenceFiles` avec les nouvelles valeurs

Kelio génère un **nouvel `absenceFileKey`** à chaque création (auto-incrémenté).

### 5. Doublon détecté par Kelio sur (matricule + startDate + endDate + type)

Si une absence identique existe déjà, Kelio retourne `errorMessage = "Absence déjà existante"` dans `absenceFilesInError`.

---

## Services WSDL utilisés

| Service               | URL WSDL                                              |
|-----------------------|-------------------------------------------------------|
| `AbsenceFileService`  | `{BASE_URL}/open/services/AbsenceFileService?wsdl`    |
| `TypeService`         | `{BASE_URL}/open/services/TypeService?wsdl`           |
| `LightEmployeeService`| `{BASE_URL}/open/services/LightEmployeeService?wsdl`  |

---

## Créer un client zeep (lecture uniquement)

```python
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth

def get_client(service="AbsenceFileService", strict=False):
    wsdl_url = f"{KELIO_BASE_URL}/open/services/{service}?wsdl"
    session = Session()
    session.auth = HTTPBasicAuth(KELIO_USER, KELIO_PASSWORD)
    transport = Transport(session=session)
    settings = Settings(strict=strict, xml_huge_tree=True)
    return Client(wsdl=wsdl_url, transport=transport, settings=settings)
```

`strict=False` est nécessaire pour ignorer les champs inconnus dans les réponses (ex: `defaultExternalReferenceType` dans `TypeService`).

---

## Lire les types d'absences

**Service** : `TypeService`  
**Méthode** : `exportAbsenceTypes`

```python
client = get_client("TypeService", strict=False)
result = client.service.exportAbsenceTypes()
types = result if isinstance(result, list) else (result.exportedAbsenceTypes or [])

for t in types:
    abrev = get_raw(t, 'typeAbbreviation')
    label = get_raw(t, 'typeDescription')
    print(f"{abrev} | {label}")
```

**Exemple de résultat (Plastigray)** :

| Abrégé | Libellé           |
|--------|-------------------|
| CP     | 0.Congés Payés    |
| RTT    | 1. RTT            |
| RCR    | 2.RCR             |

---

## Lire les absences

**Service** : `AbsenceFileService`  
**Méthode** : `exportAbsenceFiles`

```python
from datetime import date

client = get_client(strict=False)
result = client.service.exportAbsenceFiles(
    populationFilter=None,
    groupFilter=None,
    startDate=date(2026, 1, 1),
    endDate=date(2026, 12, 31),
)
absences = result if isinstance(result, list) else (result.exportedAbsenceFiles or [])

for a in absences:
    print(
        get_raw(a, 'employeeIdentificationNumber'),
        get_raw(a, 'employeeSurname'),
        a.absenceTypeAbbreviation,
        a.startDate, a.endDate,
        a.absenceFileKey,
    )
```

**Champs disponibles sur chaque `AbsenceFile`** :

| Champ                           | Type    | Description                          |
|---------------------------------|---------|--------------------------------------|
| `absenceFileKey`                | int     | Identifiant unique Kelio             |
| `absenceTypeAbbreviation`       | str     | Abréviation du type (CP, RTT…)       |
| `startDate` / `endDate`         | date    | Période de l'absence                 |
| `startInTheMorning`             | bool    | Début le matin                       |
| `endingTheAfternoon`            | bool    | Fin l'après-midi                     |
| `employeeIdentificationNumber`  | str     | Matricule du salarié *(hérité)*      |
| `employeeBadgeCode`             | str     | Code badge *(hérité)*                |
| `employeeSurname`               | str     | Nom *(hérité)*                       |
| `employeeFirstName`             | str     | Prénom *(hérité)*                    |
| `employeeKey`                   | int     | Clé interne Kelio de l'employé       |
| `errorMessage`                  | str     | Message d'erreur (null si OK)        |

> Les champs marqués *(hérité)* sont dans `_raw_elements`, utiliser `get_raw()`.

---

## Créer une absence

**Service** : `AbsenceFileService`  
**Méthode** : `importAbsenceFiles`  
**SOAPAction** : `urn:importAbsenceFiles`

La requête XML doit être construite manuellement (zeep ne sérialise pas les champs hérités).

```python
import requests

def creer_absence(matricule, start_date, end_date, type_absence,
                  start_in_morning=True, ending_the_afternoon=True):
    NS = "http://echange.service.open.bodet.com"
    body = f"""<?xml version='1.0' encoding='utf-8'?>
<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
  <soap-env:Body>
    <ns0:importAbsenceFiles xmlns:ns0="{NS}">
      <ns0:absenceFilesToImport>
        <ns0:AbsenceFile xmlns:ns0="{NS}">
          <ns0:employeeIdentificationNumber>{matricule}</ns0:employeeIdentificationNumber>
          <ns0:startDate>{start_date}</ns0:startDate>
          <ns0:endDate>{end_date}</ns0:endDate>
          <ns0:absenceTypeAbbreviation>{type_absence}</ns0:absenceTypeAbbreviation>
          <ns0:startInTheMorning>{"true" if start_in_morning else "false"}</ns0:startInTheMorning>
          <ns0:endingTheAfternoon>{"true" if ending_the_afternoon else "false"}</ns0:endingTheAfternoon>
        </ns0:AbsenceFile>
      </ns0:absenceFilesToImport>
    </ns0:importAbsenceFiles>
  </soap-env:Body>
</soap-env:Envelope>"""

    url = f"{KELIO_BASE_URL}/open/services/AbsenceFileService"
    headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "urn:importAbsenceFiles"}
    response = requests.post(url, data=body.encode("utf-8"), headers=headers,
                             auth=(KELIO_USER, KELIO_PASSWORD), timeout=30)
    if not response.ok:
        raise Exception(f"HTTP {response.status_code} — {response.text[:500]}")
    return response.text
```

**Vérifier le résultat** :

```python
import re

result_xml = creer_absence("0000000970", date(2026, 6, 1), date(2026, 6, 1), "CP")
errors = re.findall(r'<(?:ns\d+:)?errorMessage>(.+?)</(?:ns\d+:)?errorMessage>', result_xml)
if errors:
    print("ERREUR :", errors)  # ex: ['Absence déjà existante']
else:
    print("OK")
```

> La réponse ne contient **pas** l'`absenceFileKey` créée. Pour l'obtenir, relire avec `exportAbsenceFiles` et filtrer sur matricule + date + type.

---

## Récupérer la clé après création

```python
def get_absence_key(matricule, start_date, end_date, type_absence):
    absences = lire_absences(start_date, end_date)
    for a in absences:
        mat = get_raw(a, 'employeeIdentificationNumber') or ''
        if (mat == matricule
                and str(a.startDate) == str(start_date)
                and str(a.endDate) == str(end_date)
                and getattr(a, 'absenceTypeAbbreviation', '') == type_absence):
            return getattr(a, 'absenceFileKey', None)
    return None

key = get_absence_key("0000000970", date(2026, 6, 1), date(2026, 6, 1), "CP")
# → 12
```

---

## Supprimer une absence

**Méthode** : `deleteAbsenceFiles`  
**SOAPAction** : `urn:deleteAbsenceFiles`

```python
def supprimer_absence(absence_file_key):
    NS = "http://echange.service.open.bodet.com"
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

    url = f"{KELIO_BASE_URL}/open/services/AbsenceFileService"
    headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "urn:deleteAbsenceFiles"}
    response = requests.post(url, data=body.encode("utf-8"), headers=headers,
                             auth=(KELIO_USER, KELIO_PASSWORD), timeout=30)
    if not response.ok:
        raise Exception(f"HTTP {response.status_code} — {response.text[:500]}")
    return response.text
```

---

## Modifier une absence (suppression + recréation)

```python
def modifier_absence(matricule, absence_file_key, type_absence,
                     new_start_date, new_end_date,
                     start_in_morning=True, ending_the_afternoon=True):
    # 1. Supprimer l'ancienne absence
    supprimer_absence(absence_file_key)

    # 2. Supprimer une éventuelle absence déjà existante à la date cible
    existing_key = get_absence_key(matricule, new_start_date, new_end_date, type_absence)
    if existing_key is not None:
        supprimer_absence(existing_key)

    # 3. Créer avec les nouvelles valeurs
    result_xml = creer_absence(matricule, new_start_date, new_end_date, type_absence,
                                start_in_morning, ending_the_afternoon)
    errors = re.findall(r'<(?:ns\d+:)?errorMessage>(.+?)</(?:ns\d+:)?errorMessage>', result_xml)
    if errors:
        raise Exception(f"Erreur création : {errors}")

    # 4. Récupérer la nouvelle clé
    return get_absence_key(matricule, new_start_date, new_end_date, type_absence)

# Exemple
new_key = modifier_absence(
    matricule="0000000970",
    absence_file_key=31,
    type_absence="CP",
    new_start_date=date(2026, 8, 1),
    new_end_date=date(2026, 8, 1),
)
print(f"Nouvelle clé : {new_key}")  # → 34
```

> L'`absenceFileKey` change à chaque modification car Kelio crée une nouvelle entrée.

---

## Modes de saisie disponibles

| Mode                  | Champs à renseigner                                      |
|-----------------------|----------------------------------------------------------|
| Date à date (journée) | `startDate`, `endDate`                                   |
| Demi-journée          | `startDate`, `endDate`, `startInTheMorning=False` ou `endingTheAfternoon=False` |
| D'heure à heure       | `startDate = endDate`, `firstStartTime`, `firstEndTime`  |
| Durée imputée         | `startDate = endDate` + offset en minutes                |
