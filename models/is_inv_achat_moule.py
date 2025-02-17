# -*- coding: utf-8 -*-
from odoo import models, fields, api, _      # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


#TODO : 
#- date_commande_ou_saisie => compute


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

    code_imputation    = fields.Selection(_CODE_IMPUTATION          , string="Code imputation"   , tracking=True, required=True, index=True)
    revue_lancementid  = fields.Many2one("is.revue.lancement"       , string="Revue de lancement", tracking=True)
    num_erdid          = fields.Many2one("is.erd"                   , string="ERD"               , tracking=True)
    num_dossierid      = fields.Many2one("is.dossier.modif.variante", string="N° de dossier"     , tracking=True)
    num_mouleid        = fields.Many2one("is.mold"                  , string="Moule"             , tracking=True)
    nature             = fields.Char(string="Nature DM / Désignation ERD"                        , tracking=True, compute='_compute',store=True, readonly=True)
    clientid           = fields.Many2one("res.partner"              , string="Client"            , tracking=True, compute='_compute',store=True, readonly=True)
    projetid           = fields.Many2one("is.mold.project"          , string="Projet"            , tracking=True, compute='_compute',store=True, readonly=True)
    chef_projetid      = fields.Many2one("res.users"                , string="Chef de Projet"    , tracking=True, compute='_compute',store=True, readonly=True)
    date_saisie        = fields.Date(string="Date de saisie"                                     , tracking=True)
    annee_saisie       = fields.Char(string="Année de saisie"                                    , tracking=True, compute='_compute_annee',store=True, readonly=True)
    annee_enregistre   = fields.Char(string="Année d'enregistrement"                             , tracking=True)
    montant_vendu      = fields.Float(string="Montant vendu"                                     , tracking=True)
    num_cde_id         = fields.Many2one("is.inv.achat.moule.po", string="N°Cde"                 , tracking=True)
    num_cde            = fields.Char(string="N°Cde fournisseur"                                  , tracking=True, compute='_compute_cde',store=True, readonly=True)
    fournisseurid      = fields.Many2one("res.partner", string="Fournisseur"                     , tracking=True, compute='_compute_cde',store=True, readonly=True)
    code_fournisseur   = fields.Char(string="Code fournisseur"                                   , tracking=True, compute='_compute_cde',store=True, readonly=True)
    date_cde           = fields.Date(string="Date commande"                                      , tracking=True, compute='_compute_cde',store=True, readonly=True)
    objet_commande     = fields.Text(string="Objet de la commande"                               , tracking=True, compute='_compute_cde',store=True, readonly=True)
    prix_commande      = fields.Float(string="Montant de la commande fournisseur"                , tracking=True, compute='_compute_cde',store=True, readonly=True)
    montant_facture    = fields.Float(string="Montant des factures fournisseur"                  , tracking=True, readonly=True)
    date_derniere_facture   = fields.Date(string="Date dernière facture"                         , tracking=True, readonly=True)
    date_commande_ou_saisie = fields.Date(string="Date de commande ou de saisie"                 , tracking=True, compute='_compute_date',store=True, readonly=True)
    dynacase_id             = fields.Integer(string="Id Dynacase", index=True, copy=False)
    active                  = fields.Boolean('Actif', default=True                               , tracking=True)


    @api.depends('date_saisie', 'date_cde')
    def _compute_date(self):
        for obj in self:
            obj.date_commande_ou_saisie = obj.date_saisie or obj.date_cde


    @api.depends('revue_lancementid', 'num_erdid', 'num_dossierid', 'num_mouleid')
    def _compute(self):
        for obj in self:
            obj.nature   = obj.revue_lancementid.rl_designation_rc or obj.num_erdid.designation or obj.num_dossierid.demao_desig       or obj.num_mouleid.designation
            obj.clientid = obj.revue_lancementid.rl_client_rcid.id or obj.num_erdid.clientid.id or obj.num_dossierid.demao_idclient.id or obj.num_mouleid.client_id.id
            obj.projetid = obj.revue_lancementid.rl_projet_rcid.id or obj.num_mouleid.project.id
            obj.chef_projetid = obj.revue_lancementid.rl_projet_rcid.chef_projet_id.id or obj.num_mouleid.project.chef_projet_id.id
          

    @api.depends('date_saisie')
    def _compute_annee(self):
        for obj in self:
            annee_saisie=''
            if obj.date_saisie:
                annee_saisie = obj.date_saisie.strftime("%Y")
            obj.annee_saisie = annee_saisie


    @api.depends('num_cde_id')
    def _compute_cde(self):
        for obj in self:
            obj.num_cde          = obj.num_cde_id.num_cde
            obj.fournisseurid    = obj.num_cde_id.fournisseur_id.id
            obj.code_fournisseur = obj.num_cde_id.code_fournisseur
            obj.date_cde         = obj.num_cde_id.date_cde
            obj.objet_commande   = obj.num_cde_id.description
            obj.prix_commande    = obj.num_cde_id.total


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
            

class is_inv_achat_moule_po(models.Model):
    _name        = "is.inv.achat.moule.po"
    _description = "Investissement achat moule - Commande fournisseur"
    _rec_name    = "num_cde"
    _order       = "soc,num_cde desc"

    soc              = fields.Integer(string="Soc",index=True)
    num_cde          = fields.Char(string="N°Cde" ,index=True)
    date_cde         = fields.Date(string="Date Cde")
    code_fournisseur = fields.Char(string="Code fournisseur")
    fournisseur_id   = fields.Many2one("res.partner", string="Fournisseur")
    devise           = fields.Char(string="Devise")
    taux_devise      = fields.Float(string="Taux Devise")
    description      = fields.Text(string="Description")
    total            = fields.Float(string="Total")


    # //** Recherche dans Odoo ***************************************************
    # $Socs=array(1,4);
    # foreach($Socs as $Soc) {
    #     $dbname="dy-odoo16-".$Soc;
    #     $cnx = pg_connect("host=127.0.0.1 port=5432 dbname=$dbname user=odoo2dynacase password=RY04JU34");
    #     $SQL="
    #         select 
    #             po.name           numcde,
    #             rp.is_code        code_fournisseur,
    #             rc.name           devise,
    #             max(pol.name)     description,
    #             sum(pol.product_qty*pol.price_unit) total
    #         from purchase_order po inner join purchase_order_line pol on pol.order_id=po.id
    #                                inner join res_currency         rc on po.currency_id=rc.id
    #                                inner join res_partner          rp on po.partner_id=rp.id 
    #         where po.id>0
    #     ";
    #     if ($Cde<>'')   $SQL="$SQL and po.name like '%$Cde%' ";
    #     $SQL="$SQL group by po.name,rp.is_code,rc.name order by po.name limit 20 ";
    #     $result = pg_query($cnx, $SQL);
    #     while($row = pg_fetch_object($result)) {
    #         $taux=1;
    #         if ($row->devise!='EUR') {
    #             $SQL="
    #                 select rcr.id,rcr.rate,rc.name 
    #                 from res_currency_rate rcr inner join res_currency rc on rcr.currency_id=rc.id 
    #                 where rc.name='USD' 
    #                 order by rcr.id desc limit 1
    #             ";
    #             $result2 = pg_query($cnx, $SQL);
    #             while($row2 = pg_fetch_object($result2)) {
    #                 $taux=$row2->rate;
    #             }
    #         }
    #         $tab[]=array(
    #             $row->numcde." : ".$row->devise,
    #             round($row->total/$taux,2),
    #             $row->code_fournisseur,
    #             $row->numcde,
    #             $row->description,
    #         );
    #     }
    # }
    # //**************************************************************************