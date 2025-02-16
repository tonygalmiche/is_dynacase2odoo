# -*- coding: utf-8 -*-
from odoo import models, fields, api, _                              # type: ignore
from odoo.tools import format_date, formatLang, frozendict, config   # type: ignore
from odoo.exceptions import AccessError, ValidationError, UserError  # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J, TYPE_DOCUMENT, MODELE_TO_TYPE, TYPE_TO_FIELD, DOCUMENT_ACTION, DOCUMENT_ETAT # type: ignore
import shutil
from pathlib import Path
from datetime import datetime, timedelta, date
from time import time
from random import *
from subprocess import PIPE, Popen
import base64
import logging
_logger = logging.getLogger(__name__)


class IsDocMoule(models.Model):
    _name        = "is.doc.moule"
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Document moule"
    #_rec_name    = "param_project_id"
    _order = 'section_id,sequence,section_id,param_project_id'


    def compute_project_prev(self):
        "for xml-rpc"
        self.update_j_prevue_action()
        self._compute_project_prev()
        self._compute_idproject_moule_dossierf()
        self._compute_site_id()
        self._compute_demao_nature()
        self._compute_solde()
        self._compute_actuelle()
        self._compute_rsp_pj()
        self._compute_coefficient_bloquant_note()
        self._compute_color()
        self._compute_indicateur()
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
                    <div height='60px' width='100%' style='padding: 5px;margin-bottom:5px;font-size:18px;background-color:"""+color+"""'>
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


    @api.depends('idmoule.j_actuelle', 'dossierf_id.j_actuelle')
    def _compute_actuelle(self):
        for obj in self:
            actuelle=False
            if obj.idmoule:
                actuelle=obj.idmoule.j_actuelle
            if obj.dossierf_id:
                actuelle=obj.dossierf_id.j_actuelle
            obj.actuelle = actuelle


    @api.depends('j_prevue')
    def _compute_date_j_prevue(self):
        for obj in self:
            date_j_prevue=False
            rl=False
            if obj.idmoule:
                rl=obj.idmoule.revue_lancement_id
            if obj.dossierf_id:
                actuelle=obj.dossierf_id.revue_lancement_id
            if rl:
                if obj.j_prevue and obj.j_prevue!='J6':
                    date_j_prevue = getattr(rl, "rl_date_%s"%obj.j_prevue.lower())
            obj.date_j_prevue = date_j_prevue


    type_document = fields.Selection(TYPE_DOCUMENT,string="Type de document", default="Moule", required=True, tracking=True)
    sequence = fields.Integer(string="Ordre", tracking=True, copy=False)
    project_prev     = fields.Html(compute='_compute_project_prev', store=True)
    project_prev2    = fields.Html()
    param_project_id = fields.Many2one("is.param.project", string="Famille de document", tracking=True, index=True)
    param_project_array_html = fields.Html(related="param_project_id.array_html")
    ppr_type_demande         = fields.Selection(related="param_project_id.ppr_type_demande")
    ppr_transformation_pdf   = fields.Boolean(related="param_project_id.ppr_transformation_pdf")
    ppr_icon         = fields.Image(related="param_project_id.ppr_icon", string="Icône", store=True)
    ppr_color        = fields.Char(related="param_project_id.ppr_color", string="Color", store=True)
    idmoule          = fields.Many2one("is.mold"                  , string="Moule"    , tracking=True, index=True)
    dossierf_id      = fields.Many2one("is.dossierf"              , string="Dossier F", tracking=True, index=True)
    dossier_modif_variante_id = fields.Many2one("is.dossier.modif.variante", string="Dossier Modif / Variante", tracking=True)
    dossier_article_id        = fields.Many2one("is.dossier.article"       , string="Dossier article", index=True, tracking=True)
    dossier_appel_offre_id    = fields.Many2one("is.dossier.appel.offre"   , string="Dossier appel d'offre", tracking=True)
    moule_dossierf   = fields.Char("Moule / Dossier F"                   , compute='_compute_idproject_moule_dossierf',store=True, readonly=True)
    idproject        = fields.Many2one("is.mold.project", string="Projet", compute='_compute_idproject_moule_dossierf',store=True, readonly=True)
    client_id        = fields.Many2one("res.partner", string="Client"    , compute='_compute_idproject_moule_dossierf',store=True, readonly=True)
    idcp             = fields.Many2one(related="idmoule.chef_projet_id", string="CP", tracking=True)
    idresp           = fields.Many2one("res.users", string="Responsable", tracking=True)
    j_prevue         = fields.Selection(GESTION_J, string="J Prévue", tracking=True)
    date_j_prevue    = fields.Date(string="Date J prévue", compute='_compute_date_j_prevue',store=True, readonly=True)
    actuelle         = fields.Selection(GESTION_J, string="J Actuelle", tracking=True, compute='_compute_actuelle',store=True, readonly=True)
    demande          = fields.Char(string="Demande", tracking=True)
    action           = fields.Selection(DOCUMENT_ACTION, string="Action", compute='_compute_action', store=True, readonly=True, tracking=True, copy=False)
    etat             = fields.Selection(DOCUMENT_ETAT, string="État", tracking=True, copy=False) # , compute='_compute_etat',store=True, readonly=False
    fin_derogation      = fields.Date(string="Date de fin de dérogation")
    coefficient         = fields.Integer(string="Coefficient"   , compute='_compute_coefficient_bloquant_note',store=True, readonly=True, tracking=True)
    bloquant            = fields.Boolean(string="Point Bloquant", compute='_compute_coefficient_bloquant_note',store=True, readonly=True, tracking=True)
    note                = fields.Integer(string="Note"          , compute='_compute_coefficient_bloquant_note',store=True, readonly=True, tracking=True)
    indicateur          = fields.Html(string="Indicateur"       , compute='_compute_indicateur'               ,store=True, readonly=True)
    datecreate          = fields.Date(string="Date de création", default=fields.Date.context_today)
    dateend             = fields.Date(string="Date fin dynacase (Ne plus utiliser)", readonly=True, help="Remplacé par date_fin_gantt le 05/12/2024")
    array_ids           = fields.One2many("is.doc.moule.array", "is_doc_id", string="Pièce-jointe de réponse à la demande")
    dynacase_id         = fields.Integer(string="Id Dynacase",index=True,copy=False)
    duree               = fields.Integer(string="Durée (J)"      , help="Durée en jours ouvrés"         , default=1, tracking=True)
    duree_gantt         = fields.Integer(string="Durée Gantt (J)", help="Durée calendaire pour le Gantt", default=1, tracking=True, readonly=True)
    duree_attente_avant = fields.Integer("Durée attente avant (J)", help="Utilisée dans le Gantt")
    date_debut_gantt    = fields.Date(string="Date début", default=lambda self: self._date_debut_gantt(), tracking=True)
    date_fin_gantt      = fields.Date(string="Date fin", tracking=True)
    section_id          = fields.Many2one("is.section.gantt", string="Section Gantt",index=True, tracking=True, copy=False)
    gantt_pdf           = fields.Boolean("Gantt PDF", default=True, help="Afficher dans Gantt PDF")
    dependance_id       = fields.Many2one("is.doc.moule", string="Dépendance",index=True, tracking=True, copy=False)
    origine_copie_id    = fields.Many2one("is.doc.moule", string="Origine de la copie",index=True, copy=False)
    active              = fields.Boolean('Actif', default=True, tracking=True)
    site_id             = fields.Many2one('is.database', "Site", compute='_compute_site_id', readonly=True, store=True)
    demao_nature        = fields.Char(string="Nature", compute='_compute_demao_nature'     , readonly=True, store=True)
    solde               = fields.Boolean(string="Soldé", compute='_compute_solde'          , readonly=True, store=True)
    rsp_date            = fields.Date(string="Date réponse", copy=False, tracking=True)
    rsp_texte           = fields.Text(string="Texte réponse", copy=False, tracking=True)
    rsp_pj              = fields.Text(string="Réponse PJ", compute='_compute_rsp_pj', readonly=True, store=True, tracking=True)
    rsp_auto            = fields.Html(string="Réponse Auto", readonly=True)
    acces_chef_projet   = fields.Boolean(string="Accès chef de projet", compute='_compute_acces_chef_projet', readonly=True, store=False, help="Indique si les champs réservés au chef de projet sont modifiables")
    color               = fields.Char(string="Couleur indicateur", compute='_compute_color', readonly=True, store=True)
    date_creation_auto  = fields.Datetime(string="Date création auto",copy=False,readonly=True)
    attendus            = fields.Char(related="param_project_id.ppr_demande", string="Attendus")
    conforme            = fields.Selection([
        ("01", "Conforme à la norme FMV SS n°302 < 102 mm/min (ou 4 inches/min)"),
        ("02", "Conforme à l’exigence client < 80 mm/min"),
    ],string="Conforme", tracking=True)
    suivi_projet        = fields.Boolean(string="Suivi des projets", default=True, tracking=True, help="Indique si c'est ce document qui doit être affiché dans le suivi des projets dans le cas où il y a plusieurs documents de la même famille")


    # attachment_ids      = fields.One2many("ir.attachment", "is_doc_moule_id", string="Pièces-jointes")



    @api.onchange('etat')
    def onchange_etat(self):
        for obj in self:
            type_demande = obj.param_project_id.ppr_type_demande
            if type_demande in ['DATE','PJ_DATE']:
                if obj.etat=='F':
                    obj.rsp_date = date.today()
                else:
                    obj.rsp_date=False


    @api.depends('etat','date_fin_gantt','date_j_prevue')
    def _compute_color(self):
        "Retourne la couleur de l'indicateur en fonction de différent paramètres"
        for obj in self:
            now = date.today()
            if obj.type_document=='Article':
                if obj.etat=='F':
                    color='SpringGreen'
                else:
                    color = 'Orange'
                    if obj.date_fin_gantt and now>obj.date_fin_gantt:
                        color='Red'
            else:
                color = 'Lavender'
                if not obj.date_fin_gantt:
                    color = 'Orange'
                if obj.action=='':
                    color = 'Lavender'
                if obj.etat=='AF':
                    color='CornflowerBlue'
                if obj.etat=='D':
                    color='Orange'
                if obj.date_fin_gantt:
                    if now>obj.date_fin_gantt:
                        color='Red'
                if obj.etat in ('AF','D') and obj.date_j_prevue and obj.date_fin_gantt:
                    if obj.date_fin_gantt> obj.date_j_prevue:
                        color='Gray'
                if obj.etat=='F':
                    color='SpringGreen'
            obj.color=color


    @api.depends('etat','array_ids.annex','array_ids.comment')
    def _compute_rsp_pj(self):
        for obj in self:
            rsp_pj=[]
            for line in obj.array_ids:
                rsp=False
                if line.annex:
                    rsp=[]
                    for pj in line.annex:
                        rsp.append(pj.name)
                    rsp = ', '.join(rsp)
                if line.comment:
                    rsp="%s (%s)"%(rsp or '',line.comment)
                if rsp:
                    rsp_pj.append(rsp)
            rsp_pj = '\n'.join(rsp_pj)
            obj.rsp_pj = rsp_pj
            obj.write({'rsp_pj':rsp_pj}) # Permet de faire fonctionner le tracking


    @api.depends('param_project_id','j_prevue')
    def _compute_action(self):
        for obj in self:
            action=False
            if obj.j_prevue:
                for line in obj.param_project_id.array_ids:
                    if obj.j_prevue>=line.ppp_j:
                        action=line.ppr_irv
            obj.action=action


    @api.depends('param_project_id','j_prevue','actuelle','etat','action')
    def _compute_coefficient_bloquant_note(self):
        for obj in self:
            coefficients={'I':1,'R':3,'V':5}
            note = coefficient = 0
            bloquant = False
            if obj.actuelle:
                if not obj.j_prevue or obj.actuelle>=obj.j_prevue:
                    for line in obj.param_project_id.array_ids:
                        if obj.actuelle>=line.ppp_j:
                            if line.ppr_irv:
                                coefficient = coefficients[line.ppr_irv]
                                if line.ppr_bloquant:
                                    coefficient+=10
                                    bloquant=True
                    if obj.etat=='F':
                        note = coefficient
                        if obj.j_prevue and obj.actuelle>obj.j_prevue:
                            note=coefficient=0
            obj.coefficient = coefficient
            obj.bloquant    = bloquant
            obj.note        = note


    @api.depends('note','coefficient','etat','action','array_ids.annex','rsp_date','rsp_texte','date_fin_gantt')
    def _compute_indicateur(self):
        for obj in self:
            color = obj.color
            ladate = '(date)'
            if obj.date_fin_gantt:
                ladate = obj.date_fin_gantt.strftime('%d/%m/%Y')
            lanote=""
            if obj.coefficient>0:
                lanote = "%s/%s"%(obj.note,obj.coefficient)
            reponses=obj.get_doc_reponse()
            html="""
                <div style='background-color:"""+(color or '')+"""'>
                    <table style="border-collapse:collapse;width:100%">
                        <tr>
                            <td style="border:none;text-align:center;white-space:nowrap;" colspan="2">
                                <span>"""+(ladate or '')+"""</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="width:50%;border:none;text-align:left;white-space:nowrap;padding-left:0.5rem">
                                <span>"""+(lanote or '')+"""</span>
                            </td>
                            <td style="width:50%;border:none;text-align:right;white-space:nowrap;padding-right:0.5rem">
            """
            if reponses[0]:
                html+='<img title="'+reponses[0]+'" src="/is_dynacase2odoo/static/src/img/tronbonne.gif"/>'
            if reponses[1]:
                html+='<span>'+reponses[1]+'</span>'
            if reponses[2]:
                html+='<img title="'+reponses[2]+'" src="/is_dynacase2odoo/static/src/img/pg_bulle.png"/>'
            html+="""
                            </td> 
                        </tr>
                    </table>
                </div>
            """
            obj.indicateur = html


    # @api.depends('note','coefficient','etat','action','array_ids.annex','rsp_date','rsp_texte')
    # def _compute_etat(self):
    #     for obj in self:
    #         etat='AF'
    #         reponses=obj.get_doc_reponse()
    #         if reponses[0] or reponses[1] or reponses[2]:
    #             etat='F'
    #         if etat!='F':
    #             if obj.etat=='D' and obj.fin_derogation:
    #                 etat='D'
    #         if etat=='F':
    #             obj.fin_derogation=False
    #         obj.etat=etat


    def _compute_acces_chef_projet(self):
        for obj in self:
            acces=False
            if self.env.user.has_group('is_plastigray16.is_chef_projet_group'):
                acces=True
            obj.acces_chef_projet = acces


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


    def write(self,vals):

        #print('TEST',self,vals)


        nb=len(self)
        if nb==1:
            mem_date_debut_gantt = self.date_debut_gantt
            mem_duree            = self.duree
        res=super(IsDocMoule, self).write(vals)
        if nb==1:
            lier = self.env.context.get('lier')
            date_debut_gantt = vals.get('date_debut_gantt')
            duree            = vals.get('duree')
            delta = 0
            if isinstance(date_debut_gantt, str):
                if mem_date_debut_gantt and date_debut_gantt and lier:
                    date_debut_gantt   = datetime.strptime(date_debut_gantt, '%Y-%m-%d').date()
                    delta=(date_debut_gantt - mem_date_debut_gantt).days
            if isinstance(duree, int):
                if mem_duree and duree and lier:
                        delta=duree - mem_duree
            if delta:
                self.move_task_lier(delta)


        if 'etat' in vals:
            if vals['etat']=='F':
                reponses=self.get_doc_reponse()
                type_demande = dict(self._fields['ppr_type_demande'].get_description(self.env).get('selection')).get(self.ppr_type_demande)
                if not reponses[0] and not reponses[1] and not reponses[2] and self.ppr_type_demande!='AUTO':
                    raise ValidationError("Impossbile de passer à l'état 'Fait' car aucune réponse n'est fournie (%s) !"%type_demande)
                
        for obj in self:
            if not obj.acces_chef_projet:
                champs_interdit=[
                    'section_id',
                    'param_project_id',
                    'idresp',
                    'date_debut_gantt',
                    'date_fin_gantt',
                    'duree',
                    'j_prevue',
                    'demande',
                    'action',
                    'bloquant',
                    'type_document',
                    'sequence',
                    'idcp',
                    'gantt_pdf',
                ]
                msg=[]
                for key in vals:
                    if key in champs_interdit:
                        champ = obj._fields[key].string
                        msg.append("- %s"%champ)
                if len(msg)>0:
                    raise ValidationError("Modification non autorisée pour les champs :\n%s"%'\n'.join(msg))
        return res


    def name_get(self):
        result = []
        for obj in self:
            if obj.type_document=='Article':
                name="[%s] %s"%(obj.dossier_article_id.code_pg,obj.param_project_id.ppr_famille)
            else:
                name="[%s] %s"%(obj.moule_dossierf,obj.param_project_id.ppr_famille)
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


    def actualisation_indicateur_action(self):
        for obj in self:
            if obj.date_fin_gantt:
                obj.dateend = obj.date_fin_gantt
            if not obj.etat:
                if obj.actuelle and obj.j_prevue:
                    if obj.j_prevue<=obj.actuelle:
                        obj.etat='AF'
            obj._compute_coefficient_bloquant_note()
            obj._compute_color()
            obj._compute_indicateur()
        return []






