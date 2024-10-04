# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
import copy
import logging
_logger = logging.getLogger(__name__)


class IsDocMoule(models.Model):
    _inherit        = "is.doc.moule"


    def get_suivi_projet(
            self, 
            cp_id=False,
            client=False,
            projet=False,
            moule=False,
            type_moule=False,
            modele_id=False,
            ok=False
        ):
        cr = self._cr

        #** set/get var *****************************************************
        debut=datetime.now()
        if ok:
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_cp_id'     , cp_id)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_client'    , client)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_projet'    , projet)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_moule'     , moule)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_type_moule', type_moule)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_modele_id' , modele_id)
        else:
            cp_id      = self.env['is.mem.var'].get(self._uid, 'suivi_projet_cp_id')
            client     = self.env['is.mem.var'].get(self._uid, 'suivi_projet_client')
            projet     = self.env['is.mem.var'].get(self._uid, 'suivi_projet_projet')
            moule      = self.env['is.mem.var'].get(self._uid, 'suivi_projet_moule')
            type_moule = self.env['is.mem.var'].get(self._uid, 'suivi_projet_type_moule')
            modele_id  = self.env['is.mem.var'].get(self._uid, 'suivi_projet_modele_id')
        _logger.info("set/get var (durée=%.2fs)"%(datetime.now()-debut).total_seconds())


        #** Valeur par défaut *************************************************
        if not type_moule:
            type_moule='Actif'


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


        #** Recherche des familles du modele **********************************
        modele_ids=[]
        familles={}
        if modele_id:
            modeles=self.env['is.modele.bilan'].search([('id','=',modele_id)])

            for modele in modeles:
                ct=0
                for line in modele.line_ids:
                    ct+=1
                    id = line.param_project_id.id
                    if id:
                        modele_ids.append(str(id))
                        familles[ct]={
                            'ct'    : ct,
                            'id'    : id,
                            'name'  : line.param_project_id.ppr_famille,
                            'html'  : '',
                            'doc_id': False,
                        }

        mydict={}
        if len(modele_ids)>0:
            SQL="""
                select
                    idm.id,
                    im.name         moule,
                    idm.idmoule,
                    im.project,
                    imp.name        projet,
                    imp.chef_projet_id,
                    rp.name         cp,
                    imp.client_id,
                    client.name     client,
                    ipp.ppr_famille famille,
                    idm.param_project_id,
                    idm.etat
                from is_doc_moule idm inner join is_mold im           on idm.idmoule=im.id
                                    inner join is_mold_project imp  on im.project=imp.id
                                    inner join res_users ru         on imp.chef_projet_id=ru.id
                                    inner join res_partner rp       on ru.partner_id=rp.id
                                    inner join res_partner client   on imp.client_id=client.id
                                    inner join is_param_project ipp on idm.param_project_id=ipp.id
                where idm.active='t' and idm.param_project_id in (%s)
            """%','.join(modele_ids)
            if cp_id and cp_id!='0':
                SQL+=" and ru.id=%s "%cp_id
            if client:
                SQL+=" and client.name ilike '%"+client+"%' "
            if projet:
                SQL+=" and imp.name ilike '%"+projet+"%' "
            if moule:
                SQL+=" and im.name ilike '"+moule+"%' "
            if type_moule and type_moule=='Actif':
                SQL+=" and im.date_fin is null "
            SQL+="""
                order by im.name,ipp.ppr_famille
                limit 1000;
            """
            cr.execute(SQL)
            rows = cr.dictfetchall()

            for row in rows:
                idmoule          = row['idmoule']
                key="%s-%s"%(row['moule'],idmoule)
                param_project_id = row['param_project_id']
                if key not in mydict:
                    vals={
                        'key'     : key,
                        'idmoule' : idmoule,
                        'moule'   : row['moule'],
                        'familles': copy.deepcopy(familles),
                    }
                    mydict[key]=vals
                for famille in mydict[key]['familles']:
                    famille_id = mydict[key]['familles'][famille]['id']
                    if param_project_id==famille_id:
                        mydict[key]['familles'][famille]['html']=row['etat']
                        mydict[key]['familles'][famille]['doc_id']=row['id']

        res={
            "dict"              : mydict,
            "familles"          : familles,
            "client"            : client,
            "projet"            : projet,
            "moule"             : moule,
            "cp_id"             : cp_id,
            "cp_options"        : cp_options,
            "type_moule"        : type_moule,
            "type_moule_options": type_moule_options,
            "modele_id"         : modele_id,
            "modele_options"    : modele_options,
        }
        return res

    