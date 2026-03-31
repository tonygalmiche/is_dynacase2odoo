# -*- coding: utf-8 -*-
from odoo import models, fields, api


class IsPromptIa(models.Model):
    _name = "is.prompt.ia"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Prompt IA"
    _rec_name = "id"
    _order = "modele_id, id"

    modele_id   = fields.Many2one("ir.model", string="Modèle", required=True, ondelete="cascade", tracking=True)
    field_id    = fields.Many2one("ir.model.fields", string="Champ", tracking=True)
    famille_ids = fields.Many2many("is.param.project", string="Familles", domain=[("type_document", "=", "Article")], tracking=True)
    prompt      = fields.Text(string="Prompt", tracking=True)
    reflexion   = fields.Boolean(string="Réflexion", default=False, tracking=True)
    detail_analyse_ia = fields.Boolean(string="Détail analyse IA", default=True, tracking=True, help="Si coché, créer une ligne de détail dans l'analyse IA. Sinon, juste mettre à jour le champ.")
    prompt_actif = fields.Boolean(string="Prompt actif", default=True, tracking=True, help="Si décoché, ce prompt ne sera pas utilisé lors des analyses IA.")
    active      = fields.Boolean(string="Actif", default=True, tracking=True)

    @api.onchange("modele_id")
    def _onchange_modele_id(self):
        self.field_id = False
        if self.modele_id:
            return {
                "domain": {
                    "field_id": [
                        ("model_id", "=", self.modele_id.id),
                        ("ttype", "not in", ["many2many", "one2many", "reference", "binary", "serialized"]),
                        ("store", "=", True),
                    ]
                }
            }
        return {
            "domain": {
                "field_id": []
            }
        }
