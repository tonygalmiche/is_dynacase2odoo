# -*- coding: utf-8 -*-
from odoo import models, fields, api, _      # type: ignore
from odoo.exceptions import ValidationError  # type: ignore

class is_erd(models.Model):
    _name = "is.erd"
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "ERD"
    _rec_name    = "numero"

    numero          = fields.Char(string="N° ERD", tracking=True, required=True, index=True)
    date            = fields.Date(string="Date", tracking=True)
    clientid        = fields.Many2one("res.partner", string="Client"            , tracking=True)
    designation     = fields.Char(string="Désignation", tracking=True)
    commercialid    = fields.Many2one("res.users", string="Commercial"    , tracking=True)
    date_reponse_be = fields.Date(string="Date réponse BE", tracking=True)
    date_reponse    = fields.Date(string="Date réponse"   , tracking=True)
    date_lancement  = fields.Date(string="Date lancement" , tracking=True)
    prix_vente      = fields.Float(string="Prix de vente" , tracking=True)
    num_commande    = fields.Char(string="N° commande"    , tracking=True)
    observation     = fields.Text(string="Observation"    , tracking=True)
    beid            = fields.Many2one("res.users", string="BE", tracking=True)
    dynacase_id     = fields.Integer(string="Id Dynacase", index=True, copy=False)
    active          = fields.Boolean('Actif', default=True, tracking=True)
    state = fields.Selection([
        ("Cree"          , "Créé"),
        ("Transmis_BE"   , "Transmis BE"),
        ("Valide_BE"     , "Validé BE"),
        ("Diffuse_Client", "Diffusé Client"),
        ("Gagne"         , "Gagné"),
    ], default="Cree", string="État", tracking=True, copy=False)
    file_pj_commerciaux_ids = fields.Many2many("ir.attachment", "is_erd_file_pj_commerciaux_rel", "file_pj_commerciaux", "att_id", string="Pièces jointe commerciaux")
    file_pj_be_ids          = fields.Many2many("ir.attachment", "is_erd_file_pj_be_rel"         , "file_pj_be"         , "att_id", string="Fichiers BE")
    file_cde_be_ids         = fields.Many2many("ir.attachment", "is_erd_file_cde_be__rel"       , "file_cde_be"        , "att_id", string="Commandes BE")
    vers_transmis_be_vsb    = fields.Boolean(string="vers_Transmis_BE_action"   , compute='_compute_vsb', readonly=True, store=False)
    vers_valide_be_vsb      = fields.Boolean(string="vers_Valide_BE_action"     , compute='_compute_vsb', readonly=True, store=False)
    vers_diffuse_client_vsb = fields.Boolean(string="vers_Diffuse_Client_action", compute='_compute_vsb', readonly=True, store=False)
    vers_gagne_vsb          = fields.Boolean(string="vers_Gagne_action"         , compute='_compute_vsb', readonly=True, store=False)
    readonly                = fields.Boolean(string="readonly"                  , compute='_compute_vsb', readonly=True, store=False)


    @api.depends("state")
    def _compute_vsb(self):
        commercial  = self.env['res.users'].has_group('is_plastigray16.is_commerciaux_group')
        chef_projet = self.env['res.users'].has_group('is_plastigray16.is_chef_projet_group')
        for obj in self:
            vsb = False
            if (commercial or chef_projet) and obj.state=='Cree':
                vsb=True
            obj.vers_transmis_be_vsb = vsb

            vsb = False
            if (commercial or chef_projet) and obj.state in ('Transmis_BE','Diffuse_Client'):
                vsb=True
            obj.vers_valide_be_vsb = vsb

            vsb = False
            if commercial and obj.state in ('Valide_BE','Gagne'):
                vsb=True
            obj.vers_diffuse_client_vsb = vsb

            vsb = False
            if commercial and obj.state=='Diffuse_Client':
                vsb=True
            obj.vers_gagne_vsb = vsb

            readonly=False
            if obj.state in ('Diffuse_Client','Gagne'):
                readonly=True
            obj.readonly=readonly


    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
            
    def vers_Transmis_BE_action(self):
        for obj in self:
            obj.state='Transmis_BE'

    def vers_Valide_BE_action(self):
        for obj in self:
            obj.state='Valide_BE'

    def vers_Diffuse_Client_action(self):
        for obj in self:
            obj.state='Diffuse_Client'

    def vers_Gagne_action(self):
        for obj in self:
            obj.state='Gagne'
