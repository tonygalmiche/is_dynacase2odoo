from odoo import models, fields, api, _

class IsFermetureGantt(models.Model):
    _name        = "is.fermeture.gantt"
    _description = "Fermeture du Gantt"
    _order = "name"

    name     = fields.Char(string="Intitulé", required=True)
    jour_ids = fields.One2many('is.fermeture.gantt.jour', 'fermeture_id')


class IsFermetureGanttJour(models.Model):
    _name        = "is.fermeture.gantt.jour"
    _description = "Jours de fermeture du Gantt"
    _order = "date_debut"

    fermeture_id = fields.Many2one("is.fermeture.gantt", string="Fermeture", required=True, ondelete='cascade')
    date_debut   = fields.Date(string="Date début", required=True)
    date_fin     = fields.Date(string="Date fin")
