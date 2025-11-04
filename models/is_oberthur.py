from odoo import models, fields, api         # type: ignore
from datetime import datetime, timedelta


class is_oberthur(models.Model):
    _name='is.oberthur'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Oberthur"
#    _rec_name = "numero"
#    _order='create_date desc'

    montage   = fields.Char("Montage 1ier Flux", tracking=True)
    coque     = fields.Char("Coque Interne", tracking=True)
    batterie  = fields.Char("K0008B27788", tracking=True)
    harnais   = fields.Char("Harnais", tracking=True)
    numof     = fields.Char("N° OF", tracking=True)
    continu1  = fields.Char("Continuité Maillage", tracking=True)
    tensiong  = fields.Float("Tension Gauche", digits=(5, 2), tracking=True)
    tensiond  = fields.Float("Tension Droite", digits=(5, 2), tracking=True)
    bransubd  = fields.Float("Branch. Sub-D", digits=(5, 2), tracking=True)
    blocvis   = fields.Char("Blocage Vis", tracking=True)
    soudure   = fields.Char("Soudure", tracking=True)
    continu2  = fields.Char("Continuité Maillage", tracking=True)
    ctrelect  = fields.Char("Contrôle Final", tracking=True)
    date      = fields.Integer("Date saisie", tracking=True)
    heure     = fields.Integer("Heure", tracking=True)
    operateu  = fields.Char("Opérateur 1", tracking=True)
    operateu2 = fields.Char("Opérateur 2", tracking=True)
    controle  = fields.Char("Controleur", tracking=True)
    reprise   = fields.Char("Reprise", tracking=True)
    comment   = fields.Char("Commentaire", tracking=True)
