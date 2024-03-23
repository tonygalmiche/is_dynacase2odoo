# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import format_date, formatLang, frozendict


class IsDocMoule(models.Model):
    _name        = "is.doc.moule"
    _description = "Document moule"
    _rec_name    = "param_project_id"


    def compute_project_prev(self):
        "for xml-rpc"
        self._compute_project_prev()
        return True

    @api.depends('param_project_id', 'param_project_id.ppr_color', 'param_project_id.ppr_icon')
    def _compute_project_prev(self):
        for record in self:
            project_prev = ""
            if record.param_project_id:
                img_src = ""
                if record.param_project_id.ppr_icon:
                    img_src = "<img class ='img-fluid' src='data:image/gif;base64," + str(record.param_project_id.ppr_icon,'utf-8') + "' height='60' width='60' />"
                new_add = "<div height='60px' width='100%' style='padding: 10px;margin-bottom:20px;font-size:18px;background-color: " + str(record.param_project_id.ppr_color or '') + ";'> " + img_src + " " + str(record.param_project_id.ppr_famille or '') + "</div>"
                project_prev += str(new_add)
            record.project_prev = project_prev

    project_prev     = fields.Html(compute='_compute_project_prev', store=True)
    project_prev2    = fields.Html()
    param_project_id = fields.Many2one("is.param.project", string="Famille de document")
    ppr_type_demande = fields.Selection(related="param_project_id.ppr_type_demande")
    type_document    = fields.Selection(related="param_project_id.type_document")
    ppr_icon         = fields.Image(related="param_project_id.ppr_icon", string="Icône", store=True)
    ppr_color        = fields.Char(related="param_project_id.ppr_color", string="Color", store=True)
    idmoule          = fields.Many2one("is.mold", string="Moule")

    dossier_article_id = fields.Many2one("is.dossier.article", string="Dossier article")

    idproject        = fields.Many2one(related="idmoule.project", string="Projet")
    idcp             = fields.Many2one(related="idmoule.chef_projet_id", string="CP")
    idresp           = fields.Many2one("res.users", string="Responsable")
    actuelle         = fields.Char(string="J Actuelle")
    demande          = fields.Char(string="Demande")
    action           = fields.Selection([
        ("I", "Initialisation"),
        ("R", "Révision"),
        ("V", "Validation"),
    ], string="Action")
    bloquant         = fields.Boolean(string="Point Bloquant")
    etat             = fields.Selection([
        ("AF", "A Faire"),
        ("F", "Fait"),
        ("D", "Dérogé"),
    ], string="État")
    fin_derogation   = fields.Date(string="Date de fin de dérogation")
    coefficient      = fields.Integer(string="Coefficient")
    note             = fields.Integer(string="Note")
    indicateur       = fields.Html(string="Indicateur")
    datecreate       = fields.Date(string="Date de création", default=fields.Date.context_today)
    dateend          = fields.Date(string="Date de fin")
    array_ids        = fields.One2many("is.doc.moule.array", "is_doc_id", string="Pièce-jointe de réponse à la demande")
    dynacase_id      = fields.Integer(string="Id dans Dynacase")
    duree            = fields.Float(string="Durée (H)", default=8)


    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


    def list_doc(self,name,ids):
        tree_id = self.env.ref('is_dynacase2odoo.is_doc_moule_edit_tree_view').id
        for obj in self:
           

            ctx={
                'default_idmoule': obj.idmoule.id,
            }
            # return {
            #     "name": "Colis "+obj.name,
            #     "view_mode": "tree,form",
            #     "res_model": "is.purchase.order.line.colis",
            #     "domain": [
            #         ("line_id","=",obj.id),
            #     ],
            #     "type": "ir.actions.act_window",
            #     "context": ctx,
            # }



            return {
                'name': name,
                'view_mode': 'tree,form,kanban,calendar,pivot,graph',
                "views"    : [(tree_id, "tree"),(False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
                'res_model': 'is.doc.moule',
                'domain': [
                    ('id','in',ids),
                ],
                'type': 'ir.actions.act_window',
                "context": ctx,
                'limit': 1000,
            }
        
        # ValueError: External ID not found in the system: is_dynacase2odoo.is_doc_moule_edit_tree_view

            # form_id = self.env.ref('is_clair_sarl.is_account_move_line_form_view').id
            # return {
            #     "name": "Lignes des factures ",
            #     "view_mode": "tree,form",
            #     "res_model": "account.move.line",
            #     "domain": [
            #         ("is_affaire_id","=",obj.affaire_id.id),
            #         ("is_famille_id","=",obj.famille_id.id),
            #         ("exclude_from_invoice_tab","=",False),
            #         ("journal_id","=",2),
            #         ("move_id.state","=","posted"),
            #     ],
            #     "type": "ir.actions.act_window",
            #     "views"    : [[tree_id, "tree"],[form_id, "form"]],




# is_doc_moule_edit_tree_view

    def doc_moule_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('idmoule', '=', obj.idmoule.id) ])
            ids=[]
            for doc in docs:
                ids.append(doc.id)
            return obj.list_doc(obj.idmoule.name,ids)


    def doc_projet_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('idproject', '=', obj.idproject.id) ])
            ids=[]
            for doc in docs:
                ids.append(doc.id)
            return obj.list_doc(obj.idproject.name,ids)



class IsDocMouleArray(models.Model):
    _name        = "is.doc.moule.array"
    _description = "Document moule array"

    annex_pdf   = fields.Many2many("ir.attachment", "attach_annex_pdf_rel", "annex_pdf_id", "att_id", string="Fichiers PDF")
    annex       = fields.Many2many("ir.attachment", "attach_annex_rel", "annex_id", "attachment_id", string="Fichiers")
    demandmodif = fields.Char(string="Demande de modification")
    maj_amdec   = fields.Boolean(string="Mise à jour de l’AMDEC")
    comment     = fields.Text(string="Commentaire")
    rsp_date    = fields.Date(string="Date")
    rsp_texte   = fields.Char(string="Réponse à la demande")
    is_doc_id   = fields.Many2one("is.doc.moule")
