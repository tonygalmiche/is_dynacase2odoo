# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import format_date, formatLang, frozendict
from datetime import datetime
from random import *

class IsDocMoule(models.Model):
    _name        = "is.doc.moule"
    _inherit=['mail.thread']
    _description = "Document moule"
    _rec_name    = "param_project_id"
    _order = 'sequence, param_project_id'


    def compute_project_prev(self):
        "for xml-rpc"
        self._compute_project_prev()
        self._compute_idproject()
        return True

    @api.depends('param_project_id', 'param_project_id.ppr_color', 'param_project_id.ppr_icon')
    def _compute_project_prev(self):
        for record in self:
            project_prev = ""
            if record.param_project_id:
                img = ""
                if record.param_project_id.ppr_icon:
                    img = "<img class ='img-fluid' src='data:image/gif;base64," + str(record.param_project_id.ppr_icon,'utf-8') + "' style='max-height:30px' />"
                title = str(record.param_project_id.ppr_famille or '')
                color = str(record.param_project_id.ppr_color or '')
                new_add = """
                    <div height='60px' width='100%' style='padding: 10px;margin-bottom:20px;font-size:18px;background-color:"""+color+"""'>
                        """+img+"""<span style='margin-left:5px;background-color:white'>"""+title+"""</span>
                    </div>
                """
                project_prev += str(new_add)
            record.project_prev = project_prev


    @api.depends('idmoule', 'dossierf_id')
    def _compute_idproject(self):
        for obj in self:
            idproject = obj.idmoule.project.id or obj.dossierf_id.project.id
            obj.idproject = idproject


    type_document = fields.Selection([
        ("Moule"                 , "Moule"),
        ("Dossier F"             , "Dossier F"),
        ("Article"               , "Article"),
        ("Dossier Modif Variante", "Dossier Modif Variante"),
    ],string="Type de document", default="Moule", required=True)

    sequence = fields.Integer(string="Ordre")
    project_prev     = fields.Html(compute='_compute_project_prev', store=True)
    project_prev2    = fields.Html()
    param_project_id = fields.Many2one("is.param.project", string="Famille de document")
    ppr_type_demande = fields.Selection(related="param_project_id.ppr_type_demande")
    ppr_icon         = fields.Image(related="param_project_id.ppr_icon", string="Icône", store=True)
    ppr_color        = fields.Char(related="param_project_id.ppr_color", string="Color", store=True)

    idmoule                   = fields.Many2one("is.mold"                  , string="Moule")
    dossierf_id               = fields.Many2one("is.dossierf"              , string="Dossier F")
    dossier_modif_variante_id = fields.Many2one("is.dossier.modif.variante", string="Dossier Modif / Variante")
    dossier_article_id        = fields.Many2one("is.dossier.article"       , string="Dossier article")

    idproject        = fields.Many2one("is.mold.project", string="Projet",compute='_compute_idproject',store=True, readonly=True)
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
    dynacase_id      = fields.Integer(string="Id Dynacase")
    duree               = fields.Integer(string="Durée (J)", default=1)
    duree_attente_avant = fields.Integer("Durée attente avant (J)", help="Utilisée dans le Gantt")
    date_debut_gantt    = fields.Date(string="Date début Gantt")
    date_fin_gantt      = fields.Date(string="Date fin Gantt")
    dependance_id       = fields.Many2one("is.doc.moule", string="Dépendance")


    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


    def acceder_doc_action(self):
        for obj in self:
            print(obj)

            res= {
                'name': 'Doc',
                'view_mode': 'form',
                'res_model': 'is.doc.moule',
                'res_id': obj.id,
                #'view_id': view_id.id,
                'type': 'ir.actions.act_window',
            }
            return res


            # return {
            #         'name': obj.name,
            #         'view_mode': 'form,tree',
            #         "views"    : [
            #             (gantt_id, "dhtmlxgantt_project"),
            #             (tree_id, "tree"),
            #             (False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
            #         'res_model': 'is.doc.moule',
            #         'domain': [
            #             ('id','in',ids),
            #         ],
            #         'type': 'ir.actions.act_window',
            #         "context": ctx,
            #         'limit': 1000,
            #     }


    def list_doc(self,obj,ids, view_mode=False,initial_date=False):
        if not view_mode:
            return False
        tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_edit_tree_view').id
        gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
        ctx={}
        if obj._name=='is.mold':
            ctx={
                'default_idmoule': obj.id,
                'default_etat'   :'AF',
                'default_dateend': datetime.today(),
                'default_idresp' : self._uid,
                'initial_date'   : initial_date,
            }
        return {
            'name': obj.name,
            'view_mode': view_mode,
            "views"    : [
                (gantt_id, "dhtmlxgantt_project"),
                (tree_id, "tree"),
                (False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
            'res_model': 'is.doc.moule',
            'domain': [
                ('id','in',ids),
            ],
            'type': 'ir.actions.act_window',
            "context": ctx,
            'limit': 1000,
        }
             

    def doc_moule_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('idmoule', '=', obj.idmoule.id) ])
            ids=[]
            initial_date=str(datetime.today())
            for doc in docs:
                if str(doc.dateend)<initial_date:
                    initial_date=str(doc.dateend)
                ids.append(doc.id)
            view_mode = 'tree,form,dhtmlxgantt_project,kanban,calendar,pivot,graph'
            return obj.list_doc(obj.idmoule,ids,view_mode=view_mode,initial_date=initial_date)


    def doc_projet_action(self):
        for obj in self:
            return obj.idproject.gantt_action()


    def doc_dossierf_action(self):
        for obj in self:
            return obj.dossierf_id.gantt_action()


    @api.model
    def get_dhtmlx(self, domain=[]):
        print(domain)
        lines=self.env['is.doc.moule'].search(domain, limit=500) #, order="dateend"
        print(lines)

        # #** Ajout des moules ************************************************
        res=[]
        moules=[]
        for line in lines:
            if line.idmoule not in moules:
                moules.append(line.idmoule or line.dossierf_id or line.dossier_modif_variante_id)
        for moule in moules:
            if hasattr(moule, 'name'):
                name=moule.name
                project=moule.project.name
            else:
                name=moule.demao_num
                project='?'

            text="%s (%s)"%(name,project)
            infobulle_list=[]
            infobulle_list.append("<b>Moule</b>: %s"%(name))
            vals={
                "id": moule.id+100000,
                "text": text,
                "start_date": False,
                "duration": False,
                "parent": 0,
                "progress": 0,
                "open": True,
                #"assigned": project.user_id.name,
                "priority": 2,
                "infobulle": "<br>\n".join(infobulle_list)
            }
            res.append(vals)
        # #**********************************************************************


        print(res)


        #** Ajout des documents des moules **************************************
        for line in lines:
            print(line.param_project_id.ppr_famille,line.dateend)
            if line.dateend:
                priority = round(2*random()) # Nombre aléatoire entre 0 et 2
                famille=line.param_project_id.ppr_famille
                name=famille
                if famille=='Autre':
                    name="%s (Autre)"%line.demande
                else:
                    name=famille
                if line.param_project_id.ppr_revue_lancement:
                    name="%s [%s]"%(name,line.param_project_id.ppr_revue_lancement)
                duration = line.duree or 1
                infobulle_list=[]
                infobulle_list.append("<b>Document</b>           : %s"%name)
                vals={
                    "id": line.id,
                    "text": name,
                    "end_date": str(line.dateend)+' 02:00:00"',
                    "duration": duration,
                    "parent": (line.idmoule.id or line.dossierf_id.id or line.dossier_modif_variante_id.id)+100000,
                    #"assigned": line.user_id.name,
                    #"progress": line.progress/100,
                    "priority": priority,
                    "infobulle": "<br>\n".join(infobulle_list)
                }
                res.append(vals)
        #**********************************************************************


        #** Ajout des dependances *********************************************
        links=[]
        ct=1
        mem_line=False
        mem_moule=False
        for line in lines:
            if mem_moule!=line.idmoule:
                mem_line=False
            if mem_line:
                vals={
                    "id":ct,
                    "source": mem_line.id,
                    "target": line.id,
                    "type":0,
                }
                links.append(vals)
                ct+=1
            mem_line = line
            mem_moule = line.idmoule
        #**********************************************************************

        return {"items":res, "links": links}







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





