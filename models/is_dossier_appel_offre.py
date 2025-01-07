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
    ('Analyse_BE'     , 'Analysé BE'),
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
    _inherit=['mail.thread']
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="is_dossier_appel_offre"
    _order = "dao_num"
    _rec_name = 'dao_num'

    dao_num          = fields.Char("Numéro", tracking=True)
    dao_date         = fields.Date("Date consultation", tracking=True)
    dao_annee        = fields.Char("Année consultation", tracking=True)
    dao_client       = fields.Char("Client", tracking=True)
    dao_typeclient   = fields.Char("Type client", tracking=True)
    dao_sectclient   = fields.Char("Section client", tracking=True)
    dao_commercial   = fields.Char("Commercial", tracking=True)
    dao_desig        = fields.Char("Désignation", tracking=True)
    dao_ref          = fields.Char("Référence", tracking=True)
    dao_datedms      = fields.Date("Date DMS", tracking=True)
    dao_ca           = fields.Float("Chiffre d'affaire", tracking=True)
    dao_vacom        = fields.Float("VA commerciale", tracking=True)
    dao_pourcentva   = fields.Float("% VA", tracking=True)
    dao_camoule      = fields.Float("CA Moule", tracking=True)
    dao_be           = fields.Char("Chef de projet", tracking=True)
    dao_dirbe        = fields.Char("Directeur technique", tracking=True)
    dao_daterepbe    = fields.Date("Date réponse BE", tracking=True)
    dao_daterepplast = fields.Date("Date réponse Plastigray", tracking=True)
    dao_daterepcli   = fields.Date("Date réponse client", tracking=True)
    dao_comment      = fields.Char("Commentaire", tracking=True)
    dynacase_id      = fields.Integer("id Dynacase",index=True,copy=False)

    dao_rsplast      = fields.Selection(_DAO_RSPLAST, "Rsp Plastigray", tracking=True)
    dao_motif        = fields.Selection(_DAO_MOTIF, "Motif", tracking=True)
    dao_avancement   = fields.Selection(_DAO_AVANCEMENT, "Avancement", tracking=True)
    state            = fields.Selection(_STATE, "Etat", tracking=True)

    dao_consult_initial   = fields.Many2many("ir.attachment", "is_dao_consult_initial_rel"  , "consult_initial_id"  , "att_id", string="Consultation initiale client")
    dao_annexcom          = fields.Many2many("ir.attachment", "is_dao_annexcom_rel"         , "annexcom_id"         , "att_id", string="Fichiers commercial")
    dao_annex             = fields.Many2many("ir.attachment", "is_dao_annex_rel"            , "annex_id"            , "att_id", string="Fiche de devis du be")
    dao_offre_validee     = fields.Many2many("ir.attachment", "is_dao_offre_validee_rel"    , "offre_validee_id"    , "att_id", string="Dernière offre validée par le client")
    dao_commande_client   = fields.Many2many("ir.attachment", "is_dao_commande_client_rel"  , "commande_client_id"  , "att_id", string="Commande client")
    dao_lettre_nomination = fields.Many2many("ir.attachment", "is_dao_lettre_nomination_rel", "lettre_nomination_id", "att_id", string="Lettre de nomination et contrats")
    dao_devis_achat       = fields.Many2many("ir.attachment", "is_dao_devis_achat_rel"      , "devis_achat_id"      , "att_id", string="Fichier de devis des achats")
    fermeture_id          = fields.Many2one("is.fermeture.gantt", string="Fermeture du Gantt", tracking=True)
    active                = fields.Boolean('Actif', default=True, tracking=True)


    def gantt_action(self):
        for obj in self:
            # docs=self.env['is.doc.moule'].search([ ('dossier_appel_offre_id', '=', obj.id) ])
            # ids=[]
            # for doc in docs:
            #     ids.append(doc.id)
            domain = [('dossier_appel_offre_id', '=', obj.id)]
            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossier_appel_offre_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                'default_type_document': 'dossier_appel_offre',
                'default_dossier_appel_offre_id'  : obj.id,
                'default_etat'          :'AF',
                'default_date_fin_gantt': datetime.today(),
                'default_idresp'        : self._uid,
            }
            return {
                'name': obj.dao_num,
                'view_mode': 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph',
                "views"    : [
                    (gantt_id, "dhtmlxgantt_project"),
                    (tree_id, "tree"),
                    (False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
                'res_model': 'is.doc.moule',
                # 'domain': [
                #     ('id','in',ids),
                # ],
                'domain': domain,
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
            
            
