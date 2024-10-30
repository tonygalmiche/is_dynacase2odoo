# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools # type: ignore

TYPE_DOCUMENT=[
    ("Moule"                 , "Moule"),
    ("Dossier F"             , "Dossier F"),
    ("Article"               , "Article"),
    ("Dossier Modif Variante", "Dossier Modif Variante"),
    ("dossier_appel_offre"   , "Dossier appel d'offre"),
]


MODELE_TO_TYPE=[
    ("is.mold"                  , "Moule"),
    ("is.dossierf"              , "Dossier F"),
    ("is.dossier.article"       , "Article"),
    ("is.dossier.modif.variante", "Dossier Modif Variante"),
    ("is.dossier.appel.offre"   , "dossier_appel_offre"),
]


TYPE_TO_FIELD={
    "Moule"                 : "idmoule",
    "Dossier F"             : "dossierf_id",
    "Article"               : "dossier_article_id",
    "Dossier Modif Variante": "dossier_modif_variante_id",
    "dossier_appel_offre"   : "dossier_appel_offre_id",
}


GESTION_J=[
    ("J0", "Préparation J0"),
    ("J1", "Préparation J1"),
    ("J2", "Préparation J2"),
    ("J3", "Préparation J3"),
    ("J4", "Préparation J4"),
    ("J5", "Préparation J5"),
    ("J6", "J5 validé"),
]


DOCUMENT_ACTION=[
    ("I", "Initialisation"),
    ("R", "Révision"),
    ("V", "Validation"),
]


DOCUMENT_ETAT = [
    ("AF", "A Faire"),
    ("F", "Fait"),
    ("D", "Dérogé"),
]


class IsSectionGantt(models.Model):
    _name        = "is.section.gantt"
    _description = "Sections du Gantt"
    _order = 'sequence, id'

    sequence  = fields.Integer(string="Ordre",index=True)
    name      = fields.Char("Section",required=True,index=True)
    gantt_pdf = fields.Boolean("Gantt PDF", default=True, help="Afficher dans Gantt PDF")
    color     = fields.Char("Color")


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
    ppr_familleid           = fields.Integer(string="Famille Id")
    ppr_transformation_pdf  = fields.Boolean(string="Transformation en PDF")
    type_document           = fields.Selection(TYPE_DOCUMENT,string="Type de document", default="Moule", required=True)
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
    ppr_project_colors  = fields.Serialized()
    ppr_color           = fields.Char("Color", sparse="ppr_project_colors")
    dynacase_id         = fields.Integer(string="Id Dynacase"     ,index=True,copy=False)
    duree               = fields.Integer("Durée par défaut (J)"   , help="Utilisée dans le Gantt")
    duree_attente_avant = fields.Integer("Durée attente avant (J)", help="Utilisée dans le Gantt")
    dependance_id       = fields.Many2one("is.param.project", string="Dépendance")
    gantt_pdf           = fields.Boolean("Gantt PDF", default=True, help="Afficher dans Gantt PDF")
    array_ids           = fields.One2many('is.param.project.array', 'param_project_id')
    array_html          = fields.Html(string="Gestion des J", compute='_compute_array_html',store=True, readonly=True)


    @api.depends('array_ids','array_ids.ppr_irv','array_ids.ppr_bloquant')
    def _compute_array_html(self):
        for obj in self:
            html='<table style="width:120px">'
            for line in obj.array_ids:
                bloquant=''
                if line.ppr_bloquant:
                    bloquant='Bloquant'
                html+='<tr><td style="width:25%%">%s</td><td style="width:25%%">%s</td><td style="width:50%%">%s</td></tr>'%(line.ppp_j,line.ppr_irv or '',bloquant)

            html+='</table>'
            obj.array_html = html


    def creer_css_action(self):
        for obj in self:
            addons_path = tools.config['addons_path'].split(',')[1]
            path = "%s/is_dynacase2odoo/static/src/css/is.param.project.css"%addons_path
            f = open(path, "w")
            f.write("/*Ne pas modifier ce fichier, car il est généré automatiquement par l'action creer_css_action pour dhtmlxgantt_project*/\n\n")
            lines=self.env['is.param.project'].search([])
            for line in lines:
                f.write(".dhtmlxgantt_project .is_param_projet_%s{\n    background:%s;\n}\n"%(line.id,line.ppr_color))
                f.write(".dhtmlxgantt_project .is_param_projet_%s .gantt_task_progress{\n    opacity: 0.5;\n}\n\n"%(line.id))
            lines=self.env['is.section.gantt'].search([])
            for line in lines:
                f.write(".dhtmlxgantt_project .is_section_gantt_%s{\n    background:%s;\n}\n"%(line.id,line.color))
                f.write(".dhtmlxgantt_project .is_section_gantt_%s .gantt_task_progress{\n    opacity: 0.5;\n}\n\n"%(line.id))
            f.close()



    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }





class IsParamProjectArray(models.Model):
    _name        = "is.param.project.array"
    _description = "Paramétrage projet array"
    _rec_name    = "ppp_j"

    ppp_j   = fields.Selection(GESTION_J, string="J")
    ppr_irv = fields.Selection(DOCUMENT_ACTION, string="Action")
    ppr_bloquant     = fields.Boolean(string="Bloquant")
    param_project_id = fields.Many2one("is.param.project", string="Famille")