class is_mold(models.Model):
    _inherit = 'is.mold'

    def gantt_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('idmoule', '=', obj.id) ])
            ids=[]
            for doc in docs:
                ids.append(doc.id)
            view_mode = 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph'
            return self.env['is.doc.moule'].list_doc(obj,ids,view_mode=view_mode)



class is_dossierf(models.Model):
    _inherit = 'is.dossierf'

    def gantt_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('dossierf_id', '=', obj.id) ])
            ids=[]
            initial_date=str(datetime.today())
            for doc in docs:
                if str(doc.dateend)<initial_date:
                    initial_date=str(doc.dateend)
                ids.append(doc.id)
            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossierf_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                'default_type_document': 'Dossier F',
                'default_dossierf_id'  : obj.id,
                'default_etat'         :'AF',
                'default_dateend'      : datetime.today(),
                'default_idresp'       : self._uid,
                'initial_date'         : initial_date,
            }
            return {
                'name': obj.name,
                'view_mode': 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph',
                "views"    : [
                    (gantt_id, "dhtmlxgantt_project"),
                    (tree_id, "tree"),
                    (False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
                'res_model': 'is.doc.moule',
                'domain': [
                    ('id','in',ids),
                ],
                'type': 'ir.actions.act_window',
                "context": ctx,
                'limit': 1000,
            }
        


class is_mold_project(models.Model):
    _inherit = 'is.mold.project'

    def gantt_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('idproject', '=', obj.id) ])
            ids=[]
            initial_date=str(datetime.today())
            for doc in docs:
                if str(doc.dateend)<initial_date:
                    initial_date=str(doc.dateend)
                ids.append(doc.id)
            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                #'default_type_document': 'Moule',
                #'default_dossierf_id'  : obj.id,
                'default_etat'         :'AF',
                'default_dateend'      : datetime.today(),
                'default_idresp'       : self._uid,
                'initial_date'         : initial_date,
            }
            return {
                'name': obj.name,
                'view_mode': 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph',
                "views"    : [
                    (gantt_id, "dhtmlxgantt_project"),
                    (tree_id, "tree"),
                    (False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
                'res_model': 'is.doc.moule',
                'domain': [
                    ('id','in',ids),
                ],
                'type': 'ir.actions.act_window',
                "context": ctx,
                'limit': 1000,
            }
        