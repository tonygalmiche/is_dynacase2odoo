# -*- coding: utf-8 -*-
from odoo import models, fields, api  # type: ignore


class IsProcessus(models.Model):
    _name = 'is.processus'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = 'Processus'
    _order = "numpcs"
    _rec_name = 'numpcs'



    active       = fields.Boolean(string="Actif", default=True, tracking=True)
    dynacase_id  = fields.Integer(string="Id Dynacase", index=True, copy=False)

    # Identification
    numpcs       = fields.Char(string="Numéro du processus", required=False, tracking=True)
    numindice    = fields.Char(string="Indice", required=False, tracking=True)
    nom          = fields.Char(string="Nom du processus", required=False, tracking=True)
    pilotepcs_id = fields.Many2one('res.users', 'Pilote du processus', required=False, default=lambda self: self.env.uid, tracking=True)
    niveau       = fields.Char(string="Niveau", tracking=True)
    exigence     = fields.Char(string="Liste des exigences", tracking=True)

    # Informations textuelles
    element       = fields.Text(string="Éléments déclencheurs", tracking=True)
    donneesentree = fields.Text(string="Données d'entrée", tracking=True)
    donneessortie = fields.Text(string="Données de sortie", tracking=True)
    finalite      = fields.Text(string="Finalité", tracking=True)
    efficience    = fields.Text(string="Efficience", tracking=True)
    efficacite    = fields.Text(string="Efficacité", tracking=True)

    # Cycle (qui vérifie / qui approuve / diffusion)
    quiverifie_id  = fields.Many2one('res.users', 'Qui vérifie', tracking=True)
    quiapprouve_id = fields.Many2one('res.users', 'Qui approuve', tracking=True)
    diffusion      = fields.Char(string="Diffusion", tracking=True)

    # Étapes du processus
    etape_ids = fields.One2many('is.processus.etape', 'processus_id', string="Étapes du processus", tracking=True)
    
    # Documents du processus
    doc_ids = fields.One2many('is.processus.doc', 'processus_id', string="Documents du processus", readonly=True)

    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }




class IsProcessusEtape(models.Model):
    _name = 'is.processus.etape'
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = 'Étapes des processus'
    _order = "processus_id, numetape"
    _rec_name = 'numetape'

    processus_id      = fields.Many2one('is.processus', string="Processus", required=True, tracking=True)    
    pilote_id         = fields.Many2one(related="processus_id.pilotepcs_id")
    numetape          = fields.Char(string="N°", tracking=True)
    description       = fields.Text(string="Description", tracking=True)
    responsable       = fields.Char(string="Responsable", tracking=True)
    sous_processus_id = fields.Many2one('is.processus', string="Sous-processus", tracking=True)
    active            = fields.Boolean(string="Actif", default=True, tracking=True)
    dynacase_id       = fields.Integer(string="Id Dynacase", index=True, copy=False)
    doc_ids           = fields.One2many('is.processus.doc', 'etape_id', string="Documents", readonly=True)


    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


