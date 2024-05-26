# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import format_date, formatLang, frozendict
from datetime import datetime, timedelta
from random import *

from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J

class IsDocMoule(models.Model):
    _name        = "is.doc.moule"
    _inherit=['mail.thread']
    _description = "Document moule"
    _rec_name    = "param_project_id"
    _order = 'sequence,section_id,param_project_id'


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
    client_id        = fields.Many2one(related="idproject.client_id")
    idcp             = fields.Many2one(related="idmoule.chef_projet_id", string="CP")
    idresp           = fields.Many2one("res.users", string="Responsable")
    j_prevue         = fields.Selection(GESTION_J, string="J Prévue")
    actuelle         = fields.Selection(GESTION_J, string="J Actuelle")
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
    dynacase_id      = fields.Integer(string="Id Dynacase",index=True)
    duree               = fields.Integer(string="Durée (J)"      , help="Durée en jours ouvrés"         , default=1)
    duree_gantt         = fields.Integer(string="Durée Gantt (J)", help="Durée calendaire pour le Gantt", default=1, readonly=True)
    duree_attente_avant = fields.Integer("Durée attente avant (J)", help="Utilisée dans le Gantt")
    date_debut_gantt    = fields.Date(string="Date début Gantt", default=fields.Date.context_today)
    date_fin_gantt      = fields.Date(string="Date fin Gantt", readonly=True)
    dependance_id       = fields.Many2one("is.doc.moule", string="Dépendance",index=True)
    section_id          = fields.Many2one("is.section.gantt", string="Section Gantt",index=True)


    @api.onchange('date_debut_gantt','duree')
    def set_fin_gantt(self):
        for obj in self:
            if obj.date_debut_gantt and obj.duree:
                duree_gantt = obj.duree
                new_date = date_debut = date_fin = obj.date_debut_gantt
                while True:
                    if not(new_date.weekday() in [5,6]):
                        duree_gantt=duree_gantt-1
                    if duree_gantt<=0:
                        date_fin=new_date  + timedelta(days=1)
                        break
                    new_date = new_date + timedelta(days=1)
                duree_gantt = (date_fin - date_debut).days
                date_fin_gantt = obj.date_debut_gantt + timedelta(days=duree_gantt)
                obj.duree_gantt = duree_gantt
                obj.date_fin_gantt = date_fin_gantt


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
            res= {
                'name': 'Doc',
                'view_mode': 'form',
                'res_model': 'is.doc.moule',
                'res_id': obj.id,
                'type': 'ir.actions.act_window',
            }
            return res


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
                if doc.dateend and str(doc.dateend)<initial_date:
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


    def doc_client_action(self):
        for obj in self:
            return obj.client_id.gantt_action()


    @api.model
    def get_dhtmlx(self, domain=[]):
        lines=self.env['is.doc.moule'].search(domain, limit=10000) #, order="dateend"


        #** Ajout des markers (J des moules) **********************************
        res=[]
        markers=[]
        moules=[]
        dates_j={}
        for line in lines:
            moule=line.idmoule
            if moule not in moules:
                moules.append(moule)
        js=('J0','J1','J2','J3','J4','J5')
        for moule in moules:
            rpjs=self.env['is.revue.projet.jalon'].search([ ('rpj_mouleid', '=', moule.id)],limit=1,order="id desc")
            for rpj in rpjs:
                for j in js:
                    date_j = getattr(rpj, "rpj_date_valide_%s"%j.lower()) or getattr(rpj, "rpj_date_%s"%j.lower())
                    if date_j:
                        dates_j[j] = date_j
                        id = "%s-%s"%(moule.name,j)
                        start_date = str(date_j)+' 00:00:00"'
                        vals={
                            "id"        : id,
                            "start_date": start_date,
                            "css"       : "today",
                            "text"      : "%s : %s"%(moule.name,j),
                            "j"         : j,
                        }
                        markers.append(vals)
        #**********************************************************************


        #** Ajout des projets *************************************************
        projets=[]
        for line in lines:
            if line.idproject not in projets:
                projets.append(line.idproject)
        for projet in projets:
            text="%s (%s)"%(projet.name,projet.client_id.name)
            vals={
                "id": '%s-%s'%(projet._name,projet.id),
                "model": projet._name,
                "res_id": projet.id,
                "text": text,
                "start_date": False,
                "duration": False,
                "parent": 0,
                "progress": 0,
                "open": True,
                "priority": 2,
            }
            res.append(vals)
        #**********************************************************************

        #** Ajout des jours de fermeture des projets **************************
        jour_fermeture_ids=[]
        for projet in projets:
            for line in projet.fermeture_id.jour_ids:
                if line.date_fin:
                    if line.date_fin>=line.date_debut:
                        ladate=line.date_debut
                        while True:
                            if ladate>line.date_fin:
                                break                             
                            if ladate not in jour_fermeture_ids:
                                jour_fermeture_ids.append(str(ladate))
                            ladate+=timedelta(days=1)
                else:
                    if line.date_debut not in jour_fermeture_ids:
                        jour_fermeture_ids.append(str(line.date_debut))
        #**********************************************************************

        # #** Ajout des moules, dossierf ou dossier modif **********************
        dossiers=[]
        for line in lines:
            doc=False
            doc=(line.idmoule or line.dossierf_id or line.dossier_modif_variante_id)
            if doc not in dossiers:
                dossiers.append(doc)
        for dossier in dossiers:
            if hasattr(dossier, 'name'):
                name=dossier.name
                project=dossier.project.name
            else:
                name=dossier.demao_num
                project='?'
            text="%s (%s)"%(name,project)
            #infobulle_list=[]
            #infobulle_list.append("<b>Moule</b>: %s"%(name))
            vals={
                "id": "%s-%s"%(dossier._name,dossier.id),
                "model": dossier._name,
                "res_id": dossier.id,
                "text": text,
                "start_date": False,
                "duration": False,
                "parent": 'is.mold.project-%s'%dossier.project.id,
                "progress": 0,
                "open": True,
                "priority": 2,
                #"infobulle": "<br>\n".join(infobulle_list),
            }
            res.append(vals)
        # #**********************************************************************


        # #** Ajout des sections **********************************************
        my_dict={}
        for line in lines:
            dossier = (line.idmoule or line.dossierf_id or line.dossier_modif_variante_id)
            parent="%s-%s"%(dossier._name,dossier.id)
            section_id = line.section_id.id + 30000000
            id=dossier.id+20000000 + section_id
            key = "%s|%s|%s"%(id,parent,line.section_id.name)
            my_dict[id]=key
        for id in my_dict:
            tab=my_dict[id].split("|")
            parent=tab[1] 
            text="%s"%(tab[2])
            vals={
                "id": id,
                "text": text,
                "start_date": False,
                "duration": False,
                "parent": parent,
                "progress": 0,
                "open": True,
                "priority": 2,
            }
            res.append(vals)
        # #**********************************************************************


        #** Ajout des documents des moules **************************************
        for line in lines:
            if line.dateend and line.idresp:
                priority = round(2*random()) # Nombre aléatoire entre 0 et 2
                famille=line.param_project_id.ppr_famille
                name=famille
                if famille=='Autre':
                    name="%s (Autre)"%line.demande
                else:
                    name=famille
                if line.param_project_id.ppr_revue_lancement:
                    name="%s [%s]"%(name,line.param_project_id.ppr_revue_lancement)
                duration = line.duree_gantt or 1
                parent = (line.idmoule.id or line.dossierf_id.id or line.dossier_modif_variante_id.id)+20000000 + line.section_id.id + 30000000
                
                #** Bordure gauche de la tâche (Fait, A Faire ou en retard) ***
                etat_class='etat_a_faire'
                if line.etat=='F':
                    etat_class='etat_fait'
                if line.j_prevue and line.date_fin_gantt:
                    date_j = dates_j.get(line.j_prevue)
                    if dates_j:
                        if line.date_fin_gantt>date_j:
                            etat_class = "retard_j"
                #**************************************************************

                color_class = '%s is_param_projet_%s'%(etat_class,line.param_project_id.id)

                end_date = str(line.date_fin_gantt or line.dateend)+' 00:00:00"'


                j_prevue = dict(GESTION_J).get(line.j_prevue,"?")

                vals={
                    "id"         : "%s-%s"%(line._name,line.id),
                    "model"      : line._name,
                    "res_id"     : line.id,
                    "text"       : name,
                    "end_date"   : end_date,
                    "duration"   : duration,
                    "parent"     : parent,
                    "priority"   : priority,
                    "color_class": color_class,
                    "section"    : line.section_id.name,
                    "responsable": line.idresp.name,
                    "j_prevue"   : j_prevue,
                }
                res.append(vals)
        #**********************************************************************

        #** Ajout des dependances *********************************************
        links=[]
        for line in lines:
            if line.dependance_id:
                id="%s-%s"%(line.id,line.dependance_id.id)
                source = "%s-%s"%(line._name,line.dependance_id.id),
                target = "%s-%s"%(line._name,line.id),
                vals={
                    "id":id,
                    "source": source,
                    "target": target,
                    "type":0,
                }
                links.append(vals)
        #**********************************************************************

        return {
            "items"             : res, 
            "links"             : links, 
            "markers"           : markers, 
            "jour_fermeture_ids": jour_fermeture_ids
        }
    

    def write_task(self,start_date=False,duration=False,lier=False):
        start_date = start_date[0:10]
        try:
            date_debut_gantt = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=1)
        except ValueError:
            date_debut_gantt = False
        if date_debut_gantt:
            for obj in self:
                mem_date_fin = obj.date_fin_gantt
                if duration>0:
                    delta = duration - obj.duree_gantt 
                    duree = obj.duree + delta
                    if duree<1:
                        duree=1
                    obj.date_debut_gantt = date_debut_gantt
                    obj.set_fin_gantt()
                    obj.duree = duree
                    obj.set_fin_gantt()
                    delta = (obj.date_fin_gantt - mem_date_fin).days
                    if lier and delta:
                        obj.move_task_lier(delta)
        msg="%s : %s : %s => %s : %s"%(self.id,start_date,duration,obj.date_debut_gantt,obj.date_fin_gantt )
        return msg


    def move_task_lier(self,delta):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('dependance_id', '=', obj.id) ])
            for doc in docs:
                date_debut_gantt = doc.date_debut_gantt +  timedelta(days=delta)
                mem_date_fin = doc.date_fin_gantt
                doc.date_debut_gantt = date_debut_gantt
                doc.set_fin_gantt()
                delta = (doc.date_fin_gantt - mem_date_fin).days
                doc.move_task_lier(delta)


    def link_add(self,source=False,target=False):
        src=source.split("-")
        dst=target.split("-")
        doc_src = self.env[src[0]].browse(int(src[1]))
        doc_dst = self.env[dst[0]].browse(int(dst[1]))
        doc_dst.dependance_id = doc_src.id
        msg="link_add : %s : %s"%(doc_src,doc_dst)
        return msg

  
    def link_delete(self,source=False,target=False):
        msg="link_delete : %s : %s"%(source,target)
        src=source[0].split("-")
        dst=target[0].split("-")
        doc_src = self.env[src[0]].browse(int(src[1]))
        doc_dst = self.env[dst[0]].browse(int(dst[1]))
        doc_dst.dependance_id = False
        return msg


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
        

class res_partner(models.Model):
    _inherit = 'res.partner'

    def gantt_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('client_id', '=', obj.id) ])
            ids=[]
            initial_date=str(datetime.today())
            for doc in docs:
                if str(doc.dateend)<initial_date:
                    initial_date=str(doc.dateend)
                ids.append(doc.id)
            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
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
        