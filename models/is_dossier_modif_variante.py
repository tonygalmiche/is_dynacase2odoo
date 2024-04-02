# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class is_dossier_modif_variante(models.Model):
    _name        = "is.dossier.modif.variante"
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Dossier modif/variante"
    _rec_name    = "demao_num"

    @api.depends("state")
    def _compute_vsb(self):
        for obj in self:
            vsb = False
            if obj.state in ["cree", "transmis_be"]:
                vsb = True
            obj.vers_analyse_vsb = vsb
            vsb = False
            if obj.state in ["analyse", "analyse_be", "relance_client", "diffuse_client"]:
                vsb = True
            obj.vers_transmis_be_vsb = vsb
            vsb = False
            if obj.state in ["transmis_be", "vali_de_be"]:
                vsb = True
            obj.vers_analyse_be_vsb = vsb
            vsb = False
            if obj.state in ["analyse_be"]:
                vsb = True
            obj.vers_vali_de_be_vsb = vsb
            vsb = False
            if obj.state in ["vali_de_be"]:
                vsb = True
            obj.vers_vali_de_commercial_vsb = vsb
            vsb = False
            if obj.state in ["vali_de_commercial", "analyse", "perdu", "gagne", "annule"]:
                vsb = True
            obj.vers_diffuse_client_vsb = vsb
            vsb = False
            if obj.state in ["diffuse_client"]:
                vsb = True
            obj.vers_relance_client_vsb = vsb
            vsb = False
            if obj.state in ["relance_client", "diffuse_client"]:
                vsb = True
            obj.vers_perdu_vsb = vsb
            vsb = False
            if obj.state in ["relance_client", "diffuse_client"]:
                vsb = True
            obj.vers_gagne_vsb = vsb
            vsb = False
            if obj.state in ["relance_client", "diffuse_client"]:
                vsb = True
            obj.vers_annule_vsb = vsb

    def vers_analyse_action(self):
        for obj in self:
            obj.sudo().state = "analyse"

    def vers_transmis_be_action(self):
        for obj in self:
            obj.sudo().state = "transmis_be"

    def vers_vers_analyse_be_vsb_action(self):
        for obj in self:
            obj.sudo().state = "analyse_be"

    def vers_vali_de_be_vsb_action(self):
        for obj in self:
            obj.sudo().state = "vali_de_be"

    def vers_vali_de_commercial_vsb_action(self):
        for obj in self:
            obj.sudo().state = "vali_de_commercial"

    def vers_diffuse_client_vsb_action(self):
        for obj in self:
            obj.sudo().state = "diffuse_client"

    def vers_relance_client_vsb_action(self):
        for obj in self:
            obj.sudo().state = "relance_client"

    def vers_perdu_vsb_action(self):
        for obj in self:
            obj.sudo().state = "perdu"

    def vers_gagne_vsb_action(self):
        for obj in self:
            obj.sudo().state = "gagne"

    def vers_annule_vsb_action(self):
        for obj in self:
            obj.sudo().state = "annule"

    demao_type                  = fields.Selection([
        ("modification", "Modification"),
        ("variante",     "Variante"),
    ], string="Type", required=True)
    demao_num                   = fields.Char(string="N° ordre", required=True)
    demao_dao                   = fields.Char(string="Dossier AO")
    demao_date                  = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    demao_idclient              = fields.Many2one("res.partner", string="Client", required=True, domain=[("is_company","=",True), ("customer","=",True)])
    demao_idcommercial          = fields.Many2one("res.users", string="Commercial", default=lambda self: self.env.user, required=True)
    demao_idmoule               = fields.Many2one("is.mold", string="Moule")
    demao_desig                 = fields.Char(string="Désignation pièce", required=True)
    demao_nature                = fields.Char(string="Nature", required=True)
    demao_ref                   = fields.Char(string="Référence")
    demao_daterep               = fields.Date(string="Date réponse")
    demao_datelance             = fields.Date(string="Date lancement")
    demao_pxvente               = fields.Char(string="Prix de vente")
    demao_numcmd                = fields.Char(string="N° commande")
    demao_obs                   = fields.Char(string="Observation")
    demao_motif                 = fields.Selection([
        ("1", "abandon client"),
        ("2", "délai trop long"),
        ("3", "moule et pièce trop chers"),
        ("4", "moule trop cher"),
        ("5", "pièce trop chère"),
        ("6", "autre"),
        ("7", "abandon Plastigray"),
    ], string="Motif ")
    demao_idbe                  = fields.Many2one("res.users", string="BE")
    demao_annexcom              = fields.Many2many("ir.attachment", "is_dmv_annexcom_rel", "annexcom_id", "att_id", string="Fichiers commercial")
    demao_annex                 = fields.Many2many("ir.attachment", "is_dmv_annex_rel", "annex_id", "att_id", string="Fichiers BE")
    demao_cde_be                = fields.Many2many("ir.attachment", "is_dmv_cde_be_rel", "cde_be_id", "att_id", string="Commandes BE")
    state                       = fields.Selection([
        ("cree",               "Créé"),
        ("analyse",            "Analysé"),
        ("transmis_be",        "Transmis BE"),
        ("analyse_be",         "Analyse BE"),
        ("vali_de_be",         "Vali de BE"),
        ("vali_de_commercial", "Vali de Commercial"),
        ("diffuse_client",     "Diffuse Client"),
        ("relance_client",     "Relance Client"),
        ("perdu",              "Perdu"),
        ("gagne",              "Gagne"),
        ("annule",             "Annule"),
    ], string="State", default="cree", tracking=True)
    vers_analyse_vsb            = fields.Boolean(string="Vers Cree", compute='_compute_vsb', readonly=True, store=False)
    vers_transmis_be_vsb        = fields.Boolean(string="Vers Transmis BE", compute='_compute_vsb', readonly=True, store=False)
    vers_analyse_be_vsb         = fields.Boolean(string="Vers Analyse BE", compute='_compute_vsb', readonly=True, store=False)
    vers_vali_de_be_vsb         = fields.Boolean(string="Vers Vali de BE", compute='_compute_vsb', readonly=True, store=False)
    vers_vali_de_commercial_vsb = fields.Boolean(string="Vers Vali de Commercial", compute='_compute_vsb', readonly=True, store=False)
    vers_diffuse_client_vsb     = fields.Boolean(string="Diffuse Client", compute='_compute_vsb', readonly=True, store=False)
    vers_relance_client_vsb     = fields.Boolean(string="Relance Client", compute='_compute_vsb', readonly=True, store=False)
    vers_perdu_vsb              = fields.Boolean(string="Perdu", compute='_compute_vsb', readonly=True, store=False)
    vers_gagne_vsb              = fields.Boolean(string="Gagne", compute='_compute_vsb', readonly=True, store=False)
    vers_annule_vsb             = fields.Boolean(string="Annule", compute='_compute_vsb', readonly=True, store=False)
    dynacase_id                 = fields.Integer(string="Id Dynacase")
