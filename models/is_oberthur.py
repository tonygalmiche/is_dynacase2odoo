from odoo import models, fields         # type: ignore


_TYPE = [
        ("", ""),
        ("B", "Bon"),
        ("M", "Mauvais"),
        ]


class is_oberthur(models.Model):
    _name='is.oberthur'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Oberthur"
#    _rec_name = "numero"
#    _order='create_date desc'

    montage   = fields.Char("Montage 1ier Flux", tracking=True)
    coque     = fields.Char("Coque Interne", tracking=True)
    batterie  = fields.Char("K0008B27788", tracking=True)
    harnais   = fields.Char("Harnais CE-CI", tracking=True)
    numof     = fields.Char("N° OF", tracking=True)
    continu1  = fields.Selection(_TYPE, "Continuité Maillage 1", tracking=True)
    tensiong  = fields.Float("Tension Batterie Gauche", digits=(5, 2), tracking=True)
    tensiond  = fields.Float("Tension Batterie Droite", digits=(5, 2), tracking=True)
    bransubd  = fields.Selection(_TYPE, "Branchement SubD25", tracking=True)
    blocvis   = fields.Selection(_TYPE, "Blocage 2 Vis 8059", tracking=True)
    soudure   = fields.Selection(_TYPE, "Aspect Soudure", tracking=True)
    continu2  = fields.Selection(_TYPE, "Continuité Maillage 2", tracking=True)
    ctrelect  = fields.Selection(_TYPE, "Contrôle Électrique Final", tracking=True)
    date      = fields.Integer("Date saisie", tracking=True)
    heure     = fields.Integer("Heure", tracking=True)
    operateu  = fields.Char("Opérateur 1", tracking=True)
    operateu2 = fields.Char("Opérateur 2", tracking=True)
    controle  = fields.Char("Controleur", tracking=True)
    reprise   = fields.Char("Ordre Reprise", tracking=True)
    comment   = fields.Char("Commentaire", tracking=True)
    modif     = fields.Boolean(string="Modif", store=False)
