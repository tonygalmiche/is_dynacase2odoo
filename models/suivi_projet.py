# -*- coding: utf-8 -*-
from odoo import models, fields, api, _                                    # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J # type: ignore
from odoo.exceptions import AccessError, ValidationError, UserError        # type: ignore
from datetime import datetime, timedelta, date
from pathlib import Path
from subprocess import PIPE, Popen
import copy
import base64
import unidecode  # type: ignore
import logging
_logger = logging.getLogger(__name__)


#TODO:
#- Faire fonctionner les dosssiers article et le modèle 07-Composant / Matière

#- Ne pas recherche l'objet doc pour chque ligne de la requete pour gagner 0.02s par docuement => Stocker les informations utilse direcement dans is_doc_moule avec des champs calculés
#- Afficher la bonne vue liste en cliqant sur l'icone des outils et faire fonctonner avec les dossier f
#- Pb syncro avec le champ 'Etat' des documents et les champs plasfil_rsp_date et plasfil_rsp_texte
#- Manque la famille 'Dossier de Fab'
#- Résoudre problème calcul note
#- Ajouter les icones en lignes et en colonne pour effectuer les différentes actions (zip,...)
#- Bouton pour actualiser une ligne sans tout recharger (idem Analyse CBN) 


class IsDocMoule(models.Model):
    _inherit = "is.doc.moule"


    def get_suivi_projet(
            self, 
            cp_id=False,
            client=False,
            projet=False,
            moule=False,
            type_moule=False,
            avec_photo=False,
            modele_id=False,
            ok=False
        ):
        cr = self._cr
        debut=datetime.now()
        _logger.info("Début (durée=%.2fs)"%(datetime.now()-debut).total_seconds())

        #** set/get var *****************************************************
        if ok:
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_cp_id'     , cp_id)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_client'    , client)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_projet'    , projet)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_moule'     , moule)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_type_moule', type_moule)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_modele_id' , modele_id)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_avec_photo', avec_photo)
        else:
            cp_id      = self.env['is.mem.var'].get(self._uid, 'suivi_projet_cp_id')
            client     = self.env['is.mem.var'].get(self._uid, 'suivi_projet_client')
            projet     = self.env['is.mem.var'].get(self._uid, 'suivi_projet_projet')
            moule      = self.env['is.mem.var'].get(self._uid, 'suivi_projet_moule')
            type_moule = self.env['is.mem.var'].get(self._uid, 'suivi_projet_type_moule')
            modele_id  = self.env['is.mem.var'].get(self._uid, 'suivi_projet_modele_id')
            avec_photo = self.env['is.mem.var'].get(self._uid, 'suivi_projet_avec_photo')
        _logger.info("set/get var (durée=%.2fs)"%(datetime.now()-debut).total_seconds())

        #** Valeur par défaut *************************************************
        if not type_moule:
            type_moule='Actif'
        if not avec_photo:
            avec_photo='Oui'
        _logger.info("set/get var (durée=%.2fs)"%(datetime.now()-debut).total_seconds())

        #** Liste de choix cp_options *****************************************
        cp_options=[]
        cp_options.append({
            "id"      : 0,
            "name"    : '',
            "selected": False,
        })
        group = self.env.ref('is_plastigray16.is_chef_projet_group')
        for user in group.users:
            selected=False
            if str(user.id)==cp_id:
                selected=True
            cp_options.append({
                "id"      : user.id,
                "name"    : user.name,
                "selected": selected,
            })

        #** Liste de choix modele_options *************************************
        modele_options=[]
        lines=self.env['is.modele.bilan'].search([],order='mb_titre')
        for line in lines:
            selected=False
            if str(line.id)==modele_id:
                selected=True
            modele_options.append({
                "id"      : line.id,
                "name"    : line.mb_titre,
                "selected": selected,
            })
        #**********************************************************************

        #** Liste de choix type_moule_options *********************************
        options = ["Actif","Tous"]
        type_moule_options=[]
        for o in options:
            selected=False
            if o==type_moule:
                selected=True
            type_moule_options.append({
                "id": o,
                "name": o,
                "selected": selected,
            })

        #** Liste de choix avec_photo_options *********************************
        options = ["Oui","Non"]
        avec_photo_options=[]
        for o in options:
            selected=False
            if o==avec_photo:
                selected=True
            avec_photo_options.append({
                "id": o,
                "name": o,
                "selected": selected,
            })
        _logger.info("Liste de choix (durée=%.2fs)"%(datetime.now()-debut).total_seconds())

        #** Recherche des familles du modele **********************************
        modele_ids=[]
        familles={}
        type_modele=False
        if modele_id:
            modeles=self.env['is.modele.bilan'].search([('id','=',modele_id)])
            for modele in modeles:
                type_modele=modele.mb_type
                ct=0
                for line in modele.line_ids:
                    ct+=1
                    id = line.param_project_id.id
                    if id:
                        modele_ids.append(str(id))
                        familles[ct]={
                            'ct'            : ct,
                            'id'            : id,
                            'name'          : line.param_project_id.ppr_famille,
                            'doc_id'        : False,
                            'etat'          : '',
                            'date_fin_gantt': '',
                            'note'          : '',
                            'style'         : '',
                            'dynacase_id'   : False,
                            'reponse'       : [False,False,False],
                        }
        _logger.info("Familles du modele (durée=%.2fs)"%(datetime.now()-debut).total_seconds())

        mydict={}


        #** Clause WHERE ******************************************************
        WHERE=""
        if cp_id and cp_id!='0':
            WHERE+=" and ru.id=%s "%cp_id
        if client:
            WHERE+=" and client.name ilike '%"+client+"%' "
        if projet:
            WHERE+=" and imp.name ilike '%"+projet+"%' "
        if moule:
            WHERE+=" and im.name ilike '"+moule+"%' "
        if type_moule and type_moule=='Actif':
            WHERE+=" and im.date_fin_be is null "
        #**********************************************************************




        if type_modele=='Article':
            #** Moules ********************************************************
            SQL="""
                select
                    idm.id               id,
                    ida.code_pg          moule,
                    CONCAT(ida.designation,'- ',im.name) designation,
                    ida.id                moule_id,
                    'is.dossier.article' res_model,
                    imp.name             projet,
                    imp.id               projet_id,
                    rp.name              cp,
                    imp.chef_projet_id   cp_id,
                    client.name          client,
                    imp.client_id        client_id,
                    ipp.ppr_famille      famille,
                    ipp.id               famille_id,
                    idm.etat             etat,
                    im.j_actuelle        j_actuelle,
                    im.j_avancement      j_avancement,
                    idm.date_fin_gantt   date_fin_gantt,
                    idm.coefficient      coefficient,
                    idm.note             note,
                    idm.etat             etat,
                    idm.dynacase_id      dynacase_id,
                    idm.rsp_pj           rsp_pj,
                    idm.rsp_date         rsp_date,
                    idm.rsp_texte        rsp_texte,
                    idm.color            color,
                    idm.type_document
                from is_mold_dossierf_article article join is_dossier_article ida on article.article_id=ida.id
                                                      join is_mold im on article.mold_id=im.id
                                                      join is_mold_project imp              on im.project=imp.id
                                                      join res_users ru                     on imp.chef_projet_id=ru.id
                                                      join res_partner rp                   on ru.partner_id=rp.id
                                                      join res_partner client               on imp.client_id=client.id
                                                      join is_doc_moule idm                 on idm.dossier_article_id=article.article_id
                                                      join is_param_project ipp             on idm.param_project_id=ipp.id
                where idm.active='t' and idm.suivi_projet='t' and idm.param_project_id in (%s) %s
            """%(','.join(modele_ids),WHERE)


            #** Dossier F *****************************************************
            SQL+="""
                UNION
                select
                    idm.id               id,
                    ida.code_pg          moule,
                    CONCAT(ida.designation,'- ',im.name) designation,
                    ida.id                moule_id,
                    'is.dossier.article' res_model,
                    imp.name             projet,
                    imp.id               projet_id,
                    rp.name              cp,
                    imp.chef_projet_id   cp_id,
                    client.name          client,
                    imp.client_id        client_id,
                    ipp.ppr_famille      famille,
                    ipp.id               famille_id,
                    idm.etat             etat,
                    im.j_actuelle        j_actuelle,
                    im.j_avancement      j_avancement,
                    idm.date_fin_gantt   date_fin_gantt,
                    idm.coefficient      coefficient,
                    idm.note             note,
                    idm.etat             etat,
                    idm.dynacase_id      dynacase_id,
                    idm.rsp_pj           rsp_pj,
                    idm.rsp_date         rsp_date,
                    idm.rsp_texte        rsp_texte,
                    idm.color            color,
                    idm.type_document
                from is_mold_dossierf_article article join is_dossier_article ida on article.article_id=ida.id
                                                      join is_dossierf im on article.dossierf_id=im.id
                                                      join is_mold_project imp              on im.project=imp.id
                                                      join res_users ru                     on imp.chef_projet_id=ru.id
                                                      join res_partner rp                   on ru.partner_id=rp.id
                                                      join res_partner client               on imp.client_id=client.id
                                                      join is_doc_moule idm                 on idm.dossier_article_id=article.article_id
                                                      join is_param_project ipp             on idm.param_project_id=ipp.id

                where idm.active='t' and idm.suivi_projet='t' and idm.param_project_id in (%s) %s
            """%(','.join(modele_ids),WHERE)





        if type_modele=='Moule':
            #** Moules ********************************************************
            SQL="""
                select
                    idm.id               id,
                    im.name              moule,
                    im.designation       designation,
                    im.id                moule_id,
                    'is.mold'            res_model,
                    imp.name             projet,
                    imp.id               projet_id,
                    rp.name              cp,
                    imp.chef_projet_id   cp_id,
                    client.name          client,
                    imp.client_id        client_id,
                    ipp.ppr_famille      famille,
                    ipp.id               famille_id,
                    idm.etat             etat,
                    im.j_actuelle        j_actuelle,
                    im.j_avancement      j_avancement,
                    idm.date_fin_gantt   date_fin_gantt,
                    idm.coefficient      coefficient,
                    idm.note             note,
                    idm.etat             etat,
                    idm.dynacase_id      dynacase_id,
                    idm.rsp_pj           rsp_pj,
                    idm.rsp_date         rsp_date,
                    idm.rsp_texte        rsp_texte,
                    idm.color            color,
                    idm.type_document
                from is_doc_moule idm inner join is_mold im         on idm.idmoule=im.id
                                    inner join is_mold_project imp  on im.project=imp.id
                                    inner join res_users ru         on imp.chef_projet_id=ru.id
                                    inner join res_partner rp       on ru.partner_id=rp.id
                                    inner join res_partner client   on imp.client_id=client.id
                                    inner join is_param_project ipp on idm.param_project_id=ipp.id
                where idm.active='t' and idm.suivi_projet='t' and idm.param_project_id in (%s) %s
            """%(','.join(modele_ids),WHERE)


            #** Dossier F *****************************************************
            SQL+="""
                UNION
                select
                    idm.id               id,
                    im.name              moule,
                    im.designation       designation,
                    im.id                moule_id,
                    'is.dossierf'        res_model,
                    imp.name             projet,
                    imp.id               projet_id,
                    rp.name              cp,
                    imp.chef_projet_id   cp_id,
                    client.name          client,
                    imp.client_id        client_id,
                    ipp.ppr_famille      famille,
                    ipp.id               famille_id,
                    idm.etat             etat,
                    im.j_actuelle        j_actuelle,
                    im.j_avancement      j_avancement,
                    idm.date_fin_gantt   date_fin_gantt,
                    idm.coefficient      coefficient,
                    idm.note             note,
                    idm.etat             etat,
                    idm.dynacase_id      dynacase_id,
                    idm.rsp_pj           rsp_pj,
                    idm.rsp_date         rsp_date,
                    idm.rsp_texte        rsp_texte,
                    idm.color            color,
                    idm.type_document
                from is_doc_moule idm inner join is_dossierf im     on idm.dossierf_id=im.id
                                    inner join is_mold_project imp  on im.project=imp.id
                                    inner join res_users ru         on imp.chef_projet_id=ru.id
                                    inner join res_partner rp       on ru.partner_id=rp.id
                                    inner join res_partner client   on imp.client_id=client.id
                                    inner join is_param_project ipp on idm.param_project_id=ipp.id
                where idm.active='t' and idm.suivi_projet='t' and idm.param_project_id in (%s) %s 
                limit 10000
            """%(','.join(modele_ids),WHERE)

        alert=''
        if len(modele_ids)>0:
            cr.execute(SQL)
            rows = cr.dictfetchall()
            if len(rows)==10000:
                alert="Limite de 10 000 dépassée => Tous les documents ne sont pas affichés"
            _logger.info("Requête SQL (nb doc=%s) (durée=%.2fs)"%(len(rows),(datetime.now()-debut).total_seconds())) # 0.02s par document
            for row in rows:
                doc=False
                doc_id = row['id']
                #doc = self.env['is.doc.moule'].browse(doc_id)
                if doc_id:
                    key="%s-%s"%(row['moule'],row['moule_id'])
                    if key not in mydict:
                        #** Recherche photo du moule **************************
                        photo=''
                        if avec_photo=='Oui':
                            doc = self.env['is.doc.moule'].browse(doc_id)
                            image=False
                            if doc and doc.idmoule:
                                image = doc.idmoule.image
                            if doc and doc.dossierf_id:
                                image = doc.dossierf_id.image
                            if image and image!='':
                                photo = 'data:image/png;base64, %s'%image.decode("utf-8")




                        #** avancement_j **************************************
                        #j_actuelle = False
                        #avancement_j=[False,False]
                        # if doc.idmoule:
                        #     if doc.idmoule.j_actuelle:
                        #         j_actuelle = dict(GESTION_J).get(doc.idmoule.j_actuelle,"?")
                        #         avancement_j=[j_actuelle, doc.idmoule.j_avancement]
                        # if doc.dossierf_id:
                        #     if doc.dossierf_id.j_actuelle:
                        #         j_actuelle = dict(GESTION_J).get(doc.dossierf_id.j_actuelle,"?")
                        #         avancement_j=[j_actuelle, doc.dossierf_id.j_avancement]

                        # if row['res_model']=='is.mold':
                        #     if row['j_actuelle']:
                        #         j_actuelle = dict(GESTION_J).get(row['j_actuelle'],"?")
                        #         avancement_j=[j_actuelle, row['j_avancement']]
                        # if row['res_model']=='is.dossierf':
                        #     if row['j_actuelle']:
                        #         j_actuelle = dict(GESTION_J).get(row['j_actuelle'],"?")
                        #         avancement_j=[j_actuelle, row['j_avancement']]

                        j_actuelle = False
                        if row['j_actuelle']:
                            j_actuelle = dict(GESTION_J).get(row['j_actuelle'],"?")
                        
                        #** Calcul du nombre de modifications variantes ***
                        nb_modif_variante = 0
                        domain_modif = False
                        if row['res_model'] == 'is.mold':
                            domain_modif = [('demao_idmoule', '=', row['moule_id'])]
                        elif row['res_model'] in ['is.dossierf', 'is.dossier.article']:
                            domain_modif = [('dossierf_id', '=', row['moule_id'])]
                        
                        if domain_modif:
                            nb_modif_variante = self.env['is.dossier.modif.variante'].search_count(domain_modif)
                        
                        vals={
                            'key'         : key,
                            'res_model'   : row['res_model'],
                            'moule'       : row['moule'],
                            'designation' : row['designation'],
                            'moule_id'    : row['moule_id'],
                            'projet'      : row['projet'],
                            'projet_id'   : row['projet_id'],
                            'photo'       : photo,
                            'cp'          : row['cp'],
                            'cp_id'       : row['cp_id'],
                            'familles'    : copy.deepcopy(familles),
                            'j_actuelle'  : j_actuelle,
                            'avancement_j'     : 0,
                            'total_coefficient': 0,
                            'total_note'       : 0,
                            'nb_notes'         : 0,
                            'nb_modif_variante': nb_modif_variante,
                        }
                        mydict[key]=vals

                    for famille in mydict[key]['familles']:
                        famille_id = mydict[key]['familles'][famille]['id']
                        if row['famille_id']==famille_id:
                            #** date_fin_gantt ********************************
                            date_fin_gantt='(date)'
                            if row['date_fin_gantt']:
                                date_fin_gantt=row['date_fin_gantt'].strftime("%d/%m/%Y")
                            color       = row['color']
                            coefficient = row['coefficient'] or 0
                            note        = row['note'] or 0
                            if coefficient>0:
                                mydict[key]['nb_notes']+=1
                                mydict[key]['total_note']+=note
                                mydict[key]['total_coefficient']+=coefficient
                            rsp_date    = row['rsp_date']
                            if rsp_date:
                                rsp_date=rsp_date.strftime("%d/%m/%y")
                            reponse=[row['rsp_pj'],rsp_date,row['rsp_texte']]
                            vals={
                                'doc_id'        : doc_id,
                                'etat'          : row['etat'],
                                'date_fin_gantt': date_fin_gantt,
                                'coefficient'   : coefficient,
                                'note'          : note,
                                'style'         : 'background-color:%s'%color,
                                'dynacase_id'   : row['dynacase_id'],
                                'type_document' : row['type_document'],
                                'reponse'       : reponse,
                            }
                            mydict[key]['familles'][famille].update(vals)


                    if mydict[key]['total_coefficient']>0:
                        mydict[key]['avancement_j'] =round(100*mydict[key]['total_note']/mydict[key]['total_coefficient'])





        sorted_dict = dict(sorted(mydict.items())) 

        #** Ajout de la couleur des lignes ************************************
        trcolor=""
        for k in sorted_dict:
            if trcolor=="#ffffff":
                trcolor="#f2f3f4"
            else:
                trcolor="#ffffff"
            trstyle="background-color:%s"%(trcolor)
            sorted_dict[k]["trstyle"] = trstyle
        _logger.info("Fin (durée=%.2fs)"%(datetime.now()-debut).total_seconds())

        res={
            "dict"              : sorted_dict,
            "familles"          : familles,
            "client"            : client,
            "projet"            : projet,
            "moule"             : moule,
            "cp_id"             : cp_id,
            "cp_options"        : cp_options,
            "type_moule"        : type_moule,
            "type_moule_options": type_moule_options,
            "avec_photo"        : avec_photo,
            "avec_photo_options": avec_photo_options,
            "modele_id"         : modele_id,
            "modele_options"    : modele_options,
            "alert"             : alert,
        }
        return res

    
    def _get_doc_modele(self,res_model,res_id,modele_id):
        modele_bilan = self.env['is.modele.bilan'].browse(int(modele_id))
        if modele_bilan:
            famille_ids=modele_bilan.get_famille_ids()
        domain=False
        if res_model=='is.mold':
            domain=[
                ('idmoule','=',int(res_id)),
                ('param_project_id','in',famille_ids),
            ]
        if res_model=='is.dossierf':
            domain=[
                ('dossierf_id','=',int(res_id)),
                ('param_project_id','in',famille_ids),
            ]
        docs=False
        if domain:
            docs=self.env['is.doc.moule'].search(domain)
        return docs


    def get_doc_modele(self,res_model,res_id,modele_id):
        tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_suivi_projet_tree_view').id
        docs = self._get_doc_modele(res_model,res_id,modele_id)
        ids=[]
        if docs:
            for doc in docs:
                ids.append(doc.id)
        res = {
            'ids'    : ids,
            'tree_id': tree_id,
        }
        return res
    

    def _get_doc_famille(self,res_id):
        doc = self.env['is.doc.moule'].browse(int(res_id))
        docs=False
        if doc:
            domain=[
                ('idmoule','=',doc.idmoule.id),
                ('dossierf_id','=',doc.dossierf_id.id),
                ('param_project_id','=',doc.param_project_id.id),
            ]
            docs=self.env['is.doc.moule'].search(domain)
        return docs


    def get_doc_famille(self,res_id):
        tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_tree').id
        docs = self._get_doc_famille(res_id)
        ids=[]
        if docs:
            for doc in docs:
                ids.append(doc.id)
        res = {
            'ids'    : ids,
            'tree_id': tree_id,
        }
        return res
    

    def get_zip(self,res_model,res_id,modele_id):
        attachment_id=False
        docs = self._get_doc_modele(res_model,res_id,modele_id)
        ids=[]
        if docs:
            for doc in docs:
                ids.append(doc.id)
        nb_pdf=0
        if ids!=[]:
            domain=[('id', 'in', ids)]
            docs=self.env['is.doc.moule'].search(domain)
            if len(docs)>0:
                moule_dossierf = doc[0].moule_dossierf
                name_dossier   = "dossier-%s-%s"%(moule_dossierf,self._uid)
                tmp_dir        = "/tmp/%s"%name_dossier 
                Path(tmp_dir).mkdir(parents=True, exist_ok=True)
                for doc in docs:
                    for line in doc.array_ids:
                        if doc.param_project_id.ppr_transformation_pdf:
                            champ=line.annex_pdf
                        else:
                            champ=line.annex
                        for attachment in champ:
                            if attachment.datas:
                                tmp_dir_doc = unidecode.unidecode("%s/%s"%(tmp_dir,doc.param_project_id.ppr_famille)) # Sans les accents                          
                                cde='mkdir -p "%s"'%tmp_dir_doc
                                p = Popen(cde, shell=True, stdout=PIPE, stderr=PIPE)
                                stdout, stderr = p.communicate()
                                _logger.info("cde:%s, stdout:%s, stderr:%s"%(cde,stdout.decode("utf-8"),stderr.decode("utf-8")))
                                if stderr:
                                    raise ValidationError("%s\n%s"%(cde,stderr.decode("utf-8")))
                                file_name = unidecode.unidecode('/%s/%s'%(tmp_dir_doc,attachment.name)) # Sans les accents     
                                with open(file_name,'wb') as f:
                                    f.write(base64.decodebytes(attachment.datas))
                                    nb_pdf+=1
                if nb_pdf>0:
                    cde = 'cd /tmp && zip -r %s.zip %s'%(name_dossier,name_dossier)
                    p = Popen(cde, shell=True, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = p.communicate()
                    _logger.info("cde:%s, stdout:%s, stderr:%s"%(cde,stdout.decode("utf-8"),stderr.decode("utf-8")))
                    if stderr:
                        raise ValidationError("%s\n%s"%(cde,stderr.decode("utf-8")))
                    else: 
                        # ** Creation ou modification de la pièce jointe ******
                        name ="%s.zip"%name_dossier
                        path="/tmp/%s"%name
                        zip = open(path,'rb').read()
                        attachments = self.env['ir.attachment'].search([('name','=',name)],limit=1)
                        vals = {
                            'name':        name,
                            'type':        'binary',
                            'datas':       base64.b64encode(zip),
                        }
                        if attachments:
                            for attachment in attachments:
                                attachment.write(vals)
                                attachment_id=attachment.id
                        else:
                            attachment = self.env['ir.attachment'].create(vals)
                            attachment_id=attachment.id
                        #***********************************************************************

                    #** Suppression du dossier et du zip **********************
                    cde = 'cd /tmp && rm -Rf %s'%(name_dossier)
                    p = Popen(cde, shell=True, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = p.communicate()
                    cde = 'cd /tmp && rm %s.zip'%(name_dossier)
                    p = Popen(cde, shell=True, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = p.communicate()
                    #**********************************************************

        res = {
            'attachment_id'    : attachment_id,
        }
        return res
    

    def get_cr_jalon(self,res_model,res_id,modele_id):
        domain=False
        if res_model=='is.mold':
            domain=[('rpj_mouleid','=',int(res_id))]
        if res_model=='is.dossierf':
            domain=[('dossierf_id','=',int(res_id))]
        id=False
        if domain:
            docs=self.env['is.revue.projet.jalon'].search(domain, order="id desc", limit=1)
            for doc in docs:
                id=doc.id
        res = {
            'id'   : id,
            'model': 'is.revue.projet.jalon',
        }
        return res
    

    def get_cr_risque(self,res_model,res_id,modele_id):
        domain=False
        if res_model=='is.mold':
            domain=[('rr_mouleid','=',int(res_id))]
        id=False
        if domain:
            docs=self.env['is.revue.risque'].search(domain, order="id desc", limit=1)
            for doc in docs:
                id=doc.id
        res = {
            'id'   : id,
            'model': 'is.revue.risque',
        }
        return res

    def get_modif_variante(self,res_model,res_id):
        domain=False
        if res_model=='is.mold':
            domain=[('demao_idmoule','=',int(res_id))]
        if res_model=='is.dossierf':
            domain=[('dossierf_id','=',int(res_id))]
        ids=[]
        if domain:
            docs=self.env['is.dossier.modif.variante'].search(domain, order="demao_date desc")
            for doc in docs:
                ids.append(doc.id)
        res = {
            'ids': ids,
        }
        return res