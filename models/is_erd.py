# -*- coding: utf-8 -*-
from odoo import models, fields, api, _      # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


#TODO : 
#- Lien avec is_inv_achat_moule
#- Ajouter les 3 champs des pieces jointes


class is_erd(models.Model):
    _name = "is.erd"
    _inherit=['mail.thread']
    _description = "ERD"
    _rec_name    = "numero"

    numero          = fields.Char(string="N° ERD", tracking=True, required=True, index=True)
    date            = fields.Date(string="Date", tracking=True)
    clientid        = fields.Many2one("res.partner"              , string="Client"            , tracking=True)
    designation     = fields.Char(string="Désignation", tracking=True)
    commercialid    = fields.Many2one("res.users"                , string="Commercial"    , tracking=True)
    date_reponse_be = fields.Date(string="Date réponse BE", tracking=True)
    date_reponse    = fields.Date(string="Date réponse", tracking=True)
    date_lancement  = fields.Date(string="Date lancement", tracking=True)
    prix_vente      = fields.Float(string="Prix de vente", tracking=True)
    num_commande    = fields.Char(string="N° commande", tracking=True)
    observation     = fields.Text(string="Observation", tracking=True)
    beid            = fields.Many2one("res.users"                , string="BE"    , tracking=True)
    dynacase_id     = fields.Integer(string="Id Dynacase", index=True, copy=False)
    active          = fields.Boolean('Actif', default=True                               , tracking=True)
    state = fields.Selection([
        ("Cree"          , "Créé"),
        ("Transmis_BE"   , "Transmis BE"),
        ("Valide_BE"     , "Validé BE"),
        ("Diffuse_Client", "Diffusé Client"),
        ("Gagne"         , "Gagné"),
    ], default="Cree", string="État", tracking=True, copy=False)

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
            

# gesterd_frm_pj_commerciaux		Pièces jointes commerciaux	N	N	frame
# gesterd_ar_pj_commerciaux	gesterd_frm_pj_commerciaux		N	N	array
# gesterd_file_pj_commerciaux	gesterd_ar_pj_commerciaux		N	N	file
					
					
# gesterd_frm_pj_be		Pièces jointes BE	N	N	frame
# gesterd_ar_pj_be	gesterd_frm_pj_be	Fichiers BE	N	N	array
# gesterd_file_pj_be	gesterd_ar_pj_be	Fichiers BE	N	N	file
					
# gesterd_ar_cde_be	gesterd_frm_pj_be	Commandes BE	N	N	array
# gesterd_file_cde_be	gesterd_ar_cde_be	Commandes BE	N	N	file
