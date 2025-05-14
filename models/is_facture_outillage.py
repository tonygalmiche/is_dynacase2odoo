# -*- coding: utf-8 -*-
from odoo import models, fields, api, _      # type: ignore
from odoo.exceptions import ValidationError  # type: ignore
from datetime import datetime, timedelta, date
from subprocess import PIPE, Popen
import logging
_logger = logging.getLogger(__name__)


_TYPE_DOSSIER=([
    ('Moule'    , 'Moule'),
    ('Modif'    ,'Modif'),
    ('Variante' ,'Variante'),
    ('ERD'      ,'ERD'),
    ('Dossier F','Dossier F'),
    ('RL'       ,'Revue de lancement'),
])

_OUI_NON=([
    ('oui', 'Oui'),
    ('non', 'Non'),
])

_TYPE_FACTURE=([
    ('Proforma', 'Proforma'),
    ('Facture' , 'Facture'),
    ('Avoir'   , 'Avoir'),
])


class is_facture_outillage(models.Model):
    _name = "is.facture.outillage"
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Facture outillage"
    _rec_name    = "designation"
    _order = "create_date desc"

    type_dossier              = fields.Selection(_TYPE_DOSSIER             , string="Type"                    , tracking=True, required=True)
    revue_lancement_id        = fields.Many2one("is.revue.lancement"       , string="Revue de lancement"      , tracking=True)
    dossier_modif_variante_id = fields.Many2one("is.dossier.modif.variante", string="Dossier Modif / Variante", tracking=True)
    moule_id                  = fields.Many2one("is.mold"                  , string="Moule"                   , tracking=True)
    dossierf_id               = fields.Many2one("is.dossierf"              , string="Dossier F"               , tracking=True)
    erd_id                    = fields.Many2one("is.erd"                   , string="ERD"                     , tracking=True)
    client_id                 = fields.Many2one("res.partner"              , string="Client"                  , tracking=True)
    commercial_id             = fields.Many2one("res.users"                , string="Commercial"              , tracking=True, compute="_compute_designation", store=True, readonly=True)
    chef_projet_id            = fields.Many2one("res.users"                , string="Chef de projet"          , tracking=True, compute="_compute_designation", store=True, readonly=True)
    designation               = fields.Char("Désignation"                                                     , tracking=True, compute="_compute_designation", store=True, readonly=True)
    montant_global            = fields.Float(string="Montant global"                                          , tracking=True)
    numero_commande_client    = fields.Char("N° Commande client"                                              , tracking=True)
    piece_jointe_ids          = fields.Many2many("ir.attachment", "is_facture_outillage_piece_jointe_rel", "piece_jointe", "att_id", string="Commande client")
    montant_commande_client   = fields.Float(string="Montant commande client"                                 , tracking=True)
    date_reception            = fields.Date(string="Date de réception"                                        , tracking=True)
    montant_dossier           = fields.Float(string="Montant du dossier"                                      , tracking=True)
    total_facture             = fields.Float(string="Total facturé"                                           , tracking=True, compute="_compute_montant"  , store=True, readonly=True)
    ecart_commande_facture    = fields.Float(string="Ecart Montant dossier / Montant HT factures"             , tracking=True, compute="_compute_montant"  , store=True, readonly=True)
    ecart_ttc                 = fields.Float(string="Ecart Montant TTC payé / Ecart TTC"                      , tracking=True, compute="_compute_montant"  , store=True, readonly=True)
    solde                     = fields.Selection(_OUI_NON, string="Soldé", default='non'                      , tracking=True)
    active                    = fields.Boolean('Actif', default=True, tracking=True)
    dynacase_id               = fields.Integer(string="Id Dynacase", index=True, copy=False)
    ligne_ids                 = fields.One2many('is.facture.outillage.ligne', 'facture_id', string="Lignes")


    @api.depends('ligne_ids','ligne_ids.montant_ht','montant_dossier')
    def _compute_montant(self):
        for obj in self:
            total_facture=0
            for ligne in obj.ligne_ids:
                total_facture+=ligne.montant_ht
            ecart = obj.montant_dossier - total_facture
            obj.total_facture  = total_facture
            obj.ecart_commande_facture = ecart
            obj.ecart_ttc = ecart

			
    @api.depends('type_dossier','revue_lancement_id','dossier_modif_variante_id','moule_id','dossierf_id','erd_id')
    def _compute_designation(self):
        for obj in self:
            designation=commercial_id=chef_de_projet_id=False
            if obj.type_dossier=='Moule' and obj.moule_id:
                designation = "[%s] %s"%(obj.moule_id.name,obj.moule_id.designation)
                commercial_id     = obj.moule_id.client_id.user_id.id
                chef_de_projet_id = obj.moule_id.chef_projet_id.id
            if obj.type_dossier in ('Modif','Variante') and obj.dossier_modif_variante_id:
                designation = "[%s] %s"%(obj.dossier_modif_variante_id.demao_num,obj.dossier_modif_variante_id.demao_desig)
                commercial_id     = obj.dossier_modif_variante_id.demao_idcommercial.id
                chef_de_projet_id = obj.dossier_modif_variante_id.demao_idbe.id
            if obj.type_dossier=='ERD' and obj.erd_id:
                designation = "[%s] %s"%(obj.erd_id.numero,obj.erd_id.designation)
                commercial_id     = obj.erd_id.commercialid.id
                chef_de_projet_id = obj.erd_id.beid.id
            if obj.type_dossier=='Dossier F' and obj.dossierf_id:
                designation = "[%s] %s"%(obj.dossierf_id.name,obj.dossierf_id.designation)
                commercial_id     = obj.dossierf_id.client_id.user_id.id
                chef_de_projet_id = obj.dossierf_id.chef_projet_id.id
            if obj.type_dossier=='RL' and obj.revue_lancement_id:
                designation = "[%s] %s"%(obj.revue_lancement_id.name,obj.revue_lancement_id.rl_designation_rc)
                commercial_id     = obj.revue_lancement_id.rl_client_rcid.user_id.id
                chef_de_projet_id = obj.revue_lancement_id.rl_chef_projetid.id
            obj.designation    = designation
            obj.commercial_id  = commercial_id
            obj.chef_projet_id = chef_de_projet_id

			
    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


    def actualiser_action(self):
        for obj in self:
            obj.ligne_ids.actualiser_ligne_action()


