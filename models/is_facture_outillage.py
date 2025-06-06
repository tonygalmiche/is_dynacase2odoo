# -*- coding: utf-8 -*-
from odoo import models, fields, api, _      # type: ignore
from odoo.exceptions import ValidationError  # type: ignore
from datetime import datetime, timedelta, date
from subprocess import PIPE, Popen
import sys
import psycopg2        # type: ignore
import psycopg2.extras # type: ignore
import pyodbc          # type: ignore
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
    ('Oui', 'Oui'),
    ('Non', 'Non'),
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
    client_id                 = fields.Many2one("res.partner", string="Client", tracking=True, domain=[("is_company","=",True), ("customer","=",True)])
    client_autre              = fields.Char("Client (autre)"                                                  , tracking=True)
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
    solde                     = fields.Selection(_OUI_NON, string="Soldé", default='Non'                      , tracking=True)
    active                    = fields.Boolean('Actif', default=True, tracking=True)
    dynacase_id               = fields.Integer(string="Id Dynacase", index=True, copy=False)
    ligne_ids                 = fields.One2many('is.facture.outillage.ligne', 'facture_id', string="Lignes")
    num_facture               = fields.Text(string="N° facture"    , compute='_compute_ligne',store=True, readonly=True, tracking=True)
    montant_ht                = fields.Text(string="Montant HT"    , compute='_compute_ligne',store=True, readonly=True, tracking=True)
    date_facture_prev         = fields.Text(string="Date prév."    , compute='_compute_ligne',store=True, readonly=True, tracking=True)
    date_facture              = fields.Text(string="Date facture"  , compute='_compute_ligne',store=True, readonly=True, tracking=True)
    date_reglement            = fields.Text(string="Date règlement", compute='_compute_ligne',store=True, readonly=True, tracking=True)


    @api.depends('ligne_ids','ligne_ids.type_facture','ligne_ids.num_facture','ligne_ids.date_facture_prev','ligne_ids.date_facture','ligne_ids.date_reglement')
    def _compute_ligne(self):
        for obj in self:
            num_facture=[]
            montant_ht=[]
            date_facture_prev=[]
            date_facture=[]
            date_reglement=[]            
            for line in obj.ligne_ids:
                num_facture.append(line.num_facture or '')
                montant_ht.append('{0:,.2f}'.format(line.montant_ht).replace(',',' ').replace('.',','))
                date_facture_prev.append((line.date_facture_prev and line.date_facture_prev.strftime('%d/%m/%Y')) or '')
                date_facture.append((line.date_facture and line.date_facture.strftime('%d/%m/%Y')) or '')
                date_reglement.append((line.date_reglement and line.date_reglement.strftime('%d/%m/%Y')) or '')
            obj.num_facture = '\n'.join(num_facture)
            obj.montant_ht = '\n'.join(montant_ht)
            obj.date_facture_prev = '\n'.join(date_facture_prev)
            obj.date_facture = '\n'.join(date_facture)
            obj.date_reglement = '\n'.join(date_reglement)


    def compute_xml_rpc(self):
        "for xml-rpc"
        self._compute_designation()
        self._compute_ligne()
        return True


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
   

    def voir_facture_action(self):
        for obj in self:
            cr_odoo1,test = self.get_cr_odoo1()
            url=False
            if obj.type_facture in ['Facture','Avoir']:
                SQL="SELECT id from account_move where name=%s and move_type in ('out_invoice','out_refund')"
                cr_odoo1.execute(SQL,[obj.num_facture])
                rows = cr_odoo1.fetchall()
                for row in rows:    
                    url="https://odoo1/web#id=%s&model=account.move&view_type=form"%row['id']
            if obj.type_facture in ['Proforma']:
                SQL="SELECT id from is_facture_proforma_outillage where name=%s"
                cr_odoo1.execute(SQL,[obj.num_facture])
                rows = cr_odoo1.fetchall()
                for row in rows:    
                    url="https://odoo1/web#id=%s&model=is.facture.proforma.outillage&view_type=form"%row['id']
            if url:
                return {
                    'type' : 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }


    def get_cr_odoo1(self):
        cr_odoo1 = False
        company = self.env.user.company_id
        databases=self.env['is.database'].search([('name','=', 'Gray')])
        test=True
        for database in databases:
            host     = company.is_postgres_host or ''
            dbname   = database.database        or ''
            user     = company.is_postgres_user or ''
            password = company.is_postgres_pwd  or ''
            try:
                cnx_odoo1 = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'"%(host,dbname,user,password))
                cr_odoo1  = cnx_odoo1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            except Exception as err:
                msg="La connexion à Odoo1 sur la base '%s' et le serveur '%s' a échouée !"%(dbname,host)
                msg="%s\n[%s] %s"%(msg,type(err),err)
                _logger.error(msg)
                test=False
        return cr_odoo1,test



    @api.onchange('num_facture')
    def actualiser_ligne_action(self):
        cr_cegid = False
        company = self.env.user.company_id

        #** Connexion à Odoo 1 ************************************************
        cr_odoo1,test = self.get_cr_odoo1()
        #**********************************************************************

        ##** Connexion à CEGID ************************************************
        SERVER   = company.is_cegid_ip    or ''
        UID      = company.is_cegid_login or ''
        PWD      = company.is_cegid_mdp   or ''
        DATABASE = company.is_cegid_base  or ''
        try:
            cnx = 'DRIVER={FreeTDS};SERVER=%s;PORT=1433;UID=%s;PWD=%s;DATABASE=%s;UseNTLMv2=yes;TDS_Version=8.0;Trusted_Domain=domain.local;'%(
                SERVER,
                UID,
                PWD,
                DATABASE
            )
            cnx_cegid = pyodbc.connect(cnx)
            cr_cegid = cnx_cegid.cursor()
        except Exception as err:
            msg="La connexion à CEGID sur la base '%s' et le serveur '%s' a échouée !"%(DATABASE,SERVER)
            msg="%s\n[%s] %s"%(msg,type(err),err)
            _logger.error(msg)
            test=False
            #raise ValidationError(msg)
        #**********************************************************************

        if test:
            for obj in self:
                type_facture = obj.type_facture
                num_facture  = obj.num_facture
                montant_ht = montant_ttc = montant_paye_ht = 0
                date_facture = date_reglement = date_echeance = ''
                if type_facture in ('Facture','Avoir'):
                
                    if type_facture=="Facture":
                        move_type='out_invoice'
                    if type_facture=="Avoir":
                        move_type = 'out_refund'
                    SQL="""
                        select id,name,amount_untaxed_signed,amount_total_signed 
                        from account_move 
                        where state='posted' and move_type=%s and name=%s
                        order by name desc limit 1
                    """
                    cr_odoo1.execute(SQL,[move_type,num_facture])
                    rows = cr_odoo1.fetchall()
                    for row in rows:                
                        montant_ht  = row['amount_untaxed_signed']
                        montant_ttc = row['amount_total_signed']
                        
                        #** Recherche Date Facture dans CEGID **************************************
                        SQL="""
                            select E_DATECOMPTABLE
                            from ECRITURE
                            where 
                                E_GENERAL='411000' and
                                E_JOURNAL='VTE' and 
                                E_REFINTERNE='%s'
                        """%num_facture
                        rows_cegid = cr_cegid.execute(SQL)
                        for row_cegid in rows_cegid:
                            date_facture = row_cegid[0]
                        #***************************************************************************

                        #** Recherche Date Réglement dans CEGID ************************************
                        SQL="""
                            select E_DATECOMPTABLE
                            from ECRITURE
                            where 
                                E_GENERAL='411000' and
                                E_JOURNAL!='VTE' and 
                                E_REFINTERNE='%s' and
                                E_DATECOMPTABLE>'2024-01-01'
                        """%num_facture
                        rows_cegid = cr_cegid.execute(SQL)
                        for row_cegid in rows_cegid:
                            date_reglement = row_cegid[0]
                        #***************************************************************************

                        #** Recherche Date Echéance dans CEGID *************************************
                        SQL="""
                            select E_DATPER
                            from ECRITURE
                            where 
                                E_GENERAL='411000' and
                                E_JOURNAL!='VTE' and 
                                E_REFINTERNE='%s'
                        """%num_facture
                        rows_cegid = cr_cegid.execute(SQL)
                        for row_cegid in rows_cegid:
                            date_echeance = row_cegid[0]
                        #***************************************************************************

                        #** Montant payé CEGID *****************************************************
                        SQL="""
                            select E_CREDIT,E_GENERAL
                            from ECRITURE
                            where 
                                E_JOURNAL<>'VTE' and 
                                E_REFINTERNE='%s' and 
                                E_AUXILIAIRE>='C500000' and 
                                E_AUXILIAIRE<='C509999'
                        """%num_facture
                        rows_cegid = cr_cegid.execute(SQL)
                        for row_cegid in rows_cegid:
                            montant_paye_ht += row_cegid[0] / 10000
                        #***************************************************************************

                if type_facture=='Proforma':
                    SQL="""
                        select e.id,e.name,e.num_cde, e.date_facture, sum(l.total) total
                        from is_facture_proforma_outillage e join is_facture_proforma_outillage_line l on e.id=l.proforma_id
                        where e.name=%s
                        group by e.name, e.id,e.num_cde, e.date_facture 
                        order by e.name desc limit 1
                    """
                    cr_odoo1.execute(SQL,[num_facture])
                    rows = cr_odoo1.fetchall()
                    for row in rows:
                        montant_ht   = row['total'];
                        montant_ttc  = row['total'];
                        date_facture = row['date_facture']

                obj.montant_ht      = montant_ht
                obj.montant_ttc     = montant_ttc
                obj.montant_paye_ht = montant_paye_ht
                obj.date_facture    = date_facture
                obj.date_echeance   = date_echeance
                obj.date_reglement  = date_reglement