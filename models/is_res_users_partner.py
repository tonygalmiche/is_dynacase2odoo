# -*- coding: utf-8 -*-

from odoo import tools,models,fields


class is_res_users_partner(models.Model):
    _name='is.res.users.partner'
    _description='Annuaires téléphonqiue'
    _order='site,name'
    _auto = False

    site       = fields.Char('Site')
    name       = fields.Char('Nom')
    email      = fields.Char('Email')
    user_id    = fields.Many2one('res.users', 'Utilisateur')
    partner_id = fields.Many2one('res.partner', 'Contact')
    service_id = fields.Many2one('is.service', 'Service')
    phone      = fields.Char('Téléphone')
    mobile     = fields.Char('Mobile')
    login      = fields.Char('Login')
    standard_telephonique = fields.Char('Standard téléphonique')
    is_ligne_directe      = fields.Boolean('Ligne directe', help="Indique si l’utilisateur a une ligne directe pour apparaître dans l'annuaire téléphonique")


    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, 'is_res_users_partner')
        cr.execute("""
            CREATE OR REPLACE view is_res_users_partner AS (
                select
                   rp.id,
                   ru.id         as user_id,
                   ru.partner_id as partner_id,
                   rp.name,
                   rp.email,
                   s.name as site,
                   ru.is_service_id as service_id,
                   rp.phone,
                   rp.mobile,
                   ru.login,
                   ru.is_ligne_directe,
                   s.standard_telephonique
                from res_users ru inner join res_partner rp on ru.partner_id=rp.id
                                        join is_database s on ru.is_site_id=s.id
                where ru.active=true and rp.active=true and ru.id not in (2)
                order by s.name,rp.name
                   
            )
        """)

