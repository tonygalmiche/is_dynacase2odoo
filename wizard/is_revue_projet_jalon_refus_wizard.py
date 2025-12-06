# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class IsRevueProjetJalonRefusWizard(models.TransientModel):
    _name = 'is.revue.projet.jalon.refus.wizard'
    _description = 'Assistant de refus de revue de projet jalon'

    revue_projet_jalon_id = fields.Many2one('is.revue.projet.jalon', string="Revue de projet jalon", required=True)
    rpj_motif_refus = fields.Text(string="Motif du refus", required=True, 
                                   help="Veuillez indiquer le motif du refus de ce document")

    def action_confirmer_refus(self):
        """Confirme le refus du document avec le motif"""
        self.ensure_one()
        if not self.rpj_motif_refus:
            raise ValidationError("Le motif du refus est obligatoire.")
        
        # Récupérer l'utilisateur qui refuse
        user_refus = self.env.user
        
        # Mettre à jour le document avec sudo pour contourner les droits d'accès
        self.revue_projet_jalon_id.sudo().write({
            'rpj_motif_refus': self.rpj_motif_refus,
            'state': 'rpj_refus'
        })
        
        # Envoi du mail de refus à toute l'équipe projet
        self.revue_projet_jalon_id.sudo().envoi_mail_refus(self.rpj_motif_refus, user_refus)
