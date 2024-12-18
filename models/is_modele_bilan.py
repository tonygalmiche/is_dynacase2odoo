# -*- coding: utf-8 -*-
from odoo import models, fields


class IsModeleBilan(models.Model):
    _name        = "is.modele.bilan"
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Modèle bilan projet"
    _rec_name    = "mb_titre"
    _order       = 'mb_titre'

    mb_titre = fields.Char(string="Titre du modèle",required=True, tracking=True)
    mb_cp    = fields.Char(string="Chef de projet", tracking=True)
    mb_cpid  = fields.Integer(string="Chef de projet id", tracking=True)
    mb_type  = fields.Selection([
            ("Moule", "Moule"),
            ("Article", "Article"),
        ], string='Type de modèle',required=True, tracking=True)
    line_ids    = fields.One2many('is.modele.bilan.line', 'modele_bilan_id', string="Lignes")
    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)
    active      = fields.Boolean('Actif', default=True, tracking=True)


    def get_famille_ids(self):
        for obj in self:
            ids=[]
            for line in obj.line_ids:
                ids.append(line.param_project_id.id)
            return ids


class IsModeleBilanLine(models.Model):
    _name        = "is.modele.bilan.line"
    _description = "Lignes modèle bilan projet"
    _rec_name    = "mb_document"
    _order       = 'sequence,lig'

    modele_bilan_id  = fields.Many2one("is.modele.bilan", string="Modèle bilan", required=True, ondelete='cascade')
    sequence         = fields.Integer(string="Ordre")
    lig              = fields.Integer(string="Lig",index=True,copy=False,readonly=True, help="Permet de faire le lien avec la ligne du tableau dans Dynacase")
    mb_document      = fields.Char(string="Documents du bilan")
    mb_documentid    = fields.Integer(string="Documents du bilan id")
    param_project_id = fields.Many2one("is.param.project", string="Famille")
    mb_champ         = fields.Char(string="Champ")
    mb_champid       = fields.Char(string="Champ id")


	