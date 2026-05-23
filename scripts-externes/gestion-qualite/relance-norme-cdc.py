#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relance par e-mail pour les Normes CDC dont la date de prochaine alerte est dépassée
et dont la date de dernière vérification est vide ou antérieure à la date d'alerte.

L'e-mail est envoyé à la liste NORME_CDC_DESTINATAIRES définie dans config.py,
via le serveur de messagerie sortant d'Odoo (XML-RPC).
"""

import sys
import os
import ssl
import xmlrpc.client
from datetime import date, datetime


def fmt_date(iso):
    """Convertit une date ISO (AAAA-MM-JJ) en JJ/MM/AAAA, ou chaîne vide."""
    if not iso:
        return ""
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return iso

# --- chemin vers config.py (répertoire parent du script) ---
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import ODOO_USER, ODOO_PASSWORD, DATABASES, SOURCE_DB, ROBOT_EMAIL, MAIL_TEST, MAIL_TEST_CC, NORME_CDC_DESTINATAIRES


# ---------------------------------------------------------------------------
# Connexion XML-RPC
# ---------------------------------------------------------------------------

def get_connection():
    cfg = DATABASES[SOURCE_DB]
    url = cfg["url"]
    db  = cfg["db"]

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", context=ctx, allow_none=True)
    uid = common.authenticate(db, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        raise SystemExit(f"Échec d'authentification sur {db}")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", context=ctx, allow_none=True)
    return db, uid, models


# ---------------------------------------------------------------------------
# Recherche des normes CDC à relancer
# ---------------------------------------------------------------------------

def get_normes_a_relancer(db, uid, models):
    today = date.today().isoformat()

    # Normes avec date_prochaine_alerte dépassée
    domain = [
        ("date_prochaine_alerte", "!=", False),
        ("date_prochaine_alerte", "<=", today),
    ]
    records = models.execute_kw(
        db, uid, ODOO_PASSWORD,
        "is.norme.cdc", "search_read",
        [domain],
        {"fields": ["id", "reference", "designation", "niveau", "indice",
                    "date_prochaine_alerte", "date_verif", "etat",
                    "lieu_physique", "lieu_info"]},
    )

    # Filtrage Python : date_verif vide OU date_verif < date_prochaine_alerte
    result = []
    for rec in records:
        date_alerte = rec.get("date_prochaine_alerte") or ""
        date_verif  = rec.get("date_verif") or ""
        if not date_verif or date_verif < date_alerte:
            result.append(rec)

    return result


# ---------------------------------------------------------------------------
# Envoi de l'e-mail récapitulatif
# ---------------------------------------------------------------------------

def send_relance(db, uid, models, normes):
    dest_email = MAIL_TEST if MAIL_TEST else ", ".join(NORME_CDC_DESTINATAIRES)

    if not dest_email:
        print("  [IGNORÉ] Aucun destinataire configuré.")
        return

    odoo_url = DATABASES[SOURCE_DB]["url"]
    lignes_html = ""
    for norme in normes:
        norme_id     = norme["id"]
        reference    = norme.get("reference") or f"ID {norme_id}"
        lien         = f"<a href='{odoo_url}/web#id={norme_id}&model=is.norme.cdc&view_type=form'>{reference}</a>"
        designation  = norme.get("designation") or ""
        niveau       = norme.get("niveau") or ""
        indice       = norme.get("indice") or ""
        date_alerte  = fmt_date(norme.get("date_prochaine_alerte"))
        date_verif   = fmt_date(norme.get("date_verif")) or "<em>non renseignée</em>"
        etat         = norme.get("etat") or ""
        lieu_phys    = norme.get("lieu_physique") or ""
        lieu_info    = norme.get("lieu_info") or ""
        lignes_html += (
            f"<tr>"
            f"<td style='border:1px solid #cccccc'>{lien}</td>"
            f"<td style='border:1px solid #cccccc'>{designation}</td>"
            f"<td style='border:1px solid #cccccc'>{niveau}</td>"
            f"<td style='border:1px solid #cccccc'>{indice}</td>"
            f"<td style='border:1px solid #cccccc'>{etat}</td>"
            f"<td style='border:1px solid #cccccc;color:red'>{date_alerte}</td>"
            f"<td style='border:1px solid #cccccc'>{date_verif}</td>"
            f"<td style='border:1px solid #cccccc'>{lieu_phys}</td>"
            f"<td style='border:1px solid #cccccc'>{lieu_info}</td>"
            f"</tr>\n"
        )

    today_str = date.today().strftime("%d/%m/%Y")
    subject = f"[Normes CDC] Vérification de mise à jour requise au {today_str}"
    body = f"""
