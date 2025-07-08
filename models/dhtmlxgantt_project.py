# -*- coding: utf-8 -*-
from odoo import models, fields, api, _                              # type: ignore
from odoo.tools import format_date, formatLang, frozendict           # type: ignore
from odoo.exceptions import AccessError, ValidationError, UserError  # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J, TYPE_DOCUMENT, MODELE_TO_TYPE, TYPE_TO_FIELD  # type: ignore
from datetime import datetime, timedelta, date
from random import *


class IsDocMoule(models.Model):
    _inherit        = "is.doc.moule"


    def get_jour_fermeture_ids(self,fermeture_id):
        jour_fermeture_ids={}
        #color='red'
        for line in fermeture_id.jour_ids:
            couleur = line.couleur
            if line.date_fin:
                if line.date_fin>=line.date_debut:
                    ladate=line.date_debut
                    while True:
                        if ladate>line.date_fin:
                            break                             
                        if ladate not in jour_fermeture_ids:
                            key = str(ladate)
                            jour_fermeture_ids[key] = (key,couleur)
                        ladate+=timedelta(days=1)
            else:
                if line.date_debut not in jour_fermeture_ids:
                    key = str(line.date_debut)
                    jour_fermeture_ids[key] = (key,couleur)
        return jour_fermeture_ids


    @api.model
    def get_dhtmlx(self, domain=[]):
        scroll_x = self.env['is.mem.var'].get(self._uid, 'scroll_x')
        scroll_y = self.env['is.mem.var'].get(self._uid, 'scroll_y')

        lines=self.env['is.doc.moule'].search(domain, limit=10000)

       #** Ajout des markers (J des moules) depuis is.revue.lancement *********
        res=[]
        markers=[]
        moules=[]
        dates_j={}
        for line in lines:
            moule=line.idmoule
            if moule not in moules and moule:
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

        jour_fermeture_ids=[]
        for projet in projets:
            jour_fermeture_ids=self.get_jour_fermeture_ids(projet.fermeture_id)
        for dossier in dossiers:
            if hasattr(dossier, 'fermeture_id'):
                jours = self.get_jour_fermeture_ids(dossier.fermeture_id)
                if len(jours)>0:
                    jour_fermeture_ids=jours
        #**********************************************************************


#PROJET is.mold.project(776,) ['2009-05-18', '2009-05-19', '2009-05-20', '2009-05-21', '2009-05-22', '2009-05-23', '2009-05-24', '2009-05-25', '2009-05-26', '2009-05-27', '2009-05-28', '2009-05-29', '2009-05-30', '2024-12-01', '2024-12-02', '2024-12-03', '2024-12-04', '2024-12-05', '2024-12-06', '2024-12-07', '2024-12-08', '2024-12-09', '2024-12-10', '2024-12-11', '2024-12-12', '2024-12-13', '2024-12-14', '2024-12-15', '2024-12-16', '2024-12-17', '2024-12-18', '2024-12-19', '2024-12-20', '2024-12-21', '2024-12-22', '2024-12-23', '2024-12-24', '2024-12-25', '2024-12-26', '2024-12-27', '2024-12-28', '2024-12-29', '2024-12-30', '2024-12-31', '2025-01-27', '2025-01-28', '2025-01-29', '2025-01-30', '2025-01-31', '2025-02-01', '2025-02-02', '2025-02-03', '2025-02-04', '2025-02-05', '2025-02-06', '2025-02-07']





        dossier_id=dossier_model=False
        for dossier in dossiers:
            dossier_id    = dossier.id
            dossier_model = dossier._name
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
            name_var = "open_close_task-%s"%id
            open_close_task = self.env['is.mem.var'].get(self._uid, name_var)
            open=True
            if open_close_task=='close':
                open=False
            vals={
                "id": id,
                "model": 'is.section.gantt',
                "res_id": res_id,
                "text": text,
                "start_date": False,
                "duration": False,
                "parent": parent,
                "progress": 0,
                "open": open,
                "priority": 2,
            }
            res.append(vals)
        # #**********************************************************************


        #** Ajout des documents des moules **************************************
        for line in lines:
            if line.date_fin_gantt and line.idresp:
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
                    name="%s"%name
                    #name="%s [%s]"%(name,line.param_project_id.ppr_revue_lancement)

                duration = line.duree_gantt or 1
                parent = (line.idmoule.id or line.dossierf_id.id or line.dossier_modif_variante_id.id or line.dossier_appel_offre_id.id)+20000000 + line.section_id.id + 30000000
                
                #** Bordure gauche de la tâche (Fait, A Faire ou en retard) ***
                # etat_class='etat_a_faire'
                # if line.etat=='F':
                #     etat_class='etat_fait'
                # else:
                #     if line.j_prevue and line.date_fin_gantt:
                #         date_j = dates_j.get(line.j_prevue)
                #         if date_j and line.date_fin_gantt:
                #             if line.date_fin_gantt>date_j:
                #                 etat_class = "retard_j"
                etat_class = "border_left_%s"%(line.color or '').lower()
                #**************************************************************

                color_class = '%s is_section_gantt_%s'%(etat_class,line.section_id.id)
                end_date = str(line.date_fin_gantt)+' 00:00:00'
                j_prevue = dict(GESTION_J).get(line.j_prevue,"?")

                #** Initiales du responsable **********************************
                responsable =  line.idresp.name or ''
                t=responsable.split(' ')
                initiales=t[0][0]
                if len(t)>1:
                    initiales+=t[1][0]
                #**************************************************************
                vals={
                    "id"          : "%s-%s"%(line._name,line.id),
                    "model"       : line._name,
                    "res_id"      : line.id,
                    "text"        : name,
                    "end_date"    : end_date,
                    "duration"    : duration,
                    "parent"      : parent,
                    "priority"    : priority,
                    "etat_class"  : etat_class,
                    "color_class" : color_class,
                    "section"     : line.section_id.name,
                    "j_prevue"    : j_prevue,
                    "responsable" : responsable,
                    "initiales"   : initiales,
                    "irv"         : line.action or '',
                    "attendus"    : line.attendus or '',
                    "border_color": line.color,
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
            "dossier_id"        : dossier_id, 
            "dossier_model"     : dossier_model, 
            "items"             : res, 
            "links"             : links, 
            "markers"           : markers, 
            "jour_fermeture_ids": jour_fermeture_ids,
            "scroll_x"          : scroll_x,
            "scroll_y"          : scroll_y,
        }
    

    def copy_task(self):
        for obj in self:
            copy = obj.copy()
            copy.section_id = obj.section_id.id
            copy.sequence   = obj.sequence


    def archive_task(self):
        for obj in self:
            obj.active=False


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
            domain = obj.get_domain_type_document()
            domain.append( ('dependance_id', '=', obj.id) )
            self.env.context = self.with_context(noonchange=False).env.context
            docs=self.env['is.doc.moule'].search(domain)
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


    def open_close_task(self,task_id=False,task_state=False):
        name="open_close_task-%s"%task_id
        self.env['is.mem.var'].set(self._uid, name, task_state)
        return True


    def get_doc_reponse(self):
        "Retourne la réponse (PJ, date et commentaire) du document"
        for obj in self:
            rsp_pj=False
            rsp_date=False
            if obj.rsp_date:
                rsp_date = obj.rsp_date.strftime('%d/%m/%y')
            rsp_texte = obj.rsp_texte
            for line in obj.array_ids:
                if line.comment:
                    rsp_pj=line.comment
                if line.annex:
                    for pj in line.annex:
                        rsp_pj=pj.name
                break
            reponse=[rsp_pj,rsp_date,rsp_texte]
            return reponse