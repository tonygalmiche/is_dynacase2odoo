# -*- coding: utf-8 -*-
from odoo import models, fields, api


class IsNormeCdc(models.Model):
    _name = 'is.norme.cdc'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = 'Norme CDC'
    _rec_name = "reference"
    _order = 'reference'

    active                   = fields.Boolean(string='Actif', default=True,                       tracking=True)
    niveau                   = fields.Char(string='Niveau', required=True,                        tracking=True)
    reference                = fields.Char(string='Référence', required=True,                     tracking=True)
    designation              = fields.Text(string='Désignation-Projet', required=True,            tracking=True)
    sujet                    = fields.Char(string='Sujet',                                        tracking=True)
    createur                 = fields.Char(string='Créateur',                                     tracking=True)
    indice                   = fields.Char(string='Indice',                                       tracking=True)
    date                     = fields.Char(string='Date',                                         tracking=True)
    datepg                   = fields.Char(string="Date d'application PG",                        tracking=True)
    date_prochaine_alerte    = fields.Date(string='Date prochaine alerte',                        tracking=True)
    lieu_physique            = fields.Char(string='Lieu physique',                                tracking=True)
    lieu_info                = fields.Char(string='Lieu informatique',                            tracking=True)
    etat                     = fields.Char(string='État',                                         tracking=True)
    date_verif               = fields.Char(string='Date de dernière vérification de mise à jour', tracking=True)
    duree_conserv            = fields.Char(string='Durée de conservation',                        tracking=True)
    lien_internet            = fields.Char(string='Lien vers Internet',                           tracking=True)
    attachment_ids           = fields.Many2many("ir.attachment", "is_norme_cdc_attachment_rel", "norme_id", "att_id", string="Fichiers")
    attachment_names         = fields.Text(string='Noms des fichiers', compute='_compute_attachment_names', store=True, tracking=True)
    dynacase_id              = fields.Integer(string="Id Dynacase", index=True, copy=False)


    @api.depends('attachment_ids.name')
    def _compute_attachment_names(self):
        for record in self:
            if record.attachment_ids:
                names = record.attachment_ids.mapped('name')
                record.attachment_names = '\n'.join(names)
            else:
                record.attachment_names = False


    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
