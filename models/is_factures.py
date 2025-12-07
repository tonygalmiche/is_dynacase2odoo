# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
import psycopg2.extras
import logging
_logger = logging.getLogger(__name__)


class IsFactures(models.Model):
    _name = 'is.factures'
    _description = 'Factures'
    _order = 'date_facture desc'
    _rec_name = 'numero_facture'

    date_facture              = fields.Date(string='Date facture', required=True)
    numero_facture            = fields.Char(string='Numéro facture', required=True)
    supplier_invoice_number   = fields.Char(string='N° facture fournisseur', index=True)
    move_type                 = fields.Selection(
        selection=[
            ('in_invoice', 'Facture'),
            ('in_refund' , 'Avoir'),
        ],
        string='Type de facture'
    )
    montant_ht                = fields.Float(string='Montant HT', digits=(14, 2))
    site_id                   = fields.Many2one('is.database', "Site")

    def name_get(self):
        result = []
        for record in self:
            name = record.numero_facture
            if record.supplier_invoice_number:
                name = f"{name} ({record.supplier_invoice_number})"
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('numero_facture', operator, name), ('supplier_invoice_number', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)


    def actualiser_factures_action(self):
        user    = self.env['res.users'].browse(self._uid)
        company = user.company_id
        try:
            cnx0 = psycopg2.connect("dbname='"+self._cr.dbname+"' user='"+company.is_postgres_user+"' host='"+company.is_postgres_host+"' password='"+company.is_postgres_pwd+"'")
        except Exception:
            raise ValidationError('Postgresql 0 non disponible !')
        cur0 = cnx0.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        bases = self.env['is.database'].search([])
        nb=0
        for base in bases:
            cnx=False
            if base.database:
                x="dbname='"+base.database  +"' user='"+company.is_postgres_user+"' host='"+company.is_postgres_host+"' password='"+company.is_postgres_pwd+"'"
                try:
                    cnx  = psycopg2.connect(x)
                except Exception:
                    raise ValidationError('Postgresql non disponible !')
            if cnx:
                cur = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                SQL="""
                    SELECT  
                        am.id                          as facture_id,
                        am.name                        as numero_facture,
                        am.supplier_invoice_number     as supplier_invoice_number,
                        am.move_type                   as move_type,
                        am.invoice_date                as date_facture,
                        am.amount_untaxed              as montant_ht
                    FROM account_move am
                    WHERE am.move_type in ('in_invoice','in_refund')
                        AND am.state='posted'
                        AND am.invoice_date>='2025-01-01'
                """
                cur.execute(SQL)
                rows = cur.fetchall()
                for row in rows:
                    nb+=1
                    vals={
                        'site_id'                : base.id,
                        'numero_facture'         : row['numero_facture'],
                        'supplier_invoice_number': row['supplier_invoice_number'],
                        'move_type'              : row['move_type'],
                        'date_facture'           : row['date_facture'],
                        'montant_ht'             : row['montant_ht'],
                    }

                    #** Recherche si la facture existe déja *************
                    factures = self.env['is.factures'].search([('site_id','=',base.id),('numero_facture','=',row['numero_facture'])])
                    if len(factures)>0:
                        factures[0].write(vals)
                        action='write'
                    else:
                        self.env['is.factures'].create(vals)
                        action='create'
                    _logger.info("actualiser_factures_action : %s : %s : %s "%(base.database,action,row['numero_facture']))

                    #******************************************************


     
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Actualisation de %s factures"%nb,
                'type': 'success',
                'sticky': False,
            }
        }

