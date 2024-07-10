# -*- coding: utf-8 -*-
from odoo import models,fields,api
from datetime import datetime, timedelta


_DAO_RSPLAST=([
    ('A', 'A=Acceptée'),
    ('D', 'D=Déclinée'),
])


_DAO_MOTIF=([
    ('P01', 'Perdu - Prix moule & pièce'),
    ('P02', 'Perdu - Prix moule'),
    ('P03', 'Perdu - Prix pièce'),
    ('P04', 'Perdu - Délai trop long'),
    ('P05', 'Perdu - Projet client annulé'),
    ('P06', 'Perdu - Pas de retour client'),
    ('P07', 'Perdu - Choix stratégique client'),
    ('D01', 'Décliné - Motif technique (process ou techno)'),
    ('D02', 'Décliné - Capacitaire PG'),
    ('D03', 'Décliné - Volume faible'),
    ('D04', 'Décliné - Stratégique'),
])


_DAO_AVANCEMENT=([
    ('Développement', 'Développement'),
    ('Série'        , 'Série'),
])


_STATE=([
    ('plascreate'     , 'créé'),
    ('plasanalysed'   , 'analysé'),
    ('plastransbe'    , 'transmis BE'),
    ('plasvalidbe'    , 'validé BE'),
    ('plasvalidcom'   , 'validé commercial'),
    ('plasdiffusedcli', 'diffusé client'),
    ('plasrelancecli' , 'relance client'),
    ('plaswinned'     , 'gagné'),
    ('plasloosed'     , 'perdu'),
    ('plascancelled'  , 'annulé'),
])


class is_dossier_appel_offre(models.Model):
    _name = "is.dossier.appel.offre"
    _description="is_dossier_appel_offre"
    _order = "dao_num"
    _rec_name = 'dao_num'

    dao_num          = fields.Char("Numéro")
    dao_date         = fields.Date("Date consultation")
    dao_annee        = fields.Char("Année consultation")
    dao_client       = fields.Char("Client")
    dao_typeclient   = fields.Char("Type client")
    dao_sectclient   = fields.Char("Section client")
    dao_commercial   = fields.Char("Commercial")
    dao_desig        = fields.Char("Désignation")
    dao_ref          = fields.Char("Référence")
    dao_datedms      = fields.Date("Date DMS")
    dao_ca           = fields.Float("Chiffre d'affaire")
    dao_vacom        = fields.Float("VA commerciale")
    dao_pourcentva   = fields.Float("% VA")
    dao_camoule      = fields.Float("CA Moule")
    dao_be           = fields.Char("Chef de projet")
    dao_dirbe        = fields.Char("Directeur technique")
    dao_daterepbe    = fields.Date("Date réponse BE")
    dao_daterepplast = fields.Date("Date réponse Plastigray")
    dao_daterepcli   = fields.Date("Date réponse client")
    dao_comment      = fields.Char("Commentaire")
    dynacase_id      = fields.Integer("id Dynacase",index=True)

    dao_rsplast      = fields.Selection(_DAO_RSPLAST, "Rsp Plastigray")
    dao_motif        = fields.Selection(_DAO_MOTIF, "Motif")
    dao_avancement   = fields.Selection(_DAO_AVANCEMENT, "Avancement")
    state            = fields.Selection(_STATE, "Etat")


    def gantt_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('dossier_appel_offre_id', '=', obj.id) ])
            ids=[]
            for doc in docs:
                ids.append(doc.id)
            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossier_appel_offre_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                'default_type_document': 'dossier_appel_offre',
                'default_dossier_appel_offre_id'  : obj.id,
                'default_etat'         :'AF',
                'default_dateend'      : datetime.today(),
                'default_idresp'       : self._uid,
            }
            return {
                'name': obj.dao_num,
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



    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
            
            
