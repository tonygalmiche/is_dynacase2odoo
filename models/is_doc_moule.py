# -*- coding: utf-8 -*-
from odoo import models, fields, api, _                              # type: ignore
from odoo.tools import format_date, formatLang, frozendict           # type: ignore
from odoo.exceptions import AccessError, ValidationError, UserError  # type: ignore
from datetime import datetime, timedelta, date
from random import *
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J, TYPE_DOCUMENT, MODELE_TO_TYPE, TYPE_TO_FIELD, DOCUMENT_ACTION, DOCUMENT_ETAT # type: ignore


class IsDocMoule(models.Model):
    _name        = "is.doc.moule"
    _inherit=['mail.thread']
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


    type_document = fields.Selection(TYPE_DOCUMENT,string="Type de document", default="Moule", required=True, tracking=True)
    sequence = fields.Integer(string="Ordre", tracking=True, copy=False)
    project_prev     = fields.Html(compute='_compute_project_prev', store=True)
    project_prev2    = fields.Html()
    param_project_id = fields.Many2one("is.param.project", string="Famille de document", tracking=True, index=True)
    param_project_array_html = fields.Html(related="param_project_id.array_html")
    ppr_type_demande = fields.Selection(related="param_project_id.ppr_type_demande")
    ppr_icon         = fields.Image(related="param_project_id.ppr_icon", string="Icône", store=True)
    ppr_color        = fields.Char(related="param_project_id.ppr_color", string="Color", store=True)
    idmoule          = fields.Many2one("is.mold"                  , string="Moule"    , tracking=True, index=True)
    dossierf_id      = fields.Many2one("is.dossierf"              , string="Dossier F", tracking=True, index=True)
    dossier_modif_variante_id = fields.Many2one("is.dossier.modif.variante", string="Dossier Modif / Variante", tracking=True)
    dossier_article_id        = fields.Many2one("is.dossier.article"       , string="Dossier article", tracking=True)
    dossier_appel_offre_id    = fields.Many2one("is.dossier.appel.offre"   , string="Dossier appel d'offre", tracking=True)
    moule_dossierf   = fields.Char("Moule / Dossier F"                   , compute='_compute_idproject_moule_dossierf',store=True, readonly=True)
    idproject        = fields.Many2one("is.mold.project", string="Projet", compute='_compute_idproject_moule_dossierf',store=True, readonly=True)
    client_id        = fields.Many2one("res.partner", string="Client"    , compute='_compute_idproject_moule_dossierf',store=True, readonly=True)
    idcp             = fields.Many2one(related="idmoule.chef_projet_id", string="CP", tracking=True)
    idresp           = fields.Many2one("res.users", string="Responsable", tracking=True)
    j_prevue         = fields.Selection(GESTION_J, string="J Prévue", tracking=True)
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
    dateend             = fields.Date(string="Date de fin", tracking=True)
    array_ids           = fields.One2many("is.doc.moule.array", "is_doc_id", string="Pièce-jointe de réponse à la demande")
    dynacase_id         = fields.Integer(string="Id Dynacase",index=True,copy=False)
    duree               = fields.Integer(string="Durée (J)"      , help="Durée en jours ouvrés"         , default=1, tracking=True)
    duree_gantt         = fields.Integer(string="Durée Gantt (J)", help="Durée calendaire pour le Gantt", default=1, tracking=True, readonly=True)
    duree_attente_avant = fields.Integer("Durée attente avant (J)", help="Utilisée dans le Gantt")
    date_debut_gantt    = fields.Date(string="Date début Gantt", default=lambda self: self._date_debut_gantt(), tracking=True)
    date_fin_gantt      = fields.Date(string="Date fin Gantt", readonly=True, tracking=True)
    section_id          = fields.Many2one("is.section.gantt", string="Section Gantt",index=True, tracking=True, copy=False)
    gantt_pdf           = fields.Boolean("Gantt PDF", default=True, help="Afficher dans Gantt PDF")
    dependance_id       = fields.Many2one("is.doc.moule", string="Dépendance",index=True, tracking=True, copy=False)
    origine_copie_id    = fields.Many2one("is.doc.moule", string="Origine de la copie",index=True, copy=False)
    active              = fields.Boolean('Actif', default=True, tracking=True)
    site_id             = fields.Many2one('is.database', "Site", compute='_compute_site_id', readonly=True, store=True)
    demao_nature        = fields.Char(string="Nature", compute='_compute_demao_nature'     , readonly=True, store=True)
    solde               = fields.Boolean(string="Soldé", compute='_compute_solde'          , readonly=True, store=True)
    rsp_date            = fields.Date(string="Date réponse", copy=False)
    rsp_texte           = fields.Text(string="Texte réponse", copy=False)
    rsp_pj              = fields.Text(string="Réponse PJ", compute='_compute_rsp_pj', readonly=True, store=True)
    acces_chef_projet   = fields.Boolean(string="Accès chef de projet", compute='_compute_acces_chef_projet', readonly=True, store=False, help="Indique si les champs réservés au chef de projet sont modifiables")
    color               = fields.Char(string="Couleur indicateur", compute='_compute_color', readonly=True, store=True)


    @api.onchange('etat')
    def onchange_etat(self):
        for obj in self:
            type_demande = obj.param_project_id.ppr_type_demande
            if type_demande in ['DATE','PJ_DATE']:
                if obj.etat=='F':
                    obj.rsp_date = date.today()
                else:
                    obj.rsp_date=False


    # @api.depends('param_project_id')
    # def _compute_rsp_date_vsb(self):
    #     for obj in self:
    #         vsb=False
    #         if obj.ppr_type_demande in ('DATE','PJ_DATE'):
    #             vsb=True
    #         obj.rsp_date_vsb=vsb


