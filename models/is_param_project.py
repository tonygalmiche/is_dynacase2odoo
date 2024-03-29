# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IsParamProject(models.Model):
    _name        = "is.param.project"
    _description = "Paramétrage projet"
    _rec_name    = "ppr_famille"

    @api.model
    def default_get(self, fields):
        res = super(IsParamProject, self).default_get(fields)
        array_vals = [
            (0, 0, {'ppp_j': 'J0'}),
            (0, 0, {'ppp_j': 'J1'}),
            (0, 0, {'ppp_j': 'J2'}),
            (0, 0, {'ppp_j': 'J3'}),
            (0, 0, {'ppp_j': 'J4'}),
            (0, 0, {'ppp_j': 'J5'}),
        ]
        res.update({
            'array_ids': array_vals,
        })
        return res

    ppr_icon                = fields.Image(string="Icône")
    ppr_famille             = fields.Char(string="Famille")
    ppr_transformation_pdf  = fields.Boolean(string="Transformation en PDF")
    type_document = fields.Selection([
        ("Moule",       "Moule"),
        ("Article",     "Article"),
    ],string="Type de document", default="Moule")
    ppr_dossier_fab         = fields.Boolean(string="Famille du dossier de fabrication")
    ppr_demande             = fields.Char(string="Demande")
    ppr_type_demande        = fields.Selection([
        ("PJ",       "Pièce-jointe"),
        ("DATE",     "Date"),
        ("TEXTE",    "Texte"),
        ("PJ_TEXTE", "Pièce-jointe et texte"),
        ("PJ_DATE",  "Pièce-jointe et date"),
        ("AUTO",     "Automatique"),
    ], string="Type de demande")
    ppr_maj_amdec          = fields.Selection([
        ("Oui", "Oui"),
        ("Non", "Non"),
    ], string="Mise à jour de l’AMDEC")
    ppr_responsable        = fields.Selection([
        ("1",  "1-Commercial"),
        ("2",  "2-Chef de projet"),
        ("3",  "3-Responsable outillage"),
        ("4",  "4-Expert injection"),
        ("5",  "5-Méthode injection"),
        ("6",  "6-Methode assemblage"),
        ("7",  "7-Qualité développement"),
        ("8",  "8-Qualité usine"),
        ("9",  "9-Logistique"),
        ("10", "10-Logistique Usine"),
        ("11", "11-Achats"),
        ("12", "12-Responsable projets"),
    ], string="Responsable du document")
    ppr_revue_lancement    = fields.Selection([
        ("rl_be01",  "BE01a : Nouveau moule - Moule transféré"),
        ("rl_be01b", "BE01b : Grainage"),
        ("rl_be01c", "BE01c : Barre chaude"),
        ("rl_be02",  "BE02 : Etude - CAO - Rhéologie"),
        ("rl_be03",  "BE03 : Prototype"),
        ("rl_be04",  "BE04 : Main de préhension"),
        ("rl_be05",  "BE05 : Gabarit de contrôle"),
        ("rl_be06",  "BE06 : Mise au point"),
        ("rl_be07",  "BE07 : Test"),
        ("rl_be09",  "BE09 : Essais + divers"),
        ("rl_be10",  "BE10 : Métrologie"),
        ("rl_be11",  "BE11 : Transports"),
        ("rl_be12",  "BE12 : Etude - Developpement - Packaging"),
        ("rl_be13",  "BE13 : Poste d'assemblage"),
        ("rl_be15",  "BE15 : Achat matière"),
        ("rl_be16",  "BE16 : Achat composants"),
        ("rl_be17",  "BE17 : Essai injection"),
    ], string="Revue de lancement")
    ppr_moule_hors_auto    = fields.Boolean(string="Famille pour moule hors automobile")
    array_ids              = fields.One2many('is.param.project.array', 'param_project_id')
    ppr_project_colors     = fields.Serialized()
    ppr_color              = fields.Char("Color", sparse="ppr_project_colors")


class IsParamProjectArray(models.Model):
    _name        = "is.param.project.array"
    _description = "Paramétrage projet array"
    _rec_name    = "ppp_j"

    ppp_j            = fields.Char(string="J")
    ppr_irv          = fields.Selection([
        ("I", "Initialisation"),
        ("R", "Révision"),
        ("V", "Validation"),
    ])
    ppr_bloquant     = fields.Boolean(string="Action")
    param_project_id = fields.Many2one("is.param.project", string="Point bloquant")
