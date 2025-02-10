# -*- coding: utf-8 -*-
from odoo import models, fields, api, _      # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


#TODO : 
#- Pour les clients, projets et chef de projet, mettre un champ calculé
#- Champ nature est un compute
#- Migrer également les ERD car lien avec
#- name à revoir => Mettre le montant pour afficher dans RL
#- Lien avec RL
#- Analyser contenu fichiers PHP de cette famille
#- Ajouter vue tableau croisée et graph
#- Lien avec ERD


_CODE_IMPUTATION=[
    ('be01' , 'BE01a : Nouveau moule/Moule transféré'),
    ('be01b', 'BE01b : Grainage'),
    ('be01c', 'BE01c : Barre chaude'),
    ('be02' , 'BE02 : Étude/CAO/Rhéologie'),
    ('be03' , 'BE03 : Prototype'),
    ('be04' , 'BE04 : Main de préhension'),
    ('be05' , 'BE05 : Gabarit de contrôle'),
    ('be06' , 'BE06 : Mise au point'),
    ('be07' , 'BE07 : Test'),
    ('be09' , 'BE09 : Essais + divers'),
    ('be10' , 'BE10 : Métrologie'),
    ('be11' , 'BE11 : Transports'),
    ('be12' , 'BE12 : Étude/Développement Packaging'),
    ('be13' , "BE13 : Poste d'assemblage"),
    ('be14' , 'BE14 : Développement outillages divers ( découpe...)'),
    ('be15' , 'BE15 : Achat matière'),
    ('be16' , 'BE16 : Achat composants'),
    ('be17' , 'BE17 : Essai injection'),
    ('DM'   , 'Dossier modification'),
    ('ERD'  , 'ERD'),
]


class is_inv_achat_moule(models.Model):
    _name        = "is.inv.achat.moule"
    _inherit=['mail.thread']
    _description = "Investissement achat moule"
    #_rec_name = "montant_vendu"

    code_imputation    = fields.Selection(_CODE_IMPUTATION          , string="Code imputation"   , tracking=True, required=True, index=True)
    revue_lancementid  = fields.Many2one("is.revue.lancement"       , string="Revue de lancement", tracking=True)
    num_dossierid      = fields.Many2one("is.dossier.modif.variante", string="N° de dossier"     , tracking=True)
    num_erdid          = fields.Char(string="ERD"                                                , tracking=True)
    nature             = fields.Char(string="Nature DM / Désignation ERD"                        , tracking=True)
    num_mouleid        = fields.Many2one("is.mold"                  , string="Moule"             , tracking=True)
    clientid           = fields.Many2one("res.partner"              , string="Client"            , tracking=True)
    projetid           = fields.Many2one("is.mold.project"          , string="Projet"            , tracking=True)
    chef_projetid      = fields.Many2one("res.users"                , string="Chef de Projet"    , tracking=True)
    date_saisie        = fields.Date(string="Date de saisie"                                     , tracking=True)
    annee_saisie       = fields.Char(string="Année de saisie"                                    , tracking=True)
    annee_enregistre   = fields.Char(string="Année d'enregistrement"                             , tracking=True)
    montant_vendu      = fields.Float(string="Montant vendu"                                     , tracking=True)
    num_cde            = fields.Char(string="N°commande fournisseur"                             , tracking=True)
    date_cde           = fields.Date(string="Date commande"                                      , tracking=True)
    prix_commande      = fields.Float(string="Montant de la commande fournisseur"                , tracking=True)
    montant_facture    = fields.Float(string="Montant des factures fournisseur"                  , tracking=True)
    date_derniere_facture   = fields.Date(string="Date dernière facture"                         , tracking=True)
    code_fournisseur        = fields.Char(string="Code fournisseur"                              , tracking=True)
    date_commande_ou_saisie = fields.Date(string="Date de commande ou de saisie"                 , tracking=True)
    fournisseurid           = fields.Many2one("res.partner", string="Fournisseur"                , tracking=True)
    objet_commande          = fields.Text(string="Objet de la commande"                          , tracking=True)
    dynacase_id             = fields.Integer(string="Id Dynacase", index=True, copy=False)
    active                  = fields.Boolean('Actif', default=True                               , tracking=True)



    def name_get(self):
        result = []
        for obj in self:
            name = '{0:,.2f}'.format(obj.montant_vendu).replace(',',' ').replace('.',',')
            result.append((obj.id, name))
        return result




    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
            