#    ppr_type_demande        = fields.Selection([
#         ("PJ",       "Pièce-jointe"),
#         ("DATE",     "Date"),
#         ("TEXTE",    "Texte"),
#         ("PJ_TEXTE", "Pièce-jointe et texte"),
#         ("PJ_DATE",  "Pièce-jointe et date"),
#         ("AUTO",     "Automatique"),
#     ], string="Type de demande", required=True, default='PJ')



    @api.depends('etat','dateend')
    def _compute_color(self):
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
            obj.color=color


    @api.depends('etat','array_ids.annex','array_ids.comment')
    def _compute_rsp_pj(self):
        for obj in self:
            rsp_pj=False
            for line in obj.array_ids:
                if line.comment:
                    rsp_pj=line.comment
                if line.annex:
                    for pj in line.annex:
                        rsp_pj=pj.name
                break
            obj.rsp_pj = rsp_pj


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


    @api.depends('note','coefficient','etat','action','array_ids.annex','rsp_date','rsp_texte')
    def _compute_indicateur(self):
        for obj in self:
            color = obj.color
            ladate = '(date)'
            if obj.dateend:
                ladate = obj.dateend.strftime('%d/%m/%Y')
            lanote=""
            if obj.coefficient>0:
                lanote = "%s/%s"%(obj.note,obj.coefficient)
            reponses=obj.get_doc_reponse()
            html="""
                <div style='background-color:"""+color+"""'>
                    <table style="border-collapse:collapse;width:100%">
                        <tr>
                            <td style="border:none;text-align:center;white-space:nowrap;" colspan="2">
                                <span>"""+ladate+"""</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="width:50%;border:none;text-align:left;white-space:nowrap;padding-left:0.5rem">
                                <span>"""+lanote+"""</span>
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
        res=super(IsDocMoule, self).write(vals)
        if 'etat' in vals:
            if vals['etat']=='F':
                reponses=self.get_doc_reponse()
                if not reponses[0] and not reponses[1] and not reponses[2] and self.ppr_type_demande!='AUTO':
                    raise ValidationError("Impossbile de passer à l'état 'Fait' car aucune réponse n'est fournie !")
        if not self.acces_chef_projet:
            champs_interdit=[
                'section_id',
                'param_project_id',
                'idresp',
                'dateend',
                'date_debut_gantt',
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
                    champ = self._fields[key].string
                    msg.append("- %s"%champ)
            if len(msg)>0:
                raise ValidationError("Modification non autorisée pour les champs :\n%s"%'\n'.join(msg))
        return res


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
        