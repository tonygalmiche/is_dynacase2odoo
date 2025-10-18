# -*- coding: utf-8 -*-
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class IsReleveDimensionnel(models.Model):
    _name        = "is.releve.dimensionnel"
    _description = "Relevé dimensionnel"
    _rec_name    = "numreleve"
    _order       = "id desc"

    numreleve   = fields.Char(string="N° du relevé")
    moule       = fields.Char(string="Moule")
    createur    = fields.Char(string="Créateur")
    minimum     = fields.Float(string="Relevé minimum", digits=(12, 2))
    maximum     = fields.Float(string="Relevé maximum", digits=(12, 2))
    saisir      = fields.Char(string="Saisir des données")
    active      = fields.Boolean('Actif', default=True)
    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)    
    saisie_ids  = fields.One2many("is.releve.dimensionnel.saisie", "releve_id", string="Saisies de relevés")
    ligne_ids   = fields.One2many("is.releve.dimensionnel.saisie.ligne", "releve_id", string="Lignes de saisies")


    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }


class IsReleveDimensionnelSaisie(models.Model):
    _name        = "is.releve.dimensionnel.saisie"
    _description = "Saisie de relevé dimensionnel"
    _rec_name    = "numsaisie"
    _order       = "id"

    releve_id   = fields.Many2one("is.releve.dimensionnel", string="Relevé", required=True, ondelete="cascade", index=True)
    numsaisie   = fields.Integer(string="N° de saisie")
    datesaisie  = fields.Date(string="Date de saisie")
    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)    
    ligne_ids   = fields.One2many("is.releve.dimensionnel.saisie.ligne", "saisie_id", string="Lignes de saisies")


    def voir_saisie_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Saisie',
            'res_model': 'is.releve.dimensionnel.saisie',
            'res_id': self.id,
            'view_mode': 'form',
        }


    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }




class IsReleveDimensionnelSaisieLigne(models.Model):
    _name        = "is.releve.dimensionnel.saisie.ligne"
    _description = "Ligne de saisie de relevé dimensionnel"
    _rec_name    = "id"
    _order       = "id"

    saisie_id = fields.Many2one("is.releve.dimensionnel.saisie", string="Saisie", required=True, ondelete="cascade", index=True)
    releve_id = fields.Many2one("is.releve.dimensionnel", string="Relevé", related="saisie_id.releve_id", store=True, index=True)
    numof     = fields.Char(string="N°OF")
    numcolis  = fields.Char(string="N°Colis")
    visa      = fields.Char(string="Visa Contrôleur")
    releve    = fields.Float(string="Mesure relevéé", digits=(12, 6))
    resultat  = fields.Char(string="Résultat")


