# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class IsProcessusDocRevisionWizard(models.TransientModel):
    _name = 'is.processus.doc.revision.wizard'
    _description = 'Assistant de révision de document'

    document_id = fields.Many2one('is.processus.doc', string="Document", required=True)
    motif_revision = fields.Text(string="Motif de révision", required=True, 
                                help="Veuillez indiquer le motif de cette révision")

    def action_confirmer_revision(self):
        """Confirme et lance la révision du document"""
        self.ensure_one()
        if not self.motif_revision:
            raise ValidationError("Le motif de révision est obligatoire.")
        
        # Appeler la méthode de révision sur le document
        self.document_id.reviser_document(self.motif_revision)
        
        # Fermer le wizard et afficher une notification
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': 'Révision effectuée',
        #         'message': 'Le document a été révisé avec succès. L\'ancienne version a été archivée.',
        #         'type': 'success',
        #         'sticky': False,
        #     }
        # }