<p>Bonjour,</p>

<p>Les normes / CDC suivantes ont une <strong>date de prochaine alerte dépassée</strong>
et leur date de dernière vérification est absente ou antérieure à la date d'alerte :</p>

<table style="border-collapse:collapse;width:100%" cellpadding="6" cellspacing="0">
    <thead>
        <tr style="background-color:#f2f2f2">
            <th style="border:1px solid #cccccc">Référence</th>
            <th style="border:1px solid #cccccc">Désignation / Projet</th>
            <th style="border:1px solid #cccccc">Niveau</th>
            <th style="border:1px solid #cccccc">Indice</th>
            <th style="border:1px solid #cccccc">État</th>
            <th style="border:1px solid #cccccc">Date prochaine alerte</th>
            <th style="border:1px solid #cccccc">Dernière vérification</th>
            <th style="border:1px solid #cccccc">Lieu physique</th>
            <th style="border:1px solid #cccccc">Lieu informatique</th>
        </tr>
    </thead>
    <tbody>
        {lignes_html}
    </tbody>
</table>

<p>Merci de vérifier la mise à jour de ces documents et de renseigner la
<strong>date de dernière vérification</strong> ainsi que la prochaine date d'alerte.</p>
"""

    mail_vals = {
        "subject":     subject,
        "body_html":   body,
        "email_from":  ROBOT_EMAIL,
        "email_to":    dest_email,
        "state":       "outgoing",
        "auto_delete": True,
    }
    if MAIL_TEST_CC:
        mail_vals["email_cc"] = MAIL_TEST_CC

    mail_id = models.execute_kw(
        db, uid, ODOO_PASSWORD,
        "mail.mail", "create",
        [mail_vals],
    )
    models.execute_kw(
        db, uid, ODOO_PASSWORD,
        "mail.mail", "write",
        [[mail_id], {"state": "outgoing"}],
    )

    # Post d'un message dans le chatter de chaque norme
    dest_display = ", ".join(NORME_CDC_DESTINATAIRES)
    for norme in normes:
        models.execute_kw(
            db, uid, ODOO_PASSWORD,
            "is.norme.cdc", "message_post",
            [[norme["id"]]],
            {
                "body": f"Relance automatique envoyée le {today_str} à {dest_display} (date de prochaine alerte dépassée).",
                "message_type": "comment",
                "subtype_xmlid": "mail.mt_note",
            },
        )

    suffix = f" [TEST → {dest_email}]" if MAIL_TEST else ""
    print(f"  [OK] {len(normes)} norme(s) — e-mail mis en file d'envoi{suffix}")


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main():
    print(f"Connexion à la base '{SOURCE_DB}' ({DATABASES[SOURCE_DB]['db']})...")
    db, uid, models = get_connection()
    print("Connexion établie.")

    print("\nRecherche des normes CDC à relancer...")
    normes = get_normes_a_relancer(db, uid, models)

    if not normes:
        print("Aucune norme CDC à relancer.")
        return

    print(f"{len(normes)} norme(s) trouvée(s) :")
    for n in normes:
        ref         = n.get("reference") or f"ID {n['id']}"
        designation = n.get("designation") or ""
        date_alerte = fmt_date(n.get("date_prochaine_alerte"))
        date_verif  = fmt_date(n.get("date_verif")) or "non renseignée"
        print(f"  - {ref} | {designation} | alerte : {date_alerte} | dernière vérif : {date_verif}")
    print()
    send_relance(db, uid, models, normes)
    print("\nTerminé.")


if __name__ == "__main__":
    main()
