# -*- coding: utf-8 -*-
from odoo import models, fields, api  # type: ignore
from odoo.exceptions import UserError  # type: ignore
import base64
import logging
import time
_logger = logging.getLogger(__name__)

class is_dossier_article(models.Model):
    _inherit = 'is.dossier.article'

    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)
    doc_ids     = fields.One2many('is.dossier.article.doc', 'dossier_id')
    nb_a_faire  = fields.Integer(string="Nb doc à faire", compute='_compute_fait',store=True,readonly=True)
    nb_crees    = fields.Integer(string="Nb doc créés"  , compute='_compute_fait',store=True,readonly=True)
    nb_fait     = fields.Integer(string="Nb doc fait"   , compute='_compute_fait',store=True,readonly=True)
    site_ids    = fields.Many2many('is.database', string="Sites", readonly=True)
    has_prompt_ia = fields.Boolean(string="Prompts IA disponibles", compute='_compute_has_prompt_ia')
    analyse_ia_ids = fields.One2many('is.analyse.ia.ligne', 'dossier_article_id', string="Résultats analyse IA")


    @api.depends('doc_ids', 'doc_ids.doc_id', 'doc_ids.piecejointe')
    def _compute_fait(self):
        for obj in self:
            nb_a_faire = nb_crees = nb_fait = 0
            for line in obj.doc_ids:
                nb_a_faire+=1
                if line.doc_id:
                    nb_crees+=1
                if line.piecejointe:
                    nb_fait+=1
            obj.nb_a_faire = nb_a_faire
            obj.nb_crees   = nb_crees
            obj.nb_fait    = nb_fait


    def _compute_has_prompt_ia(self):
        model_id = self.env['ir.model']._get_id('is.dossier.article')
        count = self.env['is.prompt.ia'].sudo().search_count([('modele_id', '=', model_id)])
        for obj in self:
            obj.has_prompt_ia = count > 0


    def analyse_ia_action(self):
        """Analyse IA : récupérer les PJ des familles puis envoyer les prompts à l'IA"""
        self.ensure_one()

        # 1. Rechercher les prompts pour ce modèle
        model_id = self.env['ir.model']._get_id('is.dossier.article')
        prompts = self.env['is.prompt.ia'].sudo().search([('modele_id', '=', model_id)])
        if not prompts:
            raise UserError("Aucun prompt IA configuré pour le modèle 'Dossier article'.")

        # 2. Collecter toutes les familles référencées dans les prompts
        familles = prompts.mapped('famille_ids')
        if not familles:
            raise UserError("Aucune famille configurée dans les prompts IA.")

        # 3. Rechercher les documents liés à ce dossier article pour ces familles
        docs = self.env['is.doc.moule'].search([
            ('dossier_article_id', '=', self.id),
            ('param_project_id', 'in', familles.ids),
        ])
        if not docs:
            raise UserError("Aucun document trouvé pour les familles configurées dans les prompts IA.")

        # 4. Extraire les pièces jointes (images et PDF→images)
        images = []
        for doc in docs:
            for line in doc.array_ids:
                for attachment in line.annex:
                    mimetype = attachment.mimetype or ''
                    if not attachment.datas:
                        continue
                    if mimetype in ('image/jpeg', 'image/png', 'image/gif', 'image/webp'):
                        img_b64 = attachment.datas.decode('utf-8') if isinstance(attachment.datas, bytes) else attachment.datas
                        images.append((img_b64, mimetype))
                    elif mimetype == 'application/pdf':
                        pdf_data = base64.b64decode(attachment.datas)
                        pages_b64 = self.env['is.vllm']._pdf_to_base64_images(pdf_data)
                        for page_b64 in pages_b64:
                            images.append((page_b64, 'image/jpeg'))

        if not images:
            raise UserError("Aucune pièce jointe trouvée dans les documents des familles configurées.")

        # 5. Supprimer les anciennes lignes d'analyse
        self.analyse_ia_ids.unlink()

        # 6. Pour chaque prompt, envoyer la demande à l'IA
        lignes_vals = []
        result_map = {}
        for prompt_rec in prompts:
            # Compléter le prompt avec les contraintes du type de champ
            prompt_complet = prompt_rec.prompt or ''
            if prompt_rec.field_id:
                field_meta = self._fields.get(prompt_rec.field_id.name)
                if field_meta:
                    ttype = field_meta.type
                    if ttype == 'integer':
                        prompt_complet += "\n\nLa réponse doit être un nombre entier uniquement (sans texte, sans unité)."
                    elif ttype == 'float':
                        prompt_complet += "\n\nLa réponse doit être un nombre décimal uniquement (utiliser le point comme séparateur décimal, sans texte, sans unité)."
                    elif ttype == 'date':
                        prompt_complet += "\n\nLa réponse doit être une date au format AAAA-MM-JJ uniquement."
                    elif ttype == 'datetime':
                        prompt_complet += "\n\nLa réponse doit être une date et heure au format AAAA-MM-JJ HH:MM:SS uniquement."
                    elif ttype == 'boolean':
                        prompt_complet += "\n\nLa réponse doit être uniquement 'True' ou 'False'."
                    elif ttype == 'selection':
                        selection_list = field_meta.selection
                        if callable(selection_list):
                            try:
                                selection_list = selection_list(self)
                            except Exception:
                                selection_list = []
                        if selection_list:
                            choix = ', '.join("'%s' (%s)" % (k, v) for k, v in selection_list)
                            prompt_complet += "\n\nLa réponse doit être exactement une des valeurs suivantes (donner uniquement la clé, sans les parenthèses) : %s" % choix
                    elif ttype == 'many2one':
                        comodel = field_meta.comodel_name
                        if comodel:
                            records = self.env[comodel].sudo().search([], limit=300)
                            if records:
                                choix = ', '.join("'%s' (id=%s)" % (rec.display_name, rec.id) for rec in records)
                                prompt_complet += "\n\nLa réponse doit être exactement l'id numérique d'un de ces choix : %s" % choix
            # Calculer la taille des données envoyées (prompt + images) en Mo
            taille_prompt = len(prompt_complet.encode('utf-8'))
            taille_images = sum(len(img_b64.encode('utf-8') if isinstance(img_b64, str) else img_b64) for img_b64, _ in images)
            taille_envoi = round((taille_prompt + taille_images) / (1024 * 1024), 2)

            t0 = time.time()
            result = self.env['is.vllm'].vllm_send_prompt(
                prompt_complet,
                images_b64=images,
            )
            duree = round(time.time() - t0, 1)
            reponse = ""
            success = result.get('success', False)
            if success:
                reponse = result.get('response', '')
            else:
                reponse = "Erreur : %s" % result.get('error', 'Erreur inconnue')

            result_map[prompt_rec.id] = {'success': success, 'response': reponse}

            lignes_vals.append({
                'dossier_article_id': self.id,
                'prompt_ia_id'      : prompt_rec.id,
                'field_id'          : prompt_rec.field_id.id,
                'prompt'            : prompt_complet,
                'reponse'           : reponse,
                'temps_traitement'  : duree,
                'taille_envoi'      : taille_envoi,
            })

        self.env['is.analyse.ia.ligne'].create(lignes_vals)

        # 7. Mettre à jour les champs du dossier article avec les réponses
        for prompt_rec in prompts:
            if prompt_rec.field_id and result_map.get(prompt_rec.id, {}).get('success'):
                field_name = prompt_rec.field_id.name
                if field_name in self._fields:
                    reponse = result_map[prompt_rec.id]['response'].strip()
                    field_meta = self._fields[field_name]
                    ttype = field_meta.type
                    try:
                        # Convertir la réponse selon le type du champ
                        if ttype == 'integer':
                            import re
                            match = re.search(r'-?\d+', reponse)
                            val = int(match.group()) if match else int(reponse)
                            self.write({field_name: val})
                        elif ttype == 'float':
                            import re
                            match = re.search(r'-?\d+\.?\d*', reponse)
                            val = float(match.group()) if match else float(reponse)
                            self.write({field_name: val})
                        elif ttype == 'boolean':
                            val = reponse.lower() in ('true', '1', 'oui', 'yes')
                            self.write({field_name: val})
                        elif ttype == 'many2one':
                            import re
                            match = re.search(r'\d+', reponse)
                            if match:
                                rec_id = int(match.group())
                                comodel = field_meta.comodel_name
                                if self.env[comodel].sudo().browse(rec_id).exists():
                                    self.write({field_name: rec_id})
                                else:
                                    raise ValueError("Id %s non trouvé dans %s" % (rec_id, comodel))
                            else:
                                raise ValueError("Aucun id trouvé dans la réponse : %s" % reponse)
                        else:
                            self.write({field_name: reponse})
                        # Mettre à jour l'état de la ligne
                        ligne = self.analyse_ia_ids.filtered(lambda l: l.prompt_ia_id.id == prompt_rec.id)
                        if ligne:
                            ligne.etat = 'OK'
                    except Exception as e:
                        _logger.warning("Impossible d'écrire la réponse IA dans le champ %s : %s", field_name, str(e))
                        ligne = self.analyse_ia_ids.filtered(lambda l: l.prompt_ia_id.id == prompt_rec.id)
                        if ligne:
                            ligne.etat = "Erreur : %s" % str(e)


    @api.depends('code_pg')
    def _compute_gestionnaire(self):
        for obj in self:
            gestionnaire = False
            if obj.code_pg:
                # Recherche dans is.article avec code_pg = name
                article = self.env['is.article'].search([('name', '=', obj.code_pg)], limit=1)
                if article:
                    gestionnaire = article.gestionnaire or ""
            obj.gestionnaire = gestionnaire


    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


    def initialiser_documents_dossier_article_action(self):
        for obj in self:
            domain=[
                ('type_document', '=', 'Article'),
            ]
            if obj.type_dossier=='matiere':
                domain.append(('dossier_matiere', '=', True))
            if obj.type_dossier=='colorant':
                domain.append(('dossier_colorant', '=', True))
            if obj.type_dossier=='composant':
                domain.append(('dossier_composant', '=', True))
            familles=self.env['is.param.project'].sudo().search(domain)
            for famille in familles:
                line_id=False
                for line in obj.doc_ids:
                    if line.param_project_id==famille:
                        line_id=line
                        break
                if not line_id:
                    vals={
                        'dossier_id'      : obj.id,
                        'param_project_id': famille.id,
                    }
                    line_id = self.env['is.dossier.article.doc'].sudo().create(vals)

                #** Recherche des docuements pour cette famille ***************
                domain=[
                    ('param_project_id'  , '=', famille.id),
                    ('dossier_article_id', '=', obj.id),
                ]
                docs=self.env['is.doc.moule'].search(domain)
                for doc in docs:
                    line_id.doc_id = doc.id
                    line_id.piecejointe = doc.rsp_pj
                #**************************************************************
            obj._compute_fait()
        return []


    def actualiser_site_ids_action(self):
        """Méthode appelée par le cron pour renseigner le champ site_ids"""
        dossiers = self.env['is.dossier.article'].search([])
        dossiers_avec_code = dossiers.filtered(lambda d: d.code_pg)
        total = len(dossiers_avec_code)
        compteur = 0
        gestionnaires_exclus = ['04', '07', '12', '14']
        for dossier in dossiers_avec_code:
            compteur += 1
            # Recherche de tous les articles avec code_pg = name, en excluant les gestionnaires 04, 07, 12 et 14
            articles = self.env['is.article'].search([
                ('name', '=', dossier.code_pg),
                ('gestionnaire', 'not in', gestionnaires_exclus)
            ])
            if articles:
                # Récupération des sites (database_id) de tous les articles trouvés
                sites = articles.mapped('database_id')
                _logger.info("%s/%s - Code PG: %s - Sites: %s", compteur, total, dossier.code_pg, ', '.join(sites.mapped('name')) or 'Aucun')
                dossier.site_ids = [(6, 0, sites.ids)]
        return True