class is_facture_outillage_ligne(models.Model):
    _name = "is.facture.outillage.ligne"
    _description = "Lignes facture outillage"
    _order = "id"

    facture_id        = fields.Many2one('is.facture.outillage', 'Facture', required=True, ondelete='cascade')
    type_facture      = fields.Selection(_TYPE_FACTURE, string="Type de facture") 
    num_facture       = fields.Char("N° de facture")
    montant_ht        = fields.Float("Montant HT")
    montant_ttc       = fields.Float("Montant TTC")
    montant_paye_ht   = fields.Float("Montant Payé TTC", readonly=True)
    num_bl            = fields.Char("N° BL")
    date_facture_prev = fields.Date("Date de facture prévisionnelle")
    date_facture      = fields.Date("Date facture")
    date_echeance     = fields.Date("Date échéance")
    date_reglement    = fields.Date("Date règlement")
    commentaire       = fields.Text("Commentaire")
   

    @api.onchange('num_facture')
    def actualiser_ligne_action(self):
        for obj in self:
            res = obj.get_values()
            if len(res)==6:
                obj.montant_ht      = res[0]
                obj.montant_ttc     = res[1]
                obj.montant_paye_ht = res[2]
                obj.date_facture    = res[3]
                obj.date_echeance   = res[4]
                obj.date_reglement  = res[5]


    def get_values(self):
        for obj in self:
            res=[]
            if obj.num_facture:
                name = "actualiser-facture-outillage"
                cdes = self.env['is.commande.externe'].search([('name','=',name)])
                if len(cdes)==0:
                    raise ValidationError("Commande externe '%s' non trouvée !"%name)
                for cde in cdes:
                    commande = cde.commande.replace("#type_facture", obj.type_facture)
                    commande = cde.commande.replace("#num_facture" , obj.num_facture)
                    p = Popen(commande, shell=True, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = p.communicate()
                    _logger.info("%s => %s"%(commande,stdout))
                    if stderr:
                        raise ValidationError("Erreur dans commande externe '%s' => %s"%(commande,stderr))
                    res = stdout.decode("utf-8").strip().split('|')
            return res
            
