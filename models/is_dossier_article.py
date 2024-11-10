# -*- coding: utf-8 -*-
from odoo import models,fields,api

class is_dossier_article(models.Model):
    _inherit = 'is.dossier.article'

    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)
    doc_ids     = fields.One2many('is.dossier.article.doc', 'dossier_id')

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


    def initialiser_documents_dossier_article_action(self):
        for obj in self:
            domain=[
                ('type_document', '=', 'Article'),
            ]
            if obj.type_dossier=='matiere':
                domain.append(('dossier_matiere', '=', True))
            if obj.type_dossier=='colorant':
                domain.append(('dossier_colorant', '=', True))
            if obj.type_dossier=='composant':
                domain.append(('dossier_composant', '=', True))
            familles=self.env['is.param.project'].search(domain)
            for famille in familles:
                line_id=False
                for line in obj.doc_ids:
                    if line.param_project_id==famille:
                        line_id=line
                        break
                if not line_id:
                    vals={
                        'dossier_id'      : obj.id,
                        'param_project_id': famille.id,
                    }
                    line_id = self.env['is.dossier.article.doc'].create(vals)
                #** Recherche des docuements pour cette famille ***************
                domain=[
                    ('param_project_id'  , '=', famille.id),
                    ('dossier_article_id', '=', obj.id),
                ]
                docs=self.env['is.doc.moule'].search(domain)
                for doc in docs:
                    line_id.doc_id = doc.id
                #**************************************************************


class is_dossier_article_doc(models.Model):
    _name        = "is.dossier.article.doc"
    _description = "Documents du dossier article"
    _order       = 'param_project_id'

    dossier_id       = fields.Many2one("is.dossier.article", string="Dossier article", required=True, ondelete='cascade')
    param_project_id = fields.Many2one("is.param.project", string="Famille de document", required=True)
    doc_id           = fields.Many2one("is.doc.moule", string="Document")
    piecejointe      = fields.Text(string="Pièce jointe")

# dosart_fiche_tech  Fiche technique
# dosart_piecejointe Pièce jointe