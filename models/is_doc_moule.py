# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import format_date, formatLang, frozendict


class IsDocMoule(models.Model):
    _name        = "is.doc.moule"
    _description = "Document moule"
    _rec_name    = "param_project_id"


    def compute_project_prev(self):
        "for xml-rpc"
        self._compute_project_prev()
        return True

    @api.depends('param_project_id', 'param_project_id.ppr_color', 'param_project_id.ppr_icon')
    def _compute_project_prev(self):
        for record in self:
            project_prev = ""
            if record.param_project_id:
                img_src = ""
                if record.param_project_id.ppr_icon:
                    img_src = "<img class ='img-fluid' src='data:image/gif;base64," + str(record.param_project_id.ppr_icon,'utf-8') + "' height='60' width='60' />"
                new_add = "<div height='60px' width='100%' style='padding: 10px;margin-bottom:20px;font-size:18px;background-color: " + str(record.param_project_id.ppr_color or '') + ";'> " + img_src + " " + str(record.param_project_id.ppr_famille or '') + "</div>"
                project_prev += str(new_add)
            record.project_prev = project_prev

    project_prev     = fields.Html(compute='_compute_project_prev', store=True)
    project_prev2 = fields.Html()
    param_project_id = fields.Many2one("is.param.project", string="Famille de document")
    ppr_type_demande = fields.Selection(related="param_project_id.ppr_type_demande", selection=[
        ("PJ",       "Pièce-jointe"),
        ("DATE",     "Date"),
        ("TEXTE",    "Texte"),
        ("PJ_TEXTE", "Pièce-jointe et texte"),
        ("PJ_DATE",  "Pièce-jointe et date"),
        ("AUTO",     "Automatique"),
    ], string="Type de demande", store=True)
    ppr_icon         = fields.Image(related="param_project_id.ppr_icon", string="Icône", store=True)
    ppr_color        = fields.Char(related="param_project_id.ppr_color", string="Color", store=True)
    dynacase_id      = fields.Integer(string="Id dans Dynacase")
    idmoule          = fields.Many2one("is.mold", string="Moule")
    idproject        = fields.Many2one(related="idmoule.project", string="Projet")
    idcp             = fields.Many2one(related="idmoule.chef_projet_id", string="CP")
    idresp           = fields.Many2one("res.users", string="Responsable")
    actuelle         = fields.Char(string="J Actuelle")
    demande          = fields.Char(string="Demande")
    action           = fields.Selection([
        ("I", "Initialisation"),
        ("R", "Révision"),
        ("V", "Validation"),
    ], string="Action")
    bloquant         = fields.Boolean(string="Point Bloquant")
    etat             = fields.Selection([
        ("AF", "A Faire"),
        ("F", "Fait"),
        ("D", "Dérogé"),
    ], string="État")
    fin_derogation   = fields.Date(string="Date de fin de dérogation")
    coefficient      = fields.Integer(string="Coefficient")
    note             = fields.Integer(string="Note")
    indicateur       = fields.Char(string="Indicateur")
    datecreate       = fields.Date(string="Date de création", default=fields.Date.context_today)
    dateend          = fields.Date(string="Date de fin")
    array_ids        = fields.One2many("is.doc.moule.array", "is_doc_id", string="Pièce-jointe de réponse à la demande")


class IsDocMouleArray(models.Model):
    _name        = "is.doc.moule.array"
    _description = "Document moule array"

    annex_pdf   = fields.Many2many("ir.attachment", "attach_annex_pdf_rel", "annex_pdf_id", "att_id", string="Fichiers PDF")
    annex       = fields.Many2many("ir.attachment", "attach_annex_rel", "annex_id", "attachment_id", string="Fichiers")
    demandmodif = fields.Char(string="Demande de modification")
    maj_amdec   = fields.Boolean(string="Mise à jour de l’AMDEC")
    comment     = fields.Text(string="Commentaire")
    rsp_date    = fields.Date(string="Date")
    rsp_texte   = fields.Char(string="Réponse à la demande")
    is_doc_id   = fields.Many2one("is.doc.moule")
