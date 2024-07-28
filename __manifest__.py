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
        "security/ir.model.access.csv",
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
         ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}

