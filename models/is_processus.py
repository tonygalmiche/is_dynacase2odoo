# -*- coding: utf-8 -*-
from odoo import models, fields, api  # type: ignore
from odoo.exceptions import ValidationError


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

    # Champ calculé pour la visibilité du bouton de création de document
    can_create_document = fields.Boolean(string="Peut créer un document", compute='_compute_can_create_document')

    @api.depends('pilotepcs_id')
    def _compute_can_create_document(self):
        """Détermine si l'utilisateur courant peut créer un document pour ce processus"""
        for record in self:
            # Vérifier si l'utilisateur est le pilote du processus
            is_pilote = record.pilotepcs_id and record.pilotepcs_id.id == self.env.uid
            # Vérifier si l'utilisateur est dans le groupe gestionnaire
            is_gestionnaire = self.env.user.has_group('is_dynacase2odoo.is_gestionnaire_processus_group')
            record.can_create_document = is_pilote or is_gestionnaire

    def action_create_document(self):
        """Ouvre le formulaire de création d'un document lié à ce processus"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Créer un document',
            'res_model': 'is.processus.doc',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_processus_id': self.id,
            }
        }

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

    # Champ calculé pour la visibilité du bouton de création de document
    can_create_document = fields.Boolean(string="Peut créer un document", compute='_compute_can_create_document')

    @api.depends('pilote_id')
    def _compute_can_create_document(self):
        """Détermine si l'utilisateur courant peut créer un document pour cette étape"""
        for record in self:
            # Vérifier si l'utilisateur est le pilote du processus
            is_pilote = record.pilote_id and record.pilote_id.id == self.env.uid
            # Vérifier si l'utilisateur est dans le groupe gestionnaire
            is_gestionnaire = self.env.user.has_group('is_dynacase2odoo.is_gestionnaire_processus_group')
            record.can_create_document = is_pilote or is_gestionnaire

    def action_create_document(self):
        """Ouvre le formulaire de création d'un document lié à cette étape"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Créer un document',
            'res_model': 'is.processus.doc',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_etape_id': self.id,
                'default_processus_id': self.processus_id.id,
            }
        }

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
    _order = "reference"
    _rec_name = 'reference'


    @api.depends('processus_id', 'processus_id.pilotepcs_id')
    def _compute_pilote_id(self):
        for obj in self:
            pilote_id = False
            if obj.processus_id and obj.processus_id.pilotepcs_id:
                pilote_id = obj.processus_id.pilotepcs_id.id
            obj.pilote_id = pilote_id


    # Identification (frame dpcs_fr_pcs)
    processus_id = fields.Many2one('is.processus', string="Processus", tracking=True)
    etape_id     = fields.Many2one('is.processus.etape', string="Étape", tracking=True)
    procedure_id = fields.Many2one('is.processus.doc', string="Procédure", tracking=True)
    pilote_id    = fields.Many2one('res.users', 'Pilote du processus', compute='_compute_pilote_id', store=True, readonly=True, tracking=True)


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
    piece_jointe_noms = fields.Text(string="Liste des pièces jointes", compute='_compute_piece_jointe_noms', store=True, tracking=True)

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

    doc_ids = fields.One2many('is.processus.doc', 'procedure_id', string="Documents", readonly=True)

    # Champ pour le motif de révision
    motif_revision = fields.Text(string="Motif de révision", readonly=True, tracking=True)

    active      = fields.Boolean(string="Actif", default=True, tracking=True)
    dynacase_id = fields.Integer(string="Id Dynacase", index=True, copy=False)

    # Champ calculé pour déterminer si les champs doivent être en lecture seule
    is_readonly = fields.Boolean(string="Lecture seule", compute='_compute_is_readonly')

    @api.depends('pilote_id')
    def _compute_is_readonly(self):
        """Détermine si les champs doivent être en lecture seule pour l'utilisateur courant"""
        for record in self:
            # Vérifier si l'utilisateur est le pilote du processus
            is_pilote = record.pilote_id and record.pilote_id.id == self.env.uid
            # Vérifier si l'utilisateur est dans le groupe gestionnaire
            is_gestionnaire = self.env.user.has_group('is_dynacase2odoo.is_gestionnaire_processus_group')
            # Le champ est readonly si l'utilisateur n'est NI pilote NI gestionnaire
            record.is_readonly = not (is_pilote or is_gestionnaire)

    def _get_site_id(self):
        user = self.env['res.users'].browse(self._uid)
        site_id = user.is_site_id.id
        return site_id

    def copy(self, default=None):
        """Surcharge la méthode copy pour ajouter (copie) à la référence"""
        if default is None:
            default = {}
        # N'ajouter "(copie)" que si aucune référence n'est explicitement fournie dans default
        if (self.reference and '(copie)' not in self.reference and 
            'reference' not in default):
            default['reference'] = f"{self.reference} (copie)"
        return super(IsProcessusDoc, self).copy(default)

    def _check_reference_version_duplicate(self, reference, version, exclude_id=None):
        """Vérifie s'il existe un doublon de référence + version"""
        if reference and version:
            domain = [
                ('reference', '=', reference),
                ('version', '=', version)
            ]
            if exclude_id:
                domain.append(('id', '!=', exclude_id))
            
            existing = self.search(domain, limit=1)
            if existing:
                raise ValidationError(
                    f"Un document avec la référence '{reference}' et la version '{version}' existe déjà. "
                    f"Veuillez modifier la référence ou la version."
                )

    @api.model_create_multi
    def create(self, vals_list):
        """Surcharge create pour vérifier l'unicité référence + version en lot"""
        for vals in vals_list:
            reference = vals.get('reference')
            version = vals.get('version')
            self._check_reference_version_duplicate(reference, version)
        return super(IsProcessusDoc, self).create(vals_list)

    def write(self, vals):
        """Surcharge write pour vérifier l'unicité référence + version et notifier le pilote"""
        for record in self:
            reference = vals.get('reference', record.reference)
            version = vals.get('version', record.version)
            self._check_reference_version_duplicate(reference, version, record.id)
        
        # Sauvegarder les anciennes valeurs pour comparaison
        old_values = {}
        for record in self:
            old_values[record.id] = {
                'reference': record.reference,
                'version': record.version,
                'designation': record.designation,
                'auteur_id': record.auteur_id.name if record.auteur_id else '',
                'piece_jointe_noms': record.piece_jointe_noms,
            }
        
        # Effectuer la modification
        result = super(IsProcessusDoc, self).write(vals)
        
        # Envoyer notification au pilote après modification
        for record in self:
            if record.processus_id and record.processus_id.pilotepcs_id:
                record._notify_pilote_modification(vals, old_values.get(record.id, {}))
        
        return result

    def _notify_pilote_modification(self, vals, old_values):
        """Envoie une notification au pilote du processus et aux destinataires de la liste de diffusion lors de la modification du document"""
        self.ensure_one()
        
        if not self.processus_id or not self.processus_id.pilotepcs_id:
            return
        
        pilote = self.processus_id.pilotepcs_id
        
        # Récupérer les destinataires supplémentaires de la liste de diffusion
        liste_diffusion = self.env['is.liste.diffusion.mail']
        destinataires_ids = []
        
        # Ajouter le pilote
        destinataires_ids.append(pilote.partner_id.id)
        
        # Ajouter les destinataires de la liste de diffusion pour 'directeur-qualite'
        partners_directeur_qualite = liste_diffusion.get_partners_ids('is.processus.doc', 'directeur-qualite')
        if partners_directeur_qualite:
            destinataires_ids.extend(partners_directeur_qualite)
        
        # Supprimer les doublons
        destinataires_ids = list(set(destinataires_ids))
        
        # Construire le message des modifications
        modifications = []
        champs_surveilles = {
            'reference': 'Référence',
            'version': 'Version', 
            'designation': 'Désignation',
            'auteur_id': 'Auteur',
            'niveau': 'Niveau',
            'modification': 'Modification',
            'piece_jointe_noms': 'Pièces jointes',
        }
        
        for field, label in champs_surveilles.items():
            # Pour les champs calculés comme piece_jointe_noms, on compare les valeurs actuelles
            if field == 'piece_jointe_noms':
                old_val = old_values.get(field, '')
                new_val = self.piece_jointe_noms  # Valeur recalculée après modification
                if old_val != new_val:
                    modifications.append(f"<li><strong>{label} :</strong> '{old_val}' → '{new_val}'</li>")
            elif field in vals:
                old_val = old_values.get(field, '')
                new_val = vals.get(field, '')
                
                # Gérer les champs Many2one
                if field == 'auteur_id' and isinstance(new_val, int):
                    user = self.env['res.users'].browse(new_val)
                    new_val = user.name if user.exists() else ''
                
                if old_val != new_val:
                    modifications.append(f"<li><strong>{label} :</strong> '{old_val}' → '{new_val}'</li>")
        
        if not modifications:
            return  # Aucune modification significative
        
        # Créer la liste des destinataires pour affichage
        destinataires_info = []
        for partner_id in destinataires_ids:
            partner = self.env['res.partner'].browse(partner_id)
            if partner.exists():
                destinataires_info.append(f"{partner.name} ({partner.email})")
        
        # Informations sur l'émetteur
        emetteur_email = self.env.user.email or self.env.user.partner_id.email or 'noreply@odoo.com'
        emetteur_info = f"{self.env.user.name} ({emetteur_email})"
        
        # Générer l'URL complète vers le document
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        document_url = f"{base_url}/web#id={self.id}&model=is.processus.doc&view_type=form"
        
        # Créer le corps du message
        subject = f"Modification du document {self.reference}"
        body = f"""
        <p>Bonjour,</p>
        <p>Le document <strong><a href="{document_url}">{self.reference} v{self.version}</a></strong> du processus <strong>{self.processus_id.nom}</strong> a été modifié par <strong>{self.env.user.name}</strong>.</p>
        
        <p><strong>Détails des modifications :</strong></p>
        <ul>
            {''.join(modifications)}
        </ul>
        </p>
        <p>{self.env.user.name}</p>
        <hr>
        <p><strong>Émetteur :</strong> {emetteur_info}</p>
        <p><strong>Destinataires :</strong></p>
        <ul>
            {''.join([f"<li>{dest}</li>" for dest in destinataires_info])}
        </ul>
        
        """
        

        print('TEST',destinataires_ids)


        # Poster le message dans le chat ET envoyer par email à tous les destinataires
        self.message_post(
            body=body,
            subject=subject,
            partner_ids=destinataires_ids,
            message_type='email',
            subtype_xmlid='mail.mt_comment',
            email_from=self.env.user.email or self.env.user.partner_id.email or 'noreply@odoo.com'
        )

    @api.depends('piece_jointe_ids', 'piece_jointe_ids.name')
    def _compute_piece_jointe_noms(self):
        """Calcule la liste des noms des pièces jointes pour le tracking"""
        for record in self:
            if record.piece_jointe_ids:
                noms = [pj.name for pj in record.piece_jointe_ids if pj.name]
                record.piece_jointe_noms = ", ".join(sorted(noms))
            else:
                record.piece_jointe_noms = "Aucune pièce jointe"

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

    def action_reviser_document(self):
        """Lance le processus de révision du document"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Réviser ce document',
            'res_model': 'is.processus.doc.revision.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_document_id': self.id}
        }

    def reviser_document(self, motif_revision):
        """Effectue la révision du document"""
        self.ensure_one()
        
        # Récupérer le processus ARCHIVE
        processus_archive = self.env['is.processus'].search([('numpcs', '=', 'ARCHIVE')], limit=1)
        if not processus_archive:
            raise ValidationError("Le processus 'ARCHIVE' n'existe pas. Veuillez le créer avant de réviser un document.")
        
        # Sauvegarder l'ancienne version et référence
        ancienne_version = self.version or "0"
        ancienne_reference = self.reference
        
        # Calculer la nouvelle version (incrémenter de 1)
        try:
            if self.version:
                nouvelle_version = str(int(float(self.version)) + 1)
            else:
                nouvelle_version = "1"
        except:
            nouvelle_version = "1"
        
        # Calculer la nouvelle référence (remplacer le dernier chiffre par la nouvelle version)
        if ancienne_reference and ancienne_reference.count('-') >= 1:
            # Séparer la référence par les tirets
            parts = ancienne_reference.split('-')
            # Remplacer le dernier élément par la nouvelle version
            parts[-1] = nouvelle_version
            nouvelle_reference = '-'.join(parts)
        else:
            # Si pas de format attendu, garder la référence et ajouter la version
            nouvelle_reference = f"{ancienne_reference}-{nouvelle_version}" if ancienne_reference else nouvelle_version
        
        # D'abord mettre à jour le document original avec la nouvelle version et référence
        # pour éviter le conflit de référence+version lors de la duplication
        self.write({
            'reference': nouvelle_reference,
            'version': nouvelle_version,
            'motif_revision': motif_revision
        })
        
        # Ensuite dupliquer le document (copie = ancienne version)
        copie_default = {
            'processus_id': processus_archive.id,
            'version': ancienne_version,
            'motif_revision': False,  # Pas de motif pour l'ancienne version
            'reference': ancienne_reference,  # Garder l'ancienne référence
        }
        copie = self.copy(copie_default)
        
        # Message dans le chat du document original
        message_original = f"""
        <p><strong>Révision du document</strong></p>
        <ul>
            <li><strong>Ancienne référence :</strong> {ancienne_reference} v{ancienne_version}</li>
            <li><strong>Nouvelle référence :</strong> {nouvelle_reference} v{nouvelle_version}</li>
            <li><strong>Motif de révision :</strong> {motif_revision}</li>
            <li><strong>Ancienne version archivée :</strong> 
                <a href="#" data-oe-model="is.processus.doc" data-oe-id="{copie.id}">{copie.reference} v{copie.version}</a>
            </li>
        </ul>
        """
        self.message_post(body=message_original, subject="Révision du document")
        
        # Message dans le chat de la copie (ancienne version)
        message_copie = f"""
        <p><strong>Document archivé suite à révision</strong></p>
        <ul>
            <li><strong>Référence actuelle (archivée) :</strong> {ancienne_reference} v{ancienne_version}</li>
            <li><strong>Nouvelle version du document :</strong> 
                <a href="#" data-oe-model="is.processus.doc" data-oe-id="{self.id}">{nouvelle_reference} v{nouvelle_version}</a>
            </li>
            <li><strong>Motif de révision :</strong> {motif_revision}</li>
        </ul>
        """
        copie.message_post(body=message_copie, subject="Document archivé suite à révision")
        
        return True

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
    responsable    = fields.Char(string="Responsable", tracking=True)
    responsable_id = fields.Many2one('res.users', string="Nom du responsable", tracking=True)
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
    