class is_dossier_article_doc(models.Model):
    _name        = "is.dossier.article.doc"
    _description = "Documents du dossier article"
    _order       = 'param_project_id'

    dossier_id       = fields.Many2one("is.dossier.article", string="Dossier article", required=True, ondelete='cascade')
    param_project_id = fields.Many2one("is.param.project", string="Famille de document", required=True)
    doc_id           = fields.Many2one("is.doc.moule", string="Document")
    piecejointe      = fields.Text(string="Pièce jointe", compute='_compute_piecejointe',store=True,readonly=True)


    @api.depends('doc_id', 'doc_id.rsp_pj')
    def _compute_piecejointe(self):
        for obj in self:
            obj.piecejointe = obj.doc_id.rsp_pj


    def creer_doc_action(self):
        for obj in self:
            vals={
                'type_document'     : 'Article',
                'dossier_article_id': obj.dossier_id.id,
                'param_project_id'  : obj.param_project_id.id,
                'idresp'            : self._uid,
            }
            doc = self.env['is.doc.moule'].create(vals)
            obj.doc_id = doc.id


class IsAnalyseIaLigne(models.Model):
    _name        = "is.analyse.ia.ligne"
    _description = "Ligne d'analyse IA"
    _order       = 'id'

    dossier_article_id = fields.Many2one("is.dossier.article", string="Dossier article", required=True, ondelete='cascade')
    prompt_ia_id       = fields.Many2one("is.prompt.ia", string="Prompt IA")
    field_id           = fields.Many2one("ir.model.fields", string="Champ")
    prompt             = fields.Text(string="Prompt envoyé")
    reponse            = fields.Text(string="Réponse IA")
    temps_traitement   = fields.Float(string="Temps (s)", digits=(10, 1))
    taille_envoi       = fields.Float(string="Taille envoi (Mo)", digits=(10, 2))
    etat               = fields.Char(string="État")
