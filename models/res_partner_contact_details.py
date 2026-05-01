# -*- coding: utf-8 -*-
# Objectif : enrichir l'affichage des contacts partenaires dans le champ fournisseur_ids
# du modèle IsDemandeConsultationDemandeLine, en ajoutant le type de contact et l'email.
#
# Ce fichier contient deux mécanismes complémentaires :
#
# 1. Le champ `is_type_contact_name` (Char related, non stocké) :
#    Expose le nom du type de contact (Many2one -> is.type.contact) sous forme de
#    champ texte simple. Cela est nécessaire car le widget OWL Many2ManyTagsField ne
#    peut pas charger les champs Many2one via `fieldsToFetch` (ils retournent `false`).
#    En passant par un champ Char related, le widget peut le récupérer fiablement.
#
# 2. La méthode `_get_name()` :
#    Surcharge le calcul du nom affiché dans la liste déroulante (autocomplete).
#    Lorsque le contexte `show_contact_details` est True, le nom est enrichi avec
#    le type de contact et l'email séparés par des virgules.
#    Note : on surcharge `_get_name()` et non `name_get()` ni `_compute_display_name()`
#    car `display_name` est un champ stocké calculé avec un contexte vide sur res.partner.
#    Seul `_get_name()` est appelé avec le contexte réel lors du rendu des listes déroulantes.
#
# 3. La méthode `_name_search()` :
#    Surcharge la recherche dans l'autocomplete pour inclure le code du fournisseur
#    parent (is_code) en plus du nom. Activée uniquement avec le contexte
#    `show_contact_details`, afin de ne pas affecter les autres champs d'Odoo.
from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Champ Char related exposant le nom du type de contact.
    # Non stocké, calculé à la volée depuis is_type_contact.name.
    # Utilisé par le widget JS `many2many_tags_contact` via fieldsToFetch
    # pour afficher le type dans les puces (tags) du champ Many2many.
    is_type_contact_name = fields.Char(
        related='is_type_contact.name',
        string="Nom type de contact",
        store=False,
    )

    # Champ Char related exposant le code (is_code) du fournisseur parent.
    # Non stocké, calculé à la volée depuis parent_id.is_code.
    # Utilisé par le widget JS pour afficher le code entre parenthèses
    # après le nom du fournisseur dans les puces (tags).
    is_parent_is_code = fields.Char(
        related='parent_id.is_code',
        string="Code fournisseur parent",
        store=False,
    )

    def _get_name(self):
        # Enrichit le nom affiché dans la liste déroulante de sélection.
        # Activé uniquement quand le contexte show_contact_details=True est présent,
        # ce qui est positionné sur le champ fournisseur_ids dans la vue XML.
        # Format : "Nom fournisseur (code), Nom contact, Type de contact, email"
        name = super()._get_name()
        if self._context.get('show_contact_details'):
            # Insère le code du fournisseur parent entre parenthèses après son nom.
            # Le nom retourné par super() pour un contact est "Nom parent, Nom contact".
            # On repère la première virgule pour insérer le code juste avant.
            if self.parent_id and self.parent_id.is_code:
                parent_name = self.parent_id.name or ''
                code_str = f' ({self.parent_id.is_code})'
                if name.startswith(parent_name):
                    name = parent_name + code_str + name[len(parent_name):]
            extra = []
            if self._fields.get('is_type_contact') and self.is_type_contact:
                extra.append(self.is_type_contact.name)
            if self.email:
                extra.append(self.email)
            if extra:
                name = name + ', ' + ', '.join(extra)
        return name

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        # Surcharge de la recherche dans l'autocomplete.
        # Quand le contexte show_contact_details est actif, on recherche aussi
        # sur le code du fournisseur parent (parent_id.is_code), en plus du nom
        # habituel du contact. Les résultats des deux recherches sont fusionnés.
        ids = list(super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid))
        if self._context.get('show_contact_details') and name:
            code_domain = (args or []) + [('parent_id.is_code', operator, name)]
            code_ids = list(super()._name_search('', args=code_domain, operator=operator, limit=limit, name_get_uid=name_get_uid))
            # Fusion sans doublons en préservant l'ordre
            seen = set(ids)
            ids = ids + [i for i in code_ids if i not in seen]
            if limit:
                ids = ids[:limit]
        return ids
