# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class IsOberthurRechercheMontageWizard(models.TransientModel):
    _name = 'is.oberthur.recherche.montage.wizard'
    _description = "Recherche Montage 1ier Flux pour saisie 2"

    montage = fields.Char(
        string="Montage 1ier Flux",
        required=True,
    )

    def action_rechercher(self):
        self.ensure_one()
        oberthur = self.env['is.oberthur'].search([('montage', '=', self.montage)], limit=1)
        if not oberthur:
            raise UserError("Le Montage 1ier Flux '%s' n'est pas trouvé." % self.montage)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'is.oberthur',
            'res_id': oberthur.id,
            'view_mode': 'form',
            'view_id': self.env.ref('is_dynacase2odoo.is_oberthur_saisie_2_view').id,
            'target': 'current',
        }
