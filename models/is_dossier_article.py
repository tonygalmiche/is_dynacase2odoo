# -*- coding: utf-8 -*-
from odoo import models,fields,api

class is_dossier_article(models.Model):
    _inherit = 'is.dossier.article'

    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)
    doc_ids     = fields.One2many('is.dossier.article.doc', 'dossier_id')
    nb_a_faire  = fields.Integer(string="Nb doc à faire", compute='_compute_fait',store=True,readonly=True)
    nb_crees    = fields.Integer(string="Nb doc créés"  , compute='_compute_fait',store=True,readonly=True)
    nb_fait     = fields.Integer(string="Nb doc fait"   , compute='_compute_fait',store=True,readonly=True)


    @api.depends('doc_ids', 'doc_ids.doc_id', 'doc_ids.piecejointe')
    def _compute_fait(self):
        for obj in self:
            nb_a_faire = nb_crees = nb_fait = 0
            for line in obj.doc_ids:
                nb_a_faire+=1
                if line.doc_id:
                    nb_crees+=1
                if line.piecejointe:
                    nb_fait+=1
            obj.nb_a_faire = nb_a_faire
            obj.nb_crees   = nb_crees
            obj.nb_fait    = nb_fait


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
                    line_id.piecejointe = doc.rsp_pj
                #**************************************************************
            obj._compute_fait()
        return []


class is_dossier_article_doc(models.Model):
    _name        = "is.dossier.article.doc"
    _description = "Documents du dossier article"
    _order       = 'param_project_id'

    dossier_id       = fields.Many2one("is.dossier.article", string="Dossier article", required=True, ondelete='cascade')
    param_project_id = fields.Many2one("is.param.project", string="Famille de document", required=True)
    doc_id           = fields.Many2one("is.doc.moule", string="Document")
    piecejointe      = fields.Text(string="Pièce jointe", compute='_compute_piecejointe',store=True,readonly=True)


    @api.depends('doc_id', 'doc_id.rsp_pj')
    def _compute_piecejointe(self):
        for obj in self:
            obj.piecejointe = obj.doc_id.rsp_pj


    def creer_doc_action(self):
        for obj in self:
            vals={
                'type_document'     : 'Article',
                'dossier_article_id': obj.dossier_id.id,
                'param_project_id'  : obj.param_project_id.id,
            }
            doc = self.env['is.doc.moule'].create(vals)
            obj.doc_id = doc.id
