from odoo import models, fields, api         # type: ignore
from odoo.exceptions import ValidationError  # type: ignore
from datetime import datetime


class is_plan_amelioration_continu(models.Model):
    _name='is.plan.amelioration.continu'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Plan d'amélioration continu"
    _rec_name = "numero"
    _order='numero desc'

    numero              = fields.Integer('Numéro', tracking=True)
    active              = fields.Boolean('Actif', default=True, tracking=True)
    type                = fields.Selection([('pac', 'PAC'), ('revue', 'Revue')], "Type", required=True, tracking=True)
    createur_id         = fields.Many2one('res.users', 'Créateur', required=True, default=lambda self: self.env.uid, tracking=True)
    site_id             = fields.Many2one('is.database', "Site", tracking=True)
    service_id          = fields.Many2one('res.groups', "Service", tracking=True)
    processus_id        = fields.Char('Processus', tracking=True)
    annee               = fields.Char('Année', default=lambda self: datetime.now().year, store=True, tracking=True)
    mois                = fields.Char('Mois', default=lambda self: str(datetime.now().month) if datetime.now().month > 9 else '0' + str(datetime.now().month), tracking=True)
    groupe_acces_id     = fields.Many2one('res.groups', "Groupe d'accès en consultation Id", tracking=True)
    plan_action_ids     = fields.Many2many('is.plan.action','is_plan_amelioration_continu_plan_action_rel','plan_amelioration_continu_id','plan_action_id', string="Plan d'actions", tracking=True)
    piece_jointe_ids    = fields.Many2many("ir.attachment", "is_plan_amelioration_continu_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
    dynacase_id         = fields.Integer(string="Id Dynacase", index=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._rec_name not in vals:
                last = self.env[self._name].search([(self._rec_name, '!=', None)], order=self._rec_name + " desc", limit=1)
                if last:
                    vals[self._rec_name] = getattr(last, self._rec_name) + 1
                else:
                    vals[self._rec_name] = 0
        return super().create(vals_list)

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
