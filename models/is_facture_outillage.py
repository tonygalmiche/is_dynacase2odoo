# -*- coding: utf-8 -*-
from odoo import models, fields, api, _      # type: ignore
from odoo.exceptions import ValidationError  # type: ignore
from datetime import datetime, timedelta, date
from subprocess import PIPE, Popen
import sys
import html
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


    def actualiser_action(self):
        for obj in self:
            obj.ligne_ids.actualiser_ligne_action()


    def cron_mail_reglement_depasse(self):
        "Mail des règlements des factures d'outillage dépassés, du lundi au samedi (ancien script dynacase/020)"
        today = date.today()
        if today.weekday() == 6:
            return
        lignes = self.env['is.facture.outillage.ligne'].with_context(active_test=False).search([
            ('date_reglement', '=', False),
            ('date_echeance', '<', today),
            ('facture_id.client_id', '!=', False),
        ]).sorted(key=lambda l: l.facture_id.create_date, reverse=True)
        titre = "Liste des règlements des factures d'outillages dépassés (<%s) (%s)" % (today.strftime('%d/%m/%Y'), len(lignes))
        colonnes = ['type', 'dossier', 'client', 'cial', 'type_facture', 'num_facture', 'montant_ht', 'montant_ttc',
                    'date_facture', 'date_echeance', 'commentaire']
        self._envoi_mail_lignes('reglement-depasse', titre, lignes, colonnes)


    def cron_mail_facture_a_faire(self):
        "Mail du jeudi des factures d'outillage à faire : date prévisionnelle atteinte et pas encore facturées"
        today = date.today()
        if today.weekday() != 3:
            return
        lignes = self.env['is.facture.outillage.ligne'].search([
            ('date_facture_prev', '<=', today),
            ('date_facture', '=', False),
            ('num_facture', 'in', [False, '']),
            ('facture_id.active', '=', True),
        ]).sorted(key=lambda l: (l.date_facture_prev, l.id))
        titre = "Liste des factures d'outillages à faire (date prévisionnelle <= %s) (%s)" % (today.strftime('%d/%m/%Y'), len(lignes))
        # Montants des lignes saisis seulement à la facturation : montant du dossier, sans total (plusieurs lignes par dossier)
        colonnes = ['type', 'dossier', 'client', 'cial', 'montant_dossier', 'date_facture_prev', 'commentaire']
        self._envoi_mail_lignes('facture-a-faire', titre, lignes, colonnes)


    def _envoi_mail_lignes(self, code, titre, lignes, colonnes):
        "Envoi du tableau des lignes de factures aux destinataires de la liste de diffusion 'code' (total si colonnes montant HT et TTC consécutives)"
        users = self.env['is.liste.diffusion.mail'].get_users('is.facture.outillage', code)
        if not users:
            _logger.warning("_envoi_mail_lignes : aucun destinataire dans la liste de diffusion '%s' (à renseigner dans le menu "
                            "Gestion des projets > Paramétrage > Liste de diffusion des mails : Facture outillage / %s)"%(code, code))
            return

        def montant(val):
            return '{0:,.2f}'.format(val).replace(',', ' ').replace('.', ',')

        def date_fr(val):
            return val.strftime('%d/%m/%Y') if val else ''

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        def lien(l):
            url = f"{base_url}/web#id={l.facture_id.id}&model=is.facture.outillage&view_type=form"
            return f"<a href='{url}'>{l.facture_id.type_dossier or ''}</a>"

        def client(l):
            c = l.facture_id.client_id
            return html.escape(f"{c.name or ''} ({c.is_code or ''}/{c.is_adr_code or ''})")

        # Colonne : (entête, alignement, retour à la ligne, valeur) ; retour à la ligne seulement pour Client et Commentaire
        definitions = {
            'type'             : ('Type'         , 'left'  , 'nowrap', lien),
            'dossier'          : ('Dossier'      , 'left'  , 'nowrap', lambda l: html.escape(l.facture_id.designation or '')),
            'client'           : ('Client'       , 'left'  , 'normal', client),
            'cial'             : ('Cial'         , 'left'  , 'nowrap', lambda l: html.escape(l.facture_id.commercial_id.name or '')),
            'type_facture'     : ('Type facture' , 'center', 'nowrap', lambda l: l.type_facture or ''),
            'num_facture'      : ('N° facture'   , 'center', 'nowrap', lambda l: html.escape(l.num_facture or '')),
            'montant_ht'       : ('Montant HT'   , 'right' , 'nowrap', lambda l: montant(l.montant_ht)),
            'montant_ttc'      : ('Montant TTC'  , 'right' , 'nowrap', lambda l: montant(l.montant_ttc)),
            'montant_dossier'  : ('Montant dossier', 'right', 'nowrap', lambda l: montant(l.facture_id.montant_dossier)),
            'date_facture_prev': ('Date prév.'   , 'center', 'nowrap', lambda l: date_fr(l.date_facture_prev)),
            'date_facture'     : ('Date facture' , 'center', 'nowrap', lambda l: date_fr(l.date_facture)),
            'date_echeance'    : ('Date échéance', 'center', 'nowrap', lambda l: date_fr(l.date_echeance)),
            'commentaire'      : ('Commentaire'  , 'left'  , 'normal', lambda l: html.escape(l.commentaire or '')),
        }
        td = 'style="border:1px solid black; padding:2pt 5pt; font-size:10pt; white-space:%s; text-align:%s"'
        th = 'style="border:1px solid black; padding:2pt 5pt; font-size:10pt; font-weight:bold; text-align:%s"'
        trs = []
        for ligne in lignes:
            cellules = [definitions[c] for c in colonnes]
            trs.append("<tr>%s</tr>" % "".join(f"<td {td % (wrap, align)}>{valeur(ligne)}</td>" for entete, align, wrap, valeur in cellules))
        if 'montant_ht' in colonnes:
            avant = colonnes.index('montant_ht')
            apres = len(colonnes) - avant - 2
            trs.append(f"""
                <tr>
                    <th colspan="{avant}" {th % 'right'}>Total : </th>
                    <th {th % 'right'}>{montant(sum(lignes.mapped('montant_ht')))}</th>
                    <th {th % 'right'}>{montant(sum(lignes.mapped('montant_ttc')))}</th>
                    {f'<th colspan="{apres}" {th % "left"}></th>' if apres else ''}
                </tr>
            """)
        entetes = "".join(f"<th {th % 'center'}>{definitions[c][0]}</th>" for c in colonnes)
        body_html = f"""
            <h2>{titre}</h2>
            <table style="width:100%; border:1px solid black; border-collapse:collapse;">
                <thead><tr>{entetes}</tr></thead>
                <tbody>{"".join(trs)}</tbody>
            </table>
            <p style="font-size:8pt; color:#888888;">
                Destinataires de ce mail à modifier dans Odoo : Gestion des projets > Paramétrage > Liste de diffusion des mails
                (Facture outillage / {code})
            </p>
        """
        mail = self.env['mail.mail'].sudo().create({
            'email_from': 'robot@plastigray.com',
            'email_to'  : self.env['is.liste.diffusion.mail'].users2mail(users),
            'subject'   : titre,
            'body_html' : body_html,
        })
        mail.send()


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

                        #** Recherche Date Facture dans IsCegidEcriture ****************************
                        ecriture = self.env['is.cegid.ecriture'].sudo().search([
                            ('e_general'   , '=', '411000'),
                            ('e_journal'   , '=', 'VTE'),
                            ('e_refinterne', '=', num_facture),
                        ], limit=1)
                        if ecriture:
                            date_facture = ecriture.e_datecomptable
                        #**************************************************************************

                        #** Recherche Date Réglement dans IsCegidEcriture *************************
                        ecriture_regl = self.env['is.cegid.ecriture'].sudo().search([
                            ('e_general'        , '=', '411000'),
                            ('e_journal'        , '!=', 'VTE'),
                            ('e_refinterne'     , '=', num_facture),
                            ('e_datecomptable'  , '>', '2024-01-01'),
                        ], order='e_datecomptable desc', limit=1)
                        if ecriture_regl:
                            date_reglement = ecriture_regl.e_datecomptable
                        #**************************************************************************

                        #** Montant payé dans IsCegidEcriture **************************************
                        ecritures_paye = self.env['is.cegid.ecriture'].sudo().search([
                            ('e_journal'    , '!=', 'VTE'),
                            ('e_refinterne' , '=', num_facture),
                            ('e_auxiliaire' , '>=', 'C500000'),
                            ('e_auxiliaire' , '<=', 'C509999'),
                        ])
                        montant_paye_ht = sum(e.e_credit for e in ecritures_paye)
                        #**************************************************************************


                        #** Recherche Date Echéance dans IsCegidEcriture **************************
                        ecriture_ech = self.env['is.cegid.ecriture'].sudo().search([
                            ('e_general'   , '=', '411000'),
                            ('e_journal'   , '!=', 'VTE'),
                            ('e_refinterne', '=', num_facture),
                        ], limit=1)
                        if ecriture_ech:
                            date_echeance = ecriture_ech.e_datper
                        #**************************************************************************

                        # #** Recherche Date Echéance dans CEGID *************************************
                        # SQL="""
                        #     select E_DATPER
                        #     from ECRITURE
                        #     where 
                        #         E_GENERAL='411000' and
                        #         E_JOURNAL!='VTE' and 
                        #         E_REFINTERNE='%s'
                        # """%num_facture
                        # rows_cegid = cr_cegid.execute(SQL)
                        # for row_cegid in rows_cegid:
                        #     date_echeance = row_cegid[0]
                        # #***************************************************************************





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