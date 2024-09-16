# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)


class IsDocMoule(models.Model):
    _inherit        = "is.doc.moule"


    def get_suivi_projet(
            self, 
            cp=False,
            client=False,
            projet=False,
            moule=False,
            type_moule=False,
            modele=False,
            ok=False
        ):
        cr = self._cr

        #** set/get var *****************************************************
        debut=datetime.now()
        if ok:
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_cp'        , cp)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_client'    , client)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_projet'    , projet)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_moule'     , moule)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_type_moule', type_moule)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_modele'    , modele)
        else:
            cp         = self.env['is.mem.var'].get(self._uid, 'suivi_projet_cp')
            client     = self.env['is.mem.var'].get(self._uid, 'suivi_projet_client')
            projet     = self.env['is.mem.var'].get(self._uid, 'suivi_projet_projet')
            moule      = self.env['is.mem.var'].get(self._uid, 'suivi_projet_moule')
            type_moule = self.env['is.mem.var'].get(self._uid, 'suivi_projet_type_moule')
            modele     = self.env['is.mem.var'].get(self._uid, 'suivi_projet_modele')
        _logger.info("set/get var (durée=%.2fs)"%(datetime.now()-debut).total_seconds())



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
                idm.param_project_id
            from is_doc_moule idm inner join is_mold im           on idm.idmoule=im.id
                                inner join is_mold_project imp  on im.project=imp.id
                                inner join res_users ru         on imp.chef_projet_id=ru.id
                                inner join res_partner rp       on ru.partner_id=rp.id
                                inner join res_partner client   on imp.client_id=client.id
                                inner join is_param_project ipp on idm.param_project_id=ipp.id
            where idm.idproject=386
            order by im.name,ipp.ppr_famille
            -- limit 30;
        """


        cr.execute(SQL)
        rows = cr.dictfetchall()

        mydict={}
        for row in rows:
            print(row['id'])
            idmoule          = row['idmoule']

            key="%s-%s"%(row['moule'],idmoule)

            param_project_id = row['param_project_id']

            if key not in mydict:
                vals={
                    'key'    : key,
                    'idmoule': idmoule,
                    'moule'  : row['moule'],
                }
                mydict[key]=vals



            # if param_project_id not in mydict[idmoule]:
            #     mydict[idmoule][param_project_id]=row



        print(mydict)


        #sorted_dict = dict(sorted(mydict.items())) 



        print(cp,client,projet, moule,type_moule,modele,ok)
        #lines=self.env['is.doc.moule'].search([], limit=10) #, order="dateend"
        res={
            "cp"        : cp,
            "client"    : client,
            "projet"    : projet,
            "moule"     : moule,
            "type_moule": type_moule,
            "modele"    : modele,
            "dict"      : mydict,
        }
        return res

    