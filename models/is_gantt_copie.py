from odoo import models, fields, api, _
from odoo.addons.is_dynacase2odoo.models.is_param_project import TYPE_DOCUMENT, TYPE_TO_FIELD
from datetime import datetime, timedelta


class IsGanttCopieSection(models.Model):
    _name        = "is.gantt.copie.section"
    _description = "Sections Gantt Copie"

    gantt_copie_id = fields.Many2one('is.gantt.copie', 'Gantt Copie', required=True, ondelete='cascade')
    section_id     = fields.Many2one("is.section.gantt", string="Section", required=True)
    copier         = fields.Boolean("Copier", default=True)


class IsGanttCopie(models.Model):
    _name        = "is.gantt.copie"
    _description = "Gantt Copie"
    _order = "id desc"

    name                          = fields.Char("Document", compute='_compute_name',store=True, readonly=True)
    type_document                 = fields.Selection(TYPE_DOCUMENT,string="Type de document", default="Moule", required=True)
    src_idmoule                   = fields.Many2one("is.mold"                  , string="Moule à copier")
    src_dossierf_id               = fields.Many2one("is.dossierf"              , string="Dossier F à copier")
    src_dossier_modif_variante_id = fields.Many2one("is.dossier.modif.variante", string="Dossier Modif / Variante à copier")
    src_dossier_article_id        = fields.Many2one("is.dossier.article"       , string="Dossier article à copier")
    src_dossier_appel_offre_id    = fields.Many2one("is.dossier.appel.offre"   , string="Dossier appel d'offre à copier")
    dst_idmoule                   = fields.Many2one("is.mold"                  , string="Moule")
    dst_dossierf_id               = fields.Many2one("is.dossierf"              , string="Dossier F")
    dst_dossier_modif_variante_id = fields.Many2one("is.dossier.modif.variante", string="Dossier Modif / Variante")
    dst_dossier_article_id        = fields.Many2one("is.dossier.article"       , string="Dossier article")
    dst_dossier_appel_offre_id    = fields.Many2one("is.dossier.appel.offre"   , string="Dossier appel d'offre")
    date_debut                    = fields.Date("Date de début de la copie",required=True, default=fields.Date.context_today)
    src_nb_taches                 = fields.Integer("Nb tâches à copier"      , compute='_compute_nb_taches')
    dst_nb_taches                 = fields.Integer("Nb tâches actuellement", compute='_compute_nb_taches')
    section_ids                   = fields.One2many('is.gantt.copie.section', 'gantt_copie_id')


    @api.onchange('type_document','src_idmoule','src_dossierf_id','src_dossier_modif_variante_id','src_dossier_article_id','src_dossier_appel_offre_id')
    def onchange_dossier(self):
        for obj in self:
            sections=[]
            lines=[]
            for key in TYPE_TO_FIELD:
                if obj.type_document==key:
                    name_field = TYPE_TO_FIELD[key]
                    src_docs=obj.get_docs(name_field,prefix='src') or []     
                    for doc in src_docs:
                        section = doc.section_id
                        if section:
                            if section not in sections:
                                sections.append(section) 
                    for section in sections:
                        vals={
                            'section_id': section.id,
                        }
                        lines.append([0,0,vals])
            obj.section_ids = False
            obj.section_ids = lines


    def get_docs(self,name_field,prefix='src'):
        for obj in self:
            docs=False
            name =  '%s_%s'%(prefix,name_field)
            id = getattr(obj,name).id
            if id>0:
                domain = [(name_field, '=', id)]
                docs=self.env['is.doc.moule'].search(domain)
            return docs


    @api.depends('type_document', 'src_idmoule', 'src_dossierf_id', 'src_dossier_modif_variante_id', 'src_dossier_article_id', 'src_dossier_appel_offre_id', 'dst_idmoule', 'dst_dossierf_id', 'dst_dossier_modif_variante_id', 'dst_dossier_article_id', 'dst_dossier_appel_offre_id')
    def _compute_nb_taches(self):
        def get_nb_taches(name_field):
            res=[]
            for prefix in ('src','dst'):
                name =  '%s_%s'%(prefix,name_field)
                id = getattr(obj,name).id
                nb=0
                if id>0:
                    #domain = [(name_field, '=', id)]
                    #docs=self.env['is.doc.moule'].search(domain)
                    docs=obj.get_docs(name_field,prefix=prefix)
                    res.append(len(docs))
                else:
                    res.append(0)
            return res
        for obj in self:
            src_nb_taches = dst_nb_taches = 0
            for key in TYPE_TO_FIELD:
                if obj.type_document==key:
                    name_field = TYPE_TO_FIELD[key]
                    src_nb_taches, dst_nb_taches = get_nb_taches(name_field)
            obj.src_nb_taches = src_nb_taches
            obj.dst_nb_taches = dst_nb_taches


    @api.depends('type_document', 'dst_idmoule', 'dst_dossierf_id', 'dst_dossier_modif_variante_id', 'dst_dossier_article_id', 'dst_dossier_appel_offre_id')
    def _compute_name(self):
        for obj in self:
            name=""
            for key in TYPE_TO_FIELD:
                if obj.type_document==key:
                    name_field = 'dst_%s'%TYPE_TO_FIELD[key]
                    doc = getattr(obj,name_field)                
                    name = doc.name_get()[0][1]
            obj.name = name


    def generer_copie_action(self):
        for obj in self:
            section_ids=[]
            for line in obj.section_ids:
                if line.copier:
                    section_ids.append(line.section_id.id)


            for key in TYPE_TO_FIELD:
                if obj.type_document==key:
                    name_field = TYPE_TO_FIELD[key]
                    src_docs=obj.get_docs(name_field,prefix='src')
                    src2dst={}
                    for src_doc in src_docs:
                        if src_doc.section_id.id in section_ids:
                            dst_docs=obj.get_docs(name_field,prefix='dst')
                            #** Recherche si le doc a déja été copié **************
                            copie=False
                            for dst_doc in dst_docs:
                                if src_doc.id==dst_doc.origine_copie_id.id:
                                    copie=dst_doc
                                    break
                            #** Recherche un doc avec la même famille **************
                            if not copie:
                                for dst_doc in dst_docs:
                                    if src_doc.param_project_id==dst_doc.param_project_id and not dst_doc.origine_copie_id.id:
                                        copie=dst_doc
                                        break
                            #** Création du doc si non trouvé avant ***************
                            if not copie:
                                copie=src_doc.copy()
                                copie.idresp = src_doc.idresp.id
                                dst_name_field =  'dst_%s'%name_field
                                dst_dossier_id = getattr(obj,dst_name_field).id
                                setattr(copie, name_field, dst_dossier_id)


                            vals={
                                'section_id'      : src_doc.section_id.id,
                                'sequence'        : src_doc.sequence,
                                'param_project_id': src_doc.param_project_id.id,
                                'type_document'   : src_doc.type_document,
                                #'idresp'          : src_doc.idresp, Pour les doc venant de Dynacase ne pas changer le responsable
                                'demande'         : src_doc.demande,
                                'dateend'         : src_doc.dateend,
                                'duree'           : src_doc.duree,
                                'duree_gantt'     : src_doc.duree_gantt,
                                'date_debut_gantt': src_doc.date_debut_gantt,
                                'date_fin_gantt'  : src_doc.date_fin_gantt,
                                'origine_copie_id': src_doc.id,
                                'dependance_id'   : src_doc.dependance_id.id,
                            }
                            copie.write(vals)
                            copie._compute_idproject_moule_dossierf()
                            src2dst[src_doc]=copie

                    #** Recherche des copies des dépendances ******************
                    dst_docs=obj.get_docs(name_field,prefix='dst')
                    for dst_doc in dst_docs:
                        if dst_doc.dependance_id.id:
                            if dst_doc.dependance_id in src2dst:
                                dst_doc.dependance_id = src2dst[dst_doc.dependance_id].id

                    #** Calage du Gantt sur date_debut ************************
                    for dst_doc in dst_docs:
                        start_date = str(obj.date_debut -timedelta(days=1))
                        dst_doc.write_task(start_date=start_date, duration=dst_doc.duree, lier=True)


                        #delta = (obj.date_debut - dst_doc.date_debut_gantt).days
                        #dst_doc.date_debut_gantt = obj.date_debut
                        #dst_doc.move_task_lier(delta)
                        break

            if obj.type_document=='Moule':
                if obj.dst_idmoule.revue_lancement_id:
                    obj.dst_idmoule.revue_lancement_id.initialiser_responsable_doc_action()