# TYPE_DOCUMENT=[
#     ("Moule"                 , "Moule"),
#     ("Dossier F"             , "Dossier F"),
#     ("Article"               , "Article"),
#     ("Dossier Modif Variante", "Dossier Modif Variante"),
#     ("dossier_appel_offre"   , "Dossier appel d'offre"),
# ]

#    idmoule          = fields.Many2one("is.mold"                  , string="Moule"    , tracking=True, index=True)
#     dossierf_id      = fields.Many2one("is.dossierf"              , string="Dossier F", tracking=True, index=True)
#     dossier_modif_variante_id = fields.Many2one("is.dossier.modif.variante", string="Dossier Modif / Variante", tracking=True)
#     dossier_article_id        = fields.Many2one("is.dossier.article"       , string="Dossier article", index=True, tracking=True)
#     dossier_appel_offre_id    = fields.Many2one("is.dossier.appel.offre"   , string="Dossier appel d'offre", tracking=True)


    def get_domain_type_document(self):
        for obj in self:
            domain=[]
            if obj.type_document=='Moule':
                if obj.idmoule.id:
                    domain=[('idmoule', '=', obj.idmoule.id)]
            if obj.type_document=='Dossier F':
                if obj.dossierf_id.id:
                    domain=[('dossierf_id', '=', obj.dossierf_id.id)]
            if obj.type_document=='Article':
                if obj.dossier_modif_variante_id.id:
                    domain=[('dossier_modif_variante_id', '=', obj.dossier_modif_variante_id.id)]
            if obj.type_document=='Dossier Modif Variante':
                if obj.dossier_article_id.id:
                    domain=[('dossier_article_id', '=', obj.dossier_article_id.id)]
            if obj.type_document=='dossier_appel_offre':
                if obj.dossier_appel_offre_id.id:
                    domain=[('dossier_appel_offre_id', '=', obj.dossier_appel_offre_id.id)]
            return domain


    def actualisation_champ_suivi_projet_action(self):
        nb=len(self)
        ct=1
        for obj in self:




            domain=obj.get_domain_type_document()
            if domain!=[]:
                domain.append(('param_project_id', '=', obj.param_project_id.id))
                docs=self.env['is.doc.moule'].search(domain,order='j_prevue')
                nb_doc = len(docs)

                _logger.info("actualisation_champ_suivi_projet_action : %s/%s : nb_doc=%s : %s : %s : %s"%(ct,nb,nb_doc,obj.moule_dossierf,obj.param_project_id.ppr_famille,obj.j_prevue))


                #** Initialisation à False de tous les documents **************
                res={}
                for doc in docs:
                    res[doc]=False

                #** Permet de savoir si un docuement répond aux criteres ******
                test=False

                #** Si un seul document, il est forcement actif ***************
                if nb_doc==1:
                    for doc in docs:
                        res[doc]=True
                        test=True

                #** True si 'A Faire' et le plus ancien <= j actuelle *********
                if not test:
                    for doc in docs:
                        if doc.j_prevue and doc.actuelle:
                            if doc.j_prevue<=doc.actuelle and doc.etat!='F':
                                res[doc]=True
                                test=True
                                break

               #** Recherche du dernier document <= j actuelle ***************
                if not test:
                    last_doc=False
                    for doc in docs:
                        if doc.j_prevue and doc.actuelle:
                            if doc.j_prevue<=doc.actuelle:
                                last_doc = doc
                    if last_doc:
                        res[last_doc]=True
                        test=True
                    
                #** Recherche du premier document > actuelle ******************
                if not test:
                    last_doc=False
                    for doc in docs:
                        if doc.j_prevue and doc.actuelle:
                            if doc.j_prevue>doc.actuelle:
                                res[doc]=True
                                test=True
                                break

                #** Mise à jour des documents *********************************
                for doc in docs:
                    doc.suivi_projet = res[doc]
            ct+=1
        return []


    def update_j_prevue_action(self):
        nb=len(self)
        ct=1
        for obj in self:
            j_actuelle = obj.idmoule.j_actuelle
            j_prevue = False
            if obj.dynacase_id and j_actuelle:
                for line in obj.param_project_id.array_ids:
                    if line.ppp_j<=j_actuelle and line.ppr_irv:
                        j_prevue=line.ppp_j
                if not j_prevue:
                    j_prevue=j_actuelle
                # if obj.etat=='F':
                #     for line in obj.param_project_id.array_ids:
                #         if line.ppp_j<=j_actuelle and line.ppr_irv:
                #             j_prevue=line.ppp_j
                #     if not j_prevue:
                #         j_prevue=j_actuelle
                # else:
                #     for line in obj.param_project_id.array_ids:
                #         if line.ppp_j>=j_actuelle and line.ppr_irv:
                #             j_prevue=line.ppp_j
                #             break
                #     if not j_prevue:
                #         j_prevue=j_actuelle
                obj.j_prevue = j_prevue
            ct+=1


    def get_pj(self,attachment_ids):
        res=False
        if attachment_ids:
            res=[]
            for pj in attachment_ids:
                res.append(pj.name)
            if len(res)>0:
                res='<br>'.join(res)
        return res


    def actualisation_famille_automatique_action(self):
        nb=len(self)
        ct=1
        for obj in self:
            if obj.ppr_type_demande=='AUTO':
                rsp_auto=False
                dao = obj.idmoule.dossier_appel_offre_id or obj.dossierf_id.dossier_appel_offre_id
                if dao:
                    if obj.param_project_id.ppr_famille=="Dossier commercial":
                        rsp_auto=obj.get_pj(dao.dao_offre_validee)
                    if obj.param_project_id.ppr_famille=="Commande client":
                        rsp_auto=obj.get_pj(dao.dao_commande_client)
                    if obj.param_project_id.ppr_famille=="Lettre de nomination et contrats":
                        rsp_auto=obj.get_pj(dao.dao_lettre_nomination)
                rc = obj.idmoule.revue_contrat_id or obj.dossierf_id.revue_contrat_id
                if rc:
                    if obj.param_project_id.ppr_famille=="Engagement de faisabilité":
                        rsp_auto=obj.get_pj(rc.rc_df_engagement_faisabilite)
                    if obj.param_project_id.ppr_famille=="Fiche capacitaire":
                        rsp_auto=obj.get_pj(rc.rc_df_fiche_capacitaire)
                if rsp_auto:
                    obj.etat='F'
                obj.rsp_auto = rsp_auto
                _logger.info("actualisation_famille_automatique_action : %s/%s : %s : rsp_auto=%s"%(ct,nb,obj.param_project_id.ppr_famille,rsp_auto))


            ct+=1
        return []



    # def write_task(self,start_date=False,duration=False,lier=False,mode=False):


    @api.onchange('date_debut_gantt','duree')
    def set_fin_gantt(self):
        for obj in self:
            if not self.env.context.get("noonchange"):
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
                    vals={
                        'duree_gantt'   : duree_gantt,
                        'date_fin_gantt': date_fin_gantt,
                    }
                    self.env.context = self.with_context(noonchange=True).env.context
                    obj.write(vals)






    @api.onchange('date_fin_gantt')
    def set_debut_gantt(self):
        for obj in self:
            if not self.env.context.get("noonchange"):
                if obj.date_fin_gantt and obj.duree:
                    duree_gantt = obj.duree
                    new_date = date_debut = date_fin = obj.date_fin_gantt - timedelta(days=1)
                    while True:
                        if not(new_date.weekday() in [5,6]):
                            duree_gantt=duree_gantt-1
                        if duree_gantt<=0:
                            date_debut=new_date - timedelta(days=1)
                            break
                        new_date = new_date - timedelta(days=1)
                    duree_gantt = (date_fin - date_debut).days 
                    date_debut_gantt = obj.date_fin_gantt - timedelta(days=duree_gantt)
                    vals={
                        'duree_gantt'     : duree_gantt,
                        'date_debut_gantt': date_debut_gantt,
                    }
                    self.env.context = self.with_context(noonchange=True).env.context
                    obj.write(vals)


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


    # def ok_action(self):
    #     for obj in self:
    #         obj.rsp_date = date.today()
    #         obj.etat='F'


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
                'default_date_fin_gantt': datetime.today(),
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
            'domain': domain,
            'type': 'ir.actions.act_window',
            "context": ctx,
            'limit': 1000,
        }
           
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


