# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools


class IsParamProject(models.Model):
    _name        = "is.param.project"
    _description = "Paramétrage projet"
    _rec_name    = "ppr_famille"
    _order = 'sequence, ppr_famille'

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

    sequence = fields.Integer(string="Ordre")

    ppr_icon                = fields.Image(string="Icône")
    ppr_famille             = fields.Char(string="Famille", required=True)
    ppr_transformation_pdf  = fields.Boolean(string="Transformation en PDF")
    type_document = fields.Selection([
        ("Moule"                 , "Moule"),
        ("Dossier F"             , "Dossier F"),
        ("Article"               , "Article"),
        ("Dossier Modif Variante", "Dossier Modif Variante"),
    ],string="Type de document", default="Moule", required=True)
    ppr_dossier_fab         = fields.Boolean(string="Famille du dossier de fabrication")
    ppr_demande             = fields.Char(string="Demande")
    ppr_type_demande        = fields.Selection([
        ("PJ",       "Pièce-jointe"),
        ("DATE",     "Date"),
        ("TEXTE",    "Texte"),
        ("PJ_TEXTE", "Pièce-jointe et texte"),
        ("PJ_DATE",  "Pièce-jointe et date"),
        ("AUTO",     "Automatique"),
    ], string="Type de demande", required=True, default='PJ')
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
    ppr_moule_hors_auto = fields.Boolean(string="Famille pour moule hors automobile")
    array_ids           = fields.One2many('is.param.project.array', 'param_project_id')
    ppr_project_colors  = fields.Serialized()
    ppr_color           = fields.Char("Color", sparse="ppr_project_colors")
    dynacase_id         = fields.Integer(string="Id Dynacase",index=True)
    duree               = fields.Integer("Durée par défaut (J)"   , help="Utilisée dans le Gantt")
    duree_attente_avant = fields.Integer("Durée attente avant (J)", help="Utilisée dans le Gantt")
    dependance_id       = fields.Many2one("is.param.project", string="Dépendance")


    def creer_css_action(self):
        for obj in self:
            addons_path = tools.config['addons_path'].split(',')[1]
            path = "%s/is_dynacase2odoo/static/src/css/is.param.project.css"%addons_path
            f = open(path, "w")
            f.write("/*Ne pas modifier ce fichier, car il est généré automatiquement par l'action creer_css_action pour dhtmlxgantt_project*/\n\n")
            lines=self.env['is.param.project'].search([])
            for line in lines:
                #color = line.ppr_color
                #h = color.lstrip('#')
                #rgb = tuple(str(int(h[i:i+2], 16)) for i in (0, 2, 4))
                #f.write("/* %s */\n"%(line.ppr_famille))
                #rgba="rgba(%s,1)"%(','.join(rgb))
                #f.write(".dhtmlxgantt_project .is_param_projet_%s{\n    background:%s;\n}\n"%(line.id,rgba))
                #rgba="rgba(%s,0.5)"%(','.join(rgb))
                #f.write(".dhtmlxgantt_project .is_param_projet_%s .gantt_task_progress{\n    background:%s;\n}\n\n"%(line.id,rgba))
                #f.write(".dhtmlxgantt_project .is_param_projet_%s{\n    background:%s;\n    opacity: 1;\n}\n"%(line.id,line.ppr_color))
                #f.write(".dhtmlxgantt_project .is_param_projet_%s .gantt_task_progress{\n    background:%s;\n    opacity: 0.5;\n}\n\n"%(line.id,line.ppr_color))
                f.write(".dhtmlxgantt_project .is_param_projet_%s{\n    background:%s;\n}\n"%(line.id,line.ppr_color))
                f.write(".dhtmlxgantt_project .is_param_projet_%s .gantt_task_progress{\n    opacity: 0.5;\n}\n\n"%(line.id))
            f.close()


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


