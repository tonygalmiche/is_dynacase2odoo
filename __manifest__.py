# -*- coding: utf-8 -*-
{
    "name"     : "Module Odoo 16 pour Plastigray pour migrer les développements de Dynacase dans Odoo",
    "version"  : "0.1",
    "author"   : "InfoSaône",
    "category" : "InfoSaône",
    "description": """
Module Odoo 16 pour Plastigray pour migrer les développements de Dynacase dans Odoo
===================================================
""",
    "maintainer" : "InfoSaône",
    "website"    : "http://www.infosaone.com",
    "depends"    : [
        "utm",
        "is_plastigray16",
    ],
    "data" : [
        "security/res.groups.xml",
        "security/ir.model.access.csv",
        "security/ir.model.access.xml",
        "views/ir_attachment_view.xml",
        "views/is_param_project_view.xml",
        "views/is_doc_moule_view.xml",
        "views/is_revue_de_contrat_view.xml",
        "views/is_revue_lancement_view.xml",
        "views/is_dossier_modif_variante_view.xml",
        "views/is_revue_projet_jalon_view.xml",
        "views/is_revue_risque_view.xml",
        "views/is_dossier_appel_offre_view.xml",
        "views/is_fermeture_gantt_view.xml",
        "views/is_mold_project_view.xml",
        "views/is_gantt_pdf_view.xml",
        "views/is_gantt_copie_view.xml",
        "views/is_modele_bilan_view.xml",
        "views/is_mold_view.xml",
        "views/is_dossierf_view.xml",
        "views/is_creation_doc_migration_view.xml",
        "views/is_dossier_article_view.xml",
        "views/is_indicateur_revue_jalon_view.xml",
        "views/is_fiche_codification_view.xml",
        "views/is_fiche_information_prospect_view.xml",
        "views/is_plan_action_view.xml",
        "views/is_plan_amelioration_continu_view.xml",
        "views/is_modif_donnee_technique_view.xml",
        "views/is_prise_avance_view.xml",
        "views/is_demande_modif_compte_fournisseur_view.xml",
        "views/is_demande_modif_tarif_fournisseur_view.xml",
        "views/is_inv_achat_moule_view.xml",
        "views/is_erd_view.xml",
        "views/is_liste_diffusion_mail_view.xml",
        "views/is_facture_outillage_view.xml",
        "views/report_is_inv_achat_moule.xml",
        "views/menu.xml",
    ], 
    "qweb": [
    ],
    "assets": {
        'web.assets_backend': [
            'is_dynacase2odoo/static/src/css/*',
            'is_dynacase2odoo/static/lib/dhtmlxGantt/*',
            'is_dynacase2odoo/static/src/dhtmlxgantt_project/*',
            'is_dynacase2odoo/static/src/background_color/*',
            'is_dynacase2odoo/static/src/suivi_projet/*',

            'is_dynacase2odoo/static/src/js/*',


         ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}

