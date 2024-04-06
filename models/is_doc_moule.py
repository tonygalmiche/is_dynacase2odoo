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

    sequence = fields.Integer(string="Ordre")
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


    def list_doc(self,obj,ids, view_mode=False):
        if not view_mode:
            return False
        

        print(view_mode)

        tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_edit_tree_view').id
        gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
        ctx={}
        if obj._name=='is.mold':
            ctx={
                'default_idmoule': obj.id,
                'default_etat'   :'AF',
                'default_dateend': datetime.today(),
                'default_idresp' : self._uid,
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
            for doc in docs:
                ids.append(doc.id)
            view_mode = 'tree,form,dhtmlxgantt_project,kanban,calendar,pivot,graph'
            return obj.list_doc(obj.idmoule,ids,view_mode=view_mode)






    def doc_projet_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('idproject', '=', obj.idproject.id) ])
            ids=[]
            for doc in docs:
                ids.append(doc.id)
            return obj.list_doc(obj.idproject,ids)


    # @api.model
    # def get_dhtmlx(self, domain=[]):
    #     print("## TEST get_dhtmlx : domain=",domain)
    #     lines=self.env['is.doc.moule'].search(domain,limit=100, order="dateend")
    #     print("get_dhtmlx=",lines)
    #     res=[]


    #     for line in lines:
    #         priority = round(2*random()) # Nombre aléatoire entre 0 et 2
    #         if line.dateend:
    #             text = line.param_project_id.ppr_famille
    #             vals={
    #                 "id": line.id+100000,
    #                 "text": text,
    #                 "start_date": str(line.dateend)+' 02:00:00"',
    #                 #"end_date": str(line.dateend)+' 22:00:00"',
    #                 "duration": 32, # TODO a calculer !!
    #                 "parent": 0,
    #                 "progress": 0,
    #                 "open": True,
    #                 #"assigned": project.user_id.name,
    #                 "priority": priority,
    #                 "infobulle": "test"
    #             }
    #             res.append(vals)


    @api.model
    def get_dhtmlx(self, domain=[]):
        print(domain)
        lines=self.env['is.doc.moule'].search(domain, order="dateend", limit=500)

        # #** Ajout des moules ************************************************
        res=[]
        moules=[]
        for line in lines:
            if line.idmoule not in moules:
                moules.append(line.idmoule)
        for moule in moules:
            text="%s (%s)"%(moule.name,moule.project.name)
            infobulle_list=[]
            infobulle_list.append("<b>Moule</b>: %s"%(moule.name))
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
                duration = 14
                infobulle_list=[]
                infobulle_list.append("<b>Document</b>           : %s"%name)
                vals={
                    "id": line.id,
                    "text": name,
                    "end_date": str(line.dateend)+' 02:00:00"',
                    "duration": duration,
                    "parent": line.idmoule.id+100000,
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








        # LOCAL = tz.gettz('Europe/Paris')
        # UTC   = tz.gettz('UTC')
        # res=[]
        # ids=[]
        # for line in lines:
        #     if line.production_id.id not in ids:
        #         ids.append(line.production_id.id)
        # filtre=[
        #     ('id','in', ids),
        #     ('state', 'not in', ['done', 'cancel']),
        #     ('is_ordre_travail_id', '!=', False),
        # ]
        # productions=self.env['mrp.production'].search(filtre, order="is_date_planifiee,name")
        # for production in productions:
        #     text="%s : %s"%(production.name,(production.is_client_order_ref or '?'))

        #     infobulle_list=[]
        #     infobulle_list.append("<b>Ordre de fabrication</b>: %s"%(production.name))
        #     infobulle_list.append("<b>Article</b>             : %s"%(production.product_id.name))
        #     infobulle_list.append("<b>Commande</b>            : %s"%(production.is_sale_order_id.name))
        #     infobulle_list.append("<b>Référence client</b>    : %s"%(production.is_client_order_ref))
        #     if production.is_date_prevue:
        #         infobulle_list.append("<b>Date client</b>         : %s"%(production.is_date_prevue.strftime('%d/%m/%y')))
        #     infobulle_list.append("<b>Date planifiée début</b>: %s"%(production.is_date_planifiee.strftime('%d/%m/%y')))
        #     infobulle_list.append("<b>Date planifiée fin</b>  : %s"%(production.is_date_planifiee_fin.strftime('%d/%m/%y')))

        #     #start_date_utc   = production.date_planned_start
        #     start_date_utc   = production.is_date_planifiee
        #     end_date_utc     = production.is_date_planifiee_fin

        #     start_date_local = start_date_utc.replace(tzinfo=UTC)
        #     end_date_local   = end_date_utc.replace(tzinfo=UTC)

        #     vals={
        #         "id": production.id+100000,
        #         "text": text,
        #         "start_date": start_date_local,
        #         "end_date": end_date_local,
        #         #"duration": 8, # TODO a calculer !!
        #         "parent": 0,
        #         "progress": 0,
        #         "open": True,
        #         #"assigned": project.user_id.name,
        #         "priority": 2,
        #         "infobulle": "<br>\n".join(infobulle_list)
        #     }
        #     res.append(vals)
        # # #**********************************************************************

        links=[]
        return {"items":res, "links": links}




    # @api.model
    # def get_gantt_documents(self,domain=[]):
    #     print("## get_gantt_documents",self,domain)
    #     my_dict={}


    #     docs=self.env['is.doc.moule'].search(domain,limit=10)
    #     for doc in docs:
    #         key="%s-%s"%(doc.dateend,doc.id)

    #         print(key)

    #         vals={
    #             "key"    : key,
    #             "name"   : doc.param_project_id.ppr_famille,
    #             "dateend": doc.dateend,
    #             "duree"  : doc.duree,

    #             "id"        : doc.id,
    #             "text"      : "xxx",
    #             "start_date": start_date,
    #             "duration"  : duration,
    #             "assigned"  : assigned,
    #             "priority"  : priority,
    #             #"parent"    : parent,
    #         }
    #         my_dict[key]=vals        
    #     sorted_dict = dict(sorted(my_dict.items()))

    #     print(sorted_dict)


    #     return {
    #         "dict"           : sorted_dict,
    #         # "mois"           : mois,
    #         # "semaines"       : semaines,
    #         # "nb_semaines"    : nb_semaines,
    #         # "decale_planning": decale_planning,
    #     }





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

    def doc_moule_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('idmoule', '=', obj.id) ])
            ids=[]
            for doc in docs:
                ids.append(doc.id)
            view_mode = 'tree,dhtmlxgantt_project,form,kanban,calendar,pivot,graph'
            return self.env['is.doc.moule'].list_doc(obj,ids,view_mode=view_mode)


    def gantt_moule_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('idmoule', '=', obj.id) ])
            ids=[]
            for doc in docs:
                ids.append(doc.id)
            view_mode = 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph'
            return self.env['is.doc.moule'].list_doc(obj,ids,view_mode=view_mode)


    # def gantt_moule_action(self):
    #     for obj in self:
    #         docs=self.env['is.doc.moule'].search([ ('idmoule', '=', obj.idmoule.id) ])
    #         ids=[]
    #         for doc in docs:
    #             ids.append(doc.id)
    #         view_mode = 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph'
    #         return obj.list_doc(obj.idmoule,ids,view_mode=view_mode)