class IsDocMouleArray(models.Model):
    _name        = "is.doc.moule.array"
    _description = "Document moule array"

    annex         = fields.Many2many("ir.attachment", "attach_annex_rel"    , "annex_id"    , "attachment_id", string="Fichiers")
    annex_pdf     = fields.Many2many("ir.attachment", "attach_annex_pdf_rel", "annex_pdf_id", "attachment_id", string="Fichiers PDF", compute='_compute_annex_pdf', store=True, readonly=True)
    demandmodif   = fields.Char(string="Demande de modification")
    maj_amdec     = fields.Boolean(string="Mise à jour de l’AMDEC")
    comment       = fields.Text(string="Commentaire")
    is_doc_id     = fields.Many2one("is.doc.moule")
    lig           = fields.Integer(string="Lig",index=True,copy=False,readonly=True, help="Permet de faire le lien avec la ligne du tableau dans Dynacase")
    duree_convertion_pdf = fields.Float(string="Tps conversation en PDF (s)", digits=(12, 2), readonly=True)


    @api.depends('annex')
    def _compute_annex_pdf(self):
        data_dir = config['data_dir']
        db = self._cr.dbname
        for obj in self:
            start = time()
            if isinstance(obj.id, int) and obj.is_doc_id.param_project_id.ppr_transformation_pdf:
                obj.annex_pdf.unlink()
                annex_pdf=[]
                for attachment in obj.annex:
                    if attachment.store_fname:
                        tmp_dir = "/tmp/convert-to-pdf"
                        Path(tmp_dir).mkdir(parents=True, exist_ok=True)
                        src_path = "%s/filestore/%s/%s"%(data_dir,db,attachment.store_fname)
                        dst_path = '%s/%s'%(tmp_dir,attachment.name)                    
                        shutil.copy(src_path, dst_path)
                        if attachment.mimetype!='application/pdf':
                            cde = 'cd %s && libreoffice --convert-to pdf "%s" '%(tmp_dir,dst_path)
                            p = Popen(cde, shell=True, stdout=PIPE, stderr=PIPE)
                            stdout, stderr = p.communicate()
                            _logger.info("cde:%s, stdout:%s, stderr:%s"%(cde,stdout.decode("utf-8"),stderr.decode("utf-8")))
                            if stderr:
                                raise ValidationError("%s\n%s"%(cde,stderr.decode("utf-8")))
                        filename = Path(attachment.name)
                        name_pdf = filename.with_suffix('.pdf')
                        path_pdf = "%s/%s"%(tmp_dir,name_pdf)
                        datas = open(path_pdf,'rb').read()
                        vals = {
                            'name' : name_pdf,
                            'type' : 'binary',
                            'datas': base64.b64encode(datas),
                        }
                        attachment_pdf = self.env['ir.attachment'].create(vals)
                        annex_pdf.append(attachment_pdf.id)
                    obj.annex_pdf = annex_pdf
            duree = (time() - start)
            obj.duree_convertion_pdf=duree


class res_partner(models.Model):
    _inherit = 'res.partner'

    def gantt_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('client_id', '=', obj.id) ])
            ids=[]
            initial_date=str(datetime.today())
            for doc in docs:
                if str(doc.date_fin_gantt)<initial_date:
                    initial_date=str(doc.date_fin_gantt)
                ids.append(doc.id)
            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                'default_etat'          :'AF',
                'default_date_fin_gantt': datetime.today(),
                'default_idresp'        : self._uid,
                'initial_date'          : initial_date,
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
        