class IsProcessusDoc(models.Model):
    _name = 'is.processus.doc'
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = 'Documents des processus'
    _order = "processus_id, reference"
    _rec_name = 'reference'


    # Identification (frame dpcs_fr_pcs)
    processus_id = fields.Many2one('is.processus', string="Processus", tracking=True)
    etape_id     = fields.Many2one('is.processus.etape', string="Étape", tracking=True)
    procedure_id = fields.Many2one('is.processus.doc', string="Procédure", tracking=True)
    pilote_id    = fields.Many2one(related="processus_id.pilotepcs_id")

    # Identification (frame dpcs_ident)
    reference    = fields.Char(string="Référence", tracking=True)
    designation  = fields.Char(string="Désignation", tracking=True)
    site_id      = fields.Many2one('is.database', "Site", tracking=True, default=lambda self: self._get_site_id(),)
    niveau       = fields.Char(string="Niveau", tracking=True)
    version      = fields.Char(string="Version", tracking=True)
    modification = fields.Char(string="Modification", tracking=True)
    auteur_id    = fields.Many2one('res.users', string="Auteur", tracking=True)
    dossier      = fields.Char(string="Dossier (Processus)", tracking=True)
    piece_jointe_ids = fields.Many2many("ir.attachment", "is_processus_doc_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")

    # Organisation (Pour les FO) - frame dpcs_fo
    quiremplit_id  = fields.Many2one('res.users', string="Qui remplit", tracking=True)
    quiclasse_id   = fields.Many2one('res.users', string="Qui classe", tracking=True)
    lieuclassement = fields.Char(string="Lieu classement", tracking=True)
    quiarchive_id  = fields.Many2one('res.users', string="Qui archive", tracking=True)
    lieuarchive    = fields.Char(string="Lieu archive", tracking=True)
    reglerange     = fields.Char(string="Règle de rangement", tracking=True)
    dureecons      = fields.Char(string="Durée de conservation", tracking=True)
    quidetruit_id  = fields.Many2one('res.users', string="Qui détruit", tracking=True)

    # Diffusion (Pour les autres documents) - frame dpcs_autre
    quiverifie_id  = fields.Many2one('res.users', string="Qui vérifie", tracking=True)
    quiapprouve_id = fields.Many2one('res.users', string="Qui approuve", tracking=True)
    diffusion      = fields.Char(string="Diffusion", tracking=True)

    # Contenu du document - Étapes (array dpcs_array1)
    etape_doc_ids   = fields.One2many('is.processus.doc.etape', 'doc_id', string="Étapes du document")
    etape_doc_texte = fields.Text(string="Étapes (texte)", compute='_compute_etape_doc_texte', store=True, tracking=True)

    active      = fields.Boolean(string="Actif", default=True, tracking=True)
    dynacase_id = fields.Integer(string="Id Dynacase", index=True, copy=False)

    def _get_site_id(self):
        user = self.env['res.users'].browse(self._uid)
        site_id = user.is_site_id.id
        return site_id

    @api.depends('etape_doc_ids', 'etape_doc_ids.numeroetape', 'etape_doc_ids.nometape', 
                 'etape_doc_ids.responsable_id', 'etape_doc_ids.description', 'etape_doc_ids.doclibre')
    def _compute_etape_doc_texte(self):
        for record in self:
            if record.etape_doc_ids:
                lines = []
                for etape in record.etape_doc_ids.sorted('numeroetape'):
                    num = str(etape.numeroetape or '')
                    nom = str(etape.nometape or '')
                    resp = str(etape.responsable_id.name if etape.responsable_id else '')
                    desc = str(etape.description or '')
                    doc = str(etape.doclibre or '')
                    lines.append(f"■ {num} | {nom} | {resp} | {desc} | {doc}")
                record.etape_doc_texte = ", ".join(lines)
            else:
                record.etape_doc_texte = "Aucune étape définie"

    def action_view_document(self):
        """Ouvre la fiche complète du document du processus"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Document du processus',
            'res_model': 'is.processus.doc',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


class IsProcessusDocEtape(models.Model):
    _name = 'is.processus.doc.etape'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Étapes des documents des processus'
    _order = "doc_id, numeroetape"
    _rec_name = 'nometape'

    doc_id         = fields.Many2one('is.processus.doc', string="Document", required=True, tracking=True)
    numeroetape    = fields.Integer(string="Numéro étape", tracking=True)
    nometape       = fields.Char(string="Nom de l'étape", tracking=True)
    responsable_id = fields.Many2one('res.users', string="Responsable", tracking=True)
    description    = fields.Text(string="Description", tracking=True)
    doclibre       = fields.Text(string="Document libre", tracking=True)


    def open_etape_doc(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Étape du document',
            'res_model': 'is.processus.doc.etape',
            'view_mode': 'form',
            'res_id': self.id,
            # 'target': 'new',
        }
    
