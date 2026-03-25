# -*- coding: utf-8 -*-
from odoo import models, fields, api


class IsPromptIa(models.Model):
    _name = "is.prompt.ia"
    _description = "Prompt IA"
    _order = "modele_id, id"

    modele_id   = fields.Many2one("ir.model", string="Modèle", required=True, ondelete="cascade")
    field_id    = fields.Many2one("ir.model.fields", string="Champ")
    famille_ids = fields.Many2many("is.param.project", string="Familles", domain=[("type_document", "=", "Article")])
    prompt      = fields.Text(string="Prompt")

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
