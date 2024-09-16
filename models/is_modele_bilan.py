# -*- coding: utf-8 -*-
from odoo import models, fields


class IsModeleBilan(models.Model):
    _name        = "is.modele.bilan"
    _description = "Modèle bilan projet"
    _rec_name    = "mb_titre"
    _order       = 'mb_titre'

    mb_titre = fields.Char(string="Titre du modèle",required=True)
    mb_cp    = fields.Char(string="Chef de projet")
    mb_cpid  = fields.Integer(string="Chef de projet id")
    mb_type  = fields.Selection([
            ("Moule", "Moule"),
            ("Article", "Article"),
        ], string='Type de modèle',required=True)
    line_ids    = fields.One2many('is.modele.bilan.line', 'modele_bilan_id', string="Lignes")
    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)


class IsModeleBilanLine(models.Model):
    _name        = "is.modele.bilan.line"
    _description = "Lignes modèle bilan projet"
    _rec_name    = "mb_document"
    _order       = 'lig'

    modele_bilan_id = fields.Many2one("is.modele.bilan", string="Modèle bilan", required=True, ondelete='cascade')
    lig             = fields.Integer(string="Lig",index=True,copy=False,readonly=True, help="Permet de faire le lien avec la ligne du tableau dans Dynacase")
    mb_document     = fields.Char(string="Documents du bilan",required=True)
    mb_documentid   = fields.Integer(string="Documents du bilan id")
    mb_champ        = fields.Char(string="Champ")
    mb_champid      = fields.Integer(string="Champ id")


	