# -*- coding: utf-8 -*-
from odoo import models, fields  # type: ignore


class IsProcessus(models.Model):
    _name = 'is.processus'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = 'Processus'
    _order = "numpcs"
    _rec_name = 'numpcs'



    active       = fields.Boolean(string="Actif", default=True, tracking=True)
    dynacase_id  = fields.Integer(string="Id Dynacase", index=True, copy=False)

    # Identification
    numpcs       = fields.Char(string="Numéro du processus", required=False, tracking=True)
    numindice    = fields.Char(string="Indice", required=False, tracking=True)
    nom          = fields.Char(string="Nom du processus", required=False, tracking=True)
    pilotepcs_id = fields.Many2one('res.users', 'Pilote du processus', required=False, default=lambda self: self.env.uid, tracking=True)
    niveau       = fields.Char(string="Niveau", tracking=True)
    exigence     = fields.Char(string="Liste des exigences", tracking=True)

    # Informations textuelles
    element       = fields.Text(string="Éléments déclencheurs", tracking=True)
    donneesentree = fields.Text(string="Données d'entrée", tracking=True)
    donneessortie = fields.Text(string="Données de sortie", tracking=True)
    finalite      = fields.Text(string="Finalité", tracking=True)
    efficience    = fields.Text(string="Efficience", tracking=True)
    efficacite    = fields.Text(string="Efficacité", tracking=True)

    # Cycle (qui vérifie / qui approuve / diffusion)
    quiverifie_id  = fields.Many2one('res.users', 'Qui vérifie', tracking=True)
    quiapprouve_id = fields.Many2one('res.users', 'Qui approuve', tracking=True)
    diffusion      = fields.Char(string="Diffusion", tracking=True)

    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
