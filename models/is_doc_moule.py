# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import format_date, formatLang, frozendict
from datetime import datetime, timedelta, date
from random import *
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J, TYPE_DOCUMENT


class IsDocMoule(models.Model):
    _name        = "is.doc.moule"
    _inherit=['mail.thread']
    _description = "Document moule"
    #_rec_name    = "param_project_id"
    _order = 'section_id,sequence,section_id,param_project_id'


    def compute_project_prev(self):
        "for xml-rpc"
        self._compute_project_prev()
        self._compute_idproject_moule_dossierf()
        self._compute_site_id()
        self._compute_demao_nature()
        self._compute_solde()
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


    @api.depends('idmoule', 'dossierf_id', 'dossier_modif_variante_id.demao_idmoule', 'dossier_modif_variante_id.dossierf_id', 'dossier_modif_variante_id.demao_idclient')
    def _compute_idproject_moule_dossierf(self):
        for obj in self:
            idproject      = obj.idmoule.project.id or obj.dossierf_id.project.id
            moule_dossierf = obj.idmoule.name or obj.dossierf_id.name or obj.dossier_modif_variante_id.demao_idmoule.name or obj.dossier_modif_variante_id.dossierf_id.name
            client_id      = obj.idmoule.project.client_id.id or obj.dossierf_id.project.client_id.id or obj.dossier_modif_variante_id.demao_idclient.id
            obj.idproject      = idproject
            obj.moule_dossierf = moule_dossierf
            obj.client_id      = client_id


    type_document = fields.Selection(TYPE_DOCUMENT,string="Type de document", default="Moule", required=True, tracking=True)
    sequence = fields.Integer(string="Ordre", tracking=True)
    project_prev     = fields.Html(compute='_compute_project_prev', store=True)
    project_prev2    = fields.Html()
    param_project_id = fields.Many2one("is.param.project", string="Famille de document", tracking=True)
    ppr_type_demande = fields.Selection(related="param_project_id.ppr_type_demande")
    ppr_icon         = fields.Image(related="param_project_id.ppr_icon", string="Icône", store=True)
    ppr_color        = fields.Char(related="param_project_id.ppr_color", string="Color", store=True)
    idmoule          = fields.Many2one("is.mold"                  , string="Moule", tracking=True)
    dossierf_id      = fields.Many2one("is.dossierf"              , string="Dossier F", tracking=True)
    dossier_modif_variante_id = fields.Many2one("is.dossier.modif.variante", string="Dossier Modif / Variante", tracking=True)
    dossier_article_id        = fields.Many2one("is.dossier.article"       , string="Dossier article", tracking=True)
    dossier_appel_offre_id    = fields.Many2one("is.dossier.appel.offre"   , string="Dossier appel d'offre", tracking=True)
    moule_dossierf   = fields.Char("Moule / Dossier F"                   , compute='_compute_idproject_moule_dossierf',store=True, readonly=True)
    idproject        = fields.Many2one("is.mold.project", string="Projet", compute='_compute_idproject_moule_dossierf',store=True, readonly=True)
    client_id        = fields.Many2one("res.partner", string="Client"    , compute='_compute_idproject_moule_dossierf',store=True, readonly=True)
    idcp             = fields.Many2one(related="idmoule.chef_projet_id", string="CP", tracking=True)
    idresp           = fields.Many2one("res.users", string="Responsable", tracking=True)
    j_prevue         = fields.Selection(GESTION_J, string="J Prévue", tracking=True)
    actuelle         = fields.Selection(GESTION_J, string="J Actuelle", tracking=True)
    demande          = fields.Char(string="Demande", tracking=True)
    action           = fields.Selection([
        ("I", "Initialisation"),
        ("R", "Révision"),
        ("V", "Validation"),
    ], string="Action", tracking=True)
    bloquant         = fields.Boolean(string="Point Bloquant", tracking=True)
    etat             = fields.Selection([
        ("AF", "A Faire"),
        ("F", "Fait"),
        ("D", "Dérogé"),
    ], string="État", tracking=True)
    fin_derogation   = fields.Date(string="Date de fin de dérogation")
    coefficient      = fields.Integer(string="Coefficient")
    note             = fields.Integer(string="Note", tracking=True)
    indicateur       = fields.Html(string="Indicateur")
    datecreate       = fields.Date(string="Date de création", default=fields.Date.context_today)
    dateend          = fields.Date(string="Date de fin", tracking=True)
    array_ids        = fields.One2many("is.doc.moule.array", "is_doc_id", string="Pièce-jointe de réponse à la demande")
    dynacase_id      = fields.Integer(string="Id Dynacase",index=True,copy=False)
    duree               = fields.Integer(string="Durée (J)"      , help="Durée en jours ouvrés"         , default=1, tracking=True)
    duree_gantt         = fields.Integer(string="Durée Gantt (J)", help="Durée calendaire pour le Gantt", default=1, tracking=True, readonly=True)
    duree_attente_avant = fields.Integer("Durée attente avant (J)", help="Utilisée dans le Gantt")
    date_debut_gantt    = fields.Date(string="Date début Gantt", default=lambda self: self._date_debut_gantt(), tracking=True)
    date_fin_gantt      = fields.Date(string="Date fin Gantt", readonly=True, tracking=True)
    section_id          = fields.Many2one("is.section.gantt", string="Section Gantt",index=True, tracking=True)
    gantt_pdf           = fields.Boolean("Gantt PDF", default=True, help="Afficher dans Gantt PDF")
    dependance_id       = fields.Many2one("is.doc.moule", string="Dépendance",index=True, tracking=True)
    origine_copie_id    = fields.Many2one("is.doc.moule", string="Origine de la copie",index=True)
    active              = fields.Boolean('Actif', default=True, tracking=True)
    site_id             = fields.Many2one('is.database', "Site", compute='_compute_site_id', readonly=True, store=True)
    demao_nature        = fields.Char(string="Nature", compute='_compute_demao_nature'     , readonly=True, store=True)
    solde               = fields.Boolean(string="Soldé", compute='_compute_solde'          , readonly=True, store=True)
    rsp_date            = fields.Date(string="Date réponse")
    rsp_texte           = fields.Char(string="Réponse à la demande")


    @api.depends('dossier_modif_variante_id.solde')
    def _compute_solde(self):
        for obj in self:
            solde = False
            if obj.dossier_modif_variante_id.solde:
                solde = obj.dossier_modif_variante_id.solde
            obj.solde = solde


    @api.depends('dossier_modif_variante_id.demao_nature')
    def _compute_demao_nature(self):
        for obj in self:
            demao_nature = False
            if obj.dossier_modif_variante_id.demao_nature:
                demao_nature = obj.dossier_modif_variante_id.demao_nature
            obj.demao_nature = demao_nature


    @api.depends('dossier_modif_variante_id.site_id', 'dossierf_id.is_database_id', 'idmoule.is_database_id')
    def _compute_site_id(self):
        for obj in self:
            site_id = False
            if obj.dossier_modif_variante_id.site_id:
                site_id = obj.dossier_modif_variante_id.site_id.id
            if obj.dossierf_id.is_database_id:
                site_id = obj.dossierf_id.is_database_id.id
            if obj.idmoule.is_database_id:
                site_id = obj.idmoule.is_database_id.id
            obj.site_id = site_id


    def name_get(self):
        result = []
        for obj in self:
            name="[%s]%s"%(obj.moule_dossierf,obj.param_project_id.ppr_famille)
            result.append((obj.id, name))
        return result


    def _date_debut_gantt(self):
        now  = date.today()              # Ce jour
        d    = now
        while True:
            d = d - timedelta(days=1)   # Jour précédent tant que ce n'est pas sur un weekend
            if not(d.weekday() in [5,6]):
                break
        return d


    @api.onchange('param_project_id')
    def onchange_param_project_id(self):
        for obj in self:
            obj.gantt_pdf = obj.param_project_id.gantt_pdf


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


    def get_form_view_id(self):
        for obj in self:
            form_id = False
            if obj.type_document=='Moule':
                form_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_idmoule_form').id
            if obj.type_document=='Dossier F':
                form_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossierf_id_form').id
            if obj.type_document=='Article':
                form_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossier_article_id_form').id
            if obj.type_document=='Dossier Modif Variante':
                form_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossier_modif_variante_id_form').id
            if obj.type_document=='dossier_appel_offre':
                form_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossier_appel_offre_id_form').id
            return form_id



    def acceder_doc_action(self):
        for obj in self:
            form_id = obj.get_form_view_id()
            res= {
                'name': 'Doc',
                'view_mode': 'form',
                "views"    : [
                    (form_id, "form")
                ],
                'res_model': 'is.doc.moule',
                'res_id': obj.id,
                'type': 'ir.actions.act_window',
            }
            return res


    #def list_doc(self,obj,ids, view_mode=False,initial_date=False):
    def list_doc(self,obj,domain=False, view_mode=False):
        if not view_mode or not domain:
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
                #'initial_date'   : initial_date,
            }
        return {
            'name': obj.name,
            'view_mode': view_mode,
            "views"    : [
                (gantt_id, "dhtmlxgantt_project"),
                (tree_id, "tree"),
                (False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
            'res_model': 'is.doc.moule',
            'domain': domain,
            'type': 'ir.actions.act_window',
            "context": ctx,
            'limit': 1000,
        }
           

    # def doc_moule_action(self):
    #     for obj in self:
    #         docs=self.env['is.doc.moule'].search([ ('idmoule', '=', obj.idmoule.id) ])
    #         ids=[]
    #         initial_date=str(datetime.today())
    #         for doc in docs:
    #             if doc.dateend and str(doc.dateend)<initial_date:
    #                 initial_date=str(doc.dateend)
    #             ids.append(doc.id)
    #         view_mode = 'tree,form,dhtmlxgantt_project,kanban,calendar,pivot,graph'
    #         return obj.list_doc(obj.idmoule,ids,view_mode=view_mode,initial_date=initial_date)


    def doc_moule_action(self):
        for obj in self:
            domain=[('idmoule', '=', obj.idmoule.id)]
            view_mode = 'tree,form,dhtmlxgantt_project,kanban,calendar,pivot,graph'
            return obj.list_doc(obj.idmoule,domain,view_mode=view_mode)






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
        scroll_x = self.env['is.mem.var'].get(self._uid, 'scroll_x')
        scroll_y = self.env['is.mem.var'].get(self._uid, 'scroll_y')

        lines=self.env['is.doc.moule'].search(domain, limit=10000) #, order="dateend"


       #** Ajout des markers (J des moules) depuis is.revue.lancement *********
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
            #** Recherche is.revue.contrat ************************************
            rcs=self.env['is.revue.de.contrat'].search([ ('rc_num_outillageid', '=', moule.id)],limit=1,order="id desc")
            for rc in rcs:
                #** Recherche is.revue.lancement ******************************
                rls=self.env['is.revue.lancement'].search([ ('rl_num_rcid', '=', rc.id)],limit=1,order="id desc")
                for rl in rls:
                    for j in js:
                        date_j = getattr(rl, "rl_date_%s"%j.lower())
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
                if line.idproject:
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


        # #** Ajout des moules, dossierf ou dossier modif **********************
        dossiers=[]
        for line in lines:
            doc=False
            doc=(line.idmoule or line.dossierf_id or line.dossier_modif_variante_id or line.dossier_appel_offre_id)
            if doc not in dossiers:
                dossiers.append(doc)


        #** Ajout des jours de fermeture des projets **************************
        def get_jour_fermeture_ids(fermeture_id):
            jour_fermeture_ids=[]
            for line in fermeture_id.jour_ids:
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
            return jour_fermeture_ids
        jour_fermeture_ids=[]
        for projet in projets:
            jour_fermeture_ids=get_jour_fermeture_ids(projet.fermeture_id)
        for dossier in dossiers:
            if hasattr(dossier, 'demao_num'):
                jour_fermeture_ids=get_jour_fermeture_ids(dossier.fermeture_id)
        #**********************************************************************

        for dossier in dossiers:
            name=""
            project=""
            if hasattr(dossier, 'name'):
                name=dossier.name
                project=dossier.project.name
            if hasattr(dossier, 'demao_num'):
                name=dossier.demao_num
            if hasattr(dossier, 'dao_num'):
                name=dossier.dao_num
            text="%s (%s)"%(name,project)
            parent=False
            if hasattr(dossier, 'project'):
                parent = 'is.mold.project-%s'%dossier.project.id
            vals={
                "id": "%s-%s"%(dossier._name,dossier.id),
                "model": dossier._name,
                "res_id": dossier.id,
                "text": text,
                "start_date": False,
                "duration": False,
                "parent": parent,
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
            dossier = (line.idmoule or line.dossierf_id or line.dossier_modif_variante_id or line.dossier_appel_offre_id)
            parent="%s-%s"%(dossier._name,dossier.id)
            section_id = line.section_id.id + 30000000
            id=dossier.id+20000000 + section_id
            key = "%s|%s|%s|%s"%(id,parent,line.section_id.name,(line.section_id.id or 0))
            my_dict[id]=key
        for id in my_dict:
            tab=my_dict[id].split("|")
            parent=tab[1] 
            text="%s"%(tab[2])
            res_id=tab[3] 
            vals={
                "id": id,
                "model": 'is.section.gantt',
                "res_id": res_id,
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
            if (line.dateend or line.date_fin_gantt) and line.idresp:
                priority = round(2*random()) # Nombre aléatoire entre 0 et 2
                famille=line.param_project_id.ppr_famille
                name=famille
                #if famille=='Autre':
                #    name="%s (Autre)"%(line.demande or '')
                #else:
                #    name=famille

                if line.demande:
                   name="%s (%s)"%(line.demande,famille)
                else:
                   name=famille



                if line.param_project_id.ppr_revue_lancement:
                    name="%s [%s]"%(name,line.param_project_id.ppr_revue_lancement)
                duration = line.duree_gantt or 1
                parent = (line.idmoule.id or line.dossierf_id.id or line.dossier_modif_variante_id.id or line.dossier_appel_offre_id.id)+20000000 + line.section_id.id + 30000000
                
                #** Bordure gauche de la tâche (Fait, A Faire ou en retard) ***
                etat_class='etat_a_faire'
                if line.etat=='F':
                    etat_class='etat_fait'
                if line.j_prevue and line.date_fin_gantt:
                    date_j = dates_j.get(line.j_prevue)
                    if date_j and line.date_fin_gantt:
                        if line.date_fin_gantt>date_j:
                            etat_class = "retard_j"
                #**************************************************************

                #color_class = '%s is_param_projet_%s'%(etat_class,line.param_project_id.id)
                color_class = '%s is_section_gantt_%s'%(etat_class,line.section_id.id)




                end_date = str(line.date_fin_gantt or line.dateend)+' 00:00:00'


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
                    "etat_class" : etat_class,
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
            "jour_fermeture_ids": jour_fermeture_ids,
            "scroll_x"          : scroll_x,
            "scroll_y"          : scroll_y,
        }
    

    def write_task(self,start_date=False,duration=False,lier=False,mode=False):
        start_date = start_date[0:10]
        try:
            date_debut_gantt = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=1)
        except ValueError:
            date_debut_gantt = False
        if date_debut_gantt:
            for obj in self:
                mem_date_fin = obj.date_fin_gantt
                if duration>0:
                    if mode and mode=='resize':
                        delta = duration - obj.duree_gantt 
                        date_fin_avant = date_debut_gantt + timedelta(days=obj.duree_gantt)
                        date_fin_apres = date_fin_avant + timedelta(days=delta)
                        # Nombre de jours ouverts entre ces dates *************
                        new_date = date_debut_gantt
                        jours_ouvres = 0
                        while True:
                            if new_date==date_fin_apres:
                                break
                            if not(new_date.weekday() in [5,6]):
                                jours_ouvres+=1
                            new_date += timedelta(days=1)
                        #******************************************************
                        obj.duree          = jours_ouvres
                        obj.duree_gantt    = duration
                        obj.date_fin_gantt = date_fin_apres
                    else:
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



    def set_scroll(self,scroll_x=False,scroll_y=False):
        self.env['is.mem.var'].set(self._uid, 'scroll_x', scroll_x)
        self.env['is.mem.var'].set(self._uid, 'scroll_y', scroll_y)
        return True


    def get_doc_color(self):
        "Retourne la couleur de l'indicateur en fonction de différent paramètres"
        for obj in self:
            color = 'Lavender'
            if not obj.dateend:
                color = 'orange'
            if obj.action=='':
                color = 'Lavender'
            if obj.etat=='AF':
                color='CornflowerBlue'
            if obj.etat=='D':
                color='Orange'
            if obj.dateend:
                now = date.today()
                if now>obj.dateend:
                    color='Red'
            if obj.etat=='F':
                color='SpringGreen'
            # if ($name_fam=="DFAB")  $color = "Lavender"; // Traitement particulier pour les dossiers de fab
            return color


    def get_doc_note(self):
        "Retourne la note pour l'indicateur en fonction de différent paramètres"
        note=5
        return note

        # $notes=array("I"=>1,"R"=>3,"V"=>5);
        # for($i=0;$i<count($j);$i++) {
        #     $note=" ";
        #     if ($irv[$i]<>"") $note=$notes[$irv[$i]];
        #     if ($bloquant[$i]=="Oui") $note=$note+10;
        #     if ($bloquant[$i]!="Oui") $bloquant[$i]=" "; //Pour éffacerr la valeur
        #     $r[$j[$i]]=array("IRV"=>$irv[$i],"Bloquant"=>$bloquant[$i],"Note"=>$note);        
        # }
        # return $r;



    def get_doc_reponse(self):
        "Retourne la réponse (PJ, date et commentaire) du document"
        for obj in self:
            rsp_pj=False
            rsp_date=False
            if obj.rsp_date:
                rsp_date = obj.rsp_date.strftime('%d/%m/%y')
            rsp_texte = obj.rsp_texte
            for line in obj.array_ids:
                if line.annex:
                    for pj in line.annex:
                        rsp_pj=pj.name
                break
            reponse=[rsp_pj,rsp_date,rsp_texte]
            return reponse


    # annex       = fields.Many2many("ir.attachment", "attach_annex_rel"    , "annex_id"    , "attachment_id", string="Fichiers")
    # rsp_date    = fields.Date(string="Date")
    # rsp_texte   = fields.Char(string="Réponse à la demande")


   # //** Affichage de la réponse **************************
    # $rsp_texte = $this->getValue("plasfil_rsp_texte");
    # if($rsp_texte!="") $trombone='<a href="#" title="'.$rsp_texte.'">'.substr($rsp_texte,0,5).'</a>';

    # $rsp_date = $this->getValue("plasfil_rsp_date");
    # if($rsp_date!="") $trombone='<a href="#" title="'.$rsp_date.'">'.substr($rsp_date,0,5).'</a>';

    # $piecejointe=$this->getTValue("PLASFIL_ANNEX");
    # if (count($piecejointe)>0) {
    #   $trombone="<img border=0 src=\"/www/Images/tronbonne.gif\">";
    # }
    # //*****************************************************



		
# PLASFIL_RSP_DATE	PLASFIL_FR_ANNEX	Date
# PLASFIL_RSP_TEXTE	PLASFIL_FR_ANNEX	Réponse à la demande
# PLASFIL_RSP_HTML	PLASFIL_FR_ANNEX	Réponse à la demande




class IsDocMouleArray(models.Model):
    _name        = "is.doc.moule.array"
    _description = "Document moule array"

    annex_pdf   = fields.Many2many("ir.attachment", "attach_annex_pdf_rel", "annex_pdf_id", "attachment_id", string="Fichiers PDF")
    annex       = fields.Many2many("ir.attachment", "attach_annex_rel"    , "annex_id"    , "attachment_id", string="Fichiers")
    demandmodif = fields.Char(string="Demande de modification")
    maj_amdec   = fields.Boolean(string="Mise à jour de l’AMDEC")
    comment     = fields.Text(string="Commentaire")
    is_doc_id   = fields.Many2one("is.doc.moule")
    lig         = fields.Integer(string="Lig",index=True,copy=False,readonly=True, help="Permet de faire le lien avec la ligne du tableau dans Dynacase")




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
        