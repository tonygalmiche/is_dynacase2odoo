# -*- coding: utf-8 -*-
from odoo import models,fields,api           # type: ignore
import datetime
import pytz
import psycopg2                              # type: ignore
import psycopg2.extras                       # type: ignore
from odoo.exceptions import ValidationError  # type: ignore
import logging
_logger = logging.getLogger(__name__)





class is_reception(models.Model):
    _name='is.reception'
    _description="Réceptions de tous les sites"
    _order='date_reception desc,numero_reception'
    _rec_name = "numero_reception"

    database_id           = fields.Many2one("is.database", "Site", index=True)
    numero_reception      = fields.Char("Numéro de réception", index=True)
    move_id               = fields.Integer("Mouvemement", help="Ligne réception", index=True)
    fournisseur_id        = fields.Many2one('res.partner', 'Fournisseur', domain=[("is_company","=",True), ("supplier","=",True)])
    code_pg               = fields.Char("Référence PG", index=True)
    designation           = fields.Char("Désignation")
    moule                 = fields.Char("Moule")
    reference_fournisseur = fields.Char("Référence fournisseur")
    numero_bl_fournisseur = fields.Char("Numéro de BL fournisseur")
    numero_commande       = fields.Char("Numéro de commande")
    prix_achat_commande   = fields.Float("Prix achat commande", digits=(16, 4))
    quantite_livree       = fields.Float("Quantité livrée", digits=(16, 4))
    date_reception        = fields.Date("Date de réception", index=True)



    def actualiser_receptions_action(self):
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
                    select  
                        sm.id                     as move_id,
                        sp.name                   as numero_reception,
                        sp.is_date_reception      as date_reception,
                        rp.is_database_origine_id as fournisseur_id,
                        pt.is_code                as code_pg,
                        pt.name->>'fr_FR'         as designation,
                        pt.is_ref_fournisseur     as reference_fournisseur,
                        pt.is_mold_dossierf       as moule,
                        sp.is_num_bl              as numero_bl_fournisseur,
                        po.name                   as numero_commande,
                        pol.price_unit            as prix_achat_commande,
                        round(coalesce(sm.quantity_done/sm.is_unit_coef,0),4) as quantite_livree
                    from stock_picking sp inner join stock_move                sm on sm.picking_id=sp.id 
                                        inner join product_product           pp on sm.product_id=pp.id
                                        inner join product_template          pt on pp.product_tmpl_id=pt.id
                                        left outer join purchase_order_line pol on sm.purchase_line_id=pol.id
                                        left outer join purchase_order       po on pol.order_id=po.id
                                        join res_partner rp on sp.partner_id=rp.id
                                        join is_category ic on pt.is_category_id=ic.id
                    where sp.picking_type_id=1
                        and sm.state='done'
                        and sp.state='done'
                        and sp.is_date_reception>='2025-01-01'
                        and (ic.name::INTEGER<=60 or ic.name in ('71','72'))
                """
                cur.execute(SQL)
                rows = cur.fetchall()
                for row in rows:
                    nb+=1
                    vals={
                        'database_id'          : base.id,
                        'move_id'              : row['move_id'],
                        'numero_reception'     : row['numero_reception'],
                        'date_reception'       : row['date_reception'],
                        'fournisseur_id'       : row['fournisseur_id'],
                        'code_pg'              : row['code_pg'],
                        'designation'          : row['designation'],
                        'moule'                : row['moule'],
                        'reference_fournisseur': row['reference_fournisseur'],
                        'numero_bl_fournisseur': row['numero_bl_fournisseur'],
                        'numero_commande'      : row['numero_commande'],
                        'prix_achat_commande'  : row['prix_achat_commande'],
                        'quantite_livree'      : row['quantite_livree'],
                    }

                    #** Recherche si la fournisseur existe ********************
                    fournisseurs = self.env['res.partner'].search([('id','=',row['fournisseur_id'])])
                    if len(fournisseurs)>0:
                        #** Recherche si la réception existe déja *************
                        receptions = self.env['is.reception'].search([('database_id','=',base.id),('move_id','=',row['move_id'])])
                        if len(receptions)>0:
                            receptions[0].write(vals)
                            action='write'
                        else:
                            self.env['is.reception'].create(vals)
                            action='create'
                        _logger.info("actualiser_receptions_action : %s : %s : %s "%(base.database,action,row['numero_reception']))

                        #******************************************************


     
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Actualisation de %s réceptions"%nb,
                #'message': "Exportation vers O'Work éffectutée",
                'type': 'success',
                'sticky': False,
            }
        }




    # def exporter_receptions_owork_action(self):
    #     name = "exporter-receptions-owork"
    #     cdes = self.env['is.commande.externe'].search([('name','=',name)])
    #     if len(cdes)==0:
    #         raise ValidationError("Commande externe '%s' non trouvée !"%name)
    #     for cde in cdes:
    #         p = Popen(cde.commande, shell=True, stdout=PIPE, stderr=PIPE)
    #         stdout, stderr = p.communicate()
    #         _logger.info("%s => %s"%(cde.commande,stdout))
    #         if stderr:
    #             raise ValidationError("Erreur dans commande externe '%s' => %s"%(cde.commande,stderr))
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': "Exportation vers O'Work éffectutée",
    #             #'message': "Exportation vers O'Work éffectutée",
    #             'type': 'success',
    #             'sticky': False,
    #         }
    #     }