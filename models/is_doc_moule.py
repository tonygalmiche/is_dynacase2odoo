# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IsDocMoule(models.Model):
    _name        = "is.doc.moule"
    _description = "Document moule"
    _rec_name    = "param_project_id"

    @api.onchange('IDMOULE')
    def _onchange_IDMOULE(self):
        if self.IDMOULE.project:
            self.IDPROJECT = self.IDMOULE.project.id
        if self.IDMOULE.chef_projet_id:
            self.IDCP = self.IDMOULE.chef_projet_id.id

    param_project_id = fields.Many2one("is.param.project", string="Project")
    ppr_type_demande = fields.Selection(related="param_project_id.ppr_type_demande", selection=[
        ("PJ",       "Pièce-jointe"),
        ("DATE",     "Date"),
        ("TEXTE",    "Texte"),
        ("PJ_TEXTE", "Pièce-jointe et texte"),
        ("PJ_DATE",  "Pièce-jointe et date"),
        ("AUTO",     "Automatique"),
    ], string="Type de demande", store=True)
    ppr_icon         = fields.Image(related="param_project_id.ppr_icon", string="Icône")
    ppr_color        = fields.Char(related="param_project_id.ppr_color", string="Color")
    dynacase_id      = fields.Integer(string="Id dans Dynacase")
    IDMOULE          = fields.Many2one("is.mold", string="Moule")
    IDPROJECT        = fields.Many2one("is.mold.project", string="Projet")
    IDCP             = fields.Many2one("res.users", string="CP")
    IDRESP           = fields.Many2one("res.users", string="Responsable")
    ACTUELLE         = fields.Char(string="J Actuelle")
    DEMANDE          = fields.Char(string="Demande")
    ACTION           = fields.Selection([
        ("I", "Initialisation"),
        ("R", "Révision"),
        ("V", "Validation"),
    ], string="Action")
    BLOQUANT         = fields.Boolean(string="Point Bloquant")
    ETAT             = fields.Selection([
        ("AF", "A Faire"),
        ("F", "Fait"),
        ("D", "Dérogé"),
    ], string="État")
    FIN_DEROGATION   = fields.Date(string="Date de fin de dérogation")
    COEFFICIENT      = fields.Integer(string="Coefficient")
    NOTE             = fields.Integer(string="Note")
    INDICATEUR       = fields.Char(string="Indicateur")
    DATECREATE       = fields.Date(string="Date de création", default=fields.Date.context_today)
    DATEEND          = fields.Date(string="Date de fin")
    array_ids        = fields.One2many("is.doc.moule.array", "is_doc_id", string="Pièce-jointe de réponse à la demande")


class IsDocMouleArray(models.Model):
    _name        = "is.doc.moule.array"
    _description = "Document moule array"

    ANNEX_PDF   = fields.Binary(string="Fichiers PDF")
    ANNEX       = fields.Binary(string="Fichiers")
    DEMANDMODIF = fields.Char(string="Demande de modification")
    MAJ_AMDEC   = fields.Boolean(string="Mise à jour de l’AMDEC")
    COMMENT     = fields.Text(string="Commentaire")
    RSP_DATE    = fields.Date(string="Date")
    RSP_TEXTE   = fields.Char(string="Réponse à la demande")
    is_doc_id   = fields.Many2one("is.doc.moule")
