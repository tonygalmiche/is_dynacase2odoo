/** @odoo-module **/
/**
 * Widget personnalisé : many2many_tags_contact
 *
 * Objectif : étendre le widget standard Many2ManyTagsField pour afficher,
 * dans chaque puce (tag) d'un champ Many2many de contacts, des informations
 * enrichies : nom du contact, type de contact et email.
 *
 * Ce widget est utilisé uniquement sur le champ `fournisseur_ids` du modèle
 * IsDemandeConsultationDemandeLine. Il ne modifie pas le comportement global d'Odoo.
 *
 * Utilisation dans la vue XML :
 *   <field name="fournisseur_ids" widget="many2many_tags_contact"
 *          context="{'show_contact_details': True}"/>
 *
 * Note technique : les champs Many2one ne peuvent pas être chargés via fieldsToFetch
 * dans OWL (ils retournent `false`). On utilise donc `is_type_contact_name`, un champ
 * Char related défini côté Python dans res_partner_contact_details.py, qui expose
 * le nom du type de contact sous forme de texte simple.
 */

import { registry } from "@web/core/registry";
import { Many2ManyTagsField } from "@web/views/fields/many2many_tags/many2many_tags_field";

export class Many2ManyTagsContactField extends Many2ManyTagsField {
    /**
     * Construit les propriétés de chaque puce affichée.
     * On surcharge `text` pour afficher : nom, type de contact, email.
     * Format : "Nom contact, Type de contact, email"
     */
    getTagProps(record) {
        const props = super.getTagProps(record);

        // Insère le code fournisseur entre parenthèses après le nom du fournisseur parent.
        // display_name pour un contact Odoo a le format : "Nom fournisseur, Nom contact".
        // On insère "(code)" juste après le nom du fournisseur (avant la première virgule).
        let displayName = record.data.display_name || '';
        if (record.data.is_parent_is_code) {
            const commaIdx = displayName.indexOf(', ');
            if (commaIdx !== -1) {
                displayName = displayName.slice(0, commaIdx) + ` (${record.data.is_parent_is_code})` + displayName.slice(commaIdx);
            } else {
                displayName += ` (${record.data.is_parent_is_code})`;
            }
        }

        const parts = [displayName];
        // Ajout du type de contact (champ Char related is_type_contact_name)
        if (record.data.is_type_contact_name) {
            parts.push(record.data.is_type_contact_name);
        }
        // Ajout de l'email
        if (record.data.email) {
            parts.push(record.data.email);
        }
        props.text = parts.join(', ');
        return props;
    }
}

/**
 * Déclare les champs supplémentaires à charger pour chaque enregistrement
 * des puces Many2many. Seuls les champs de type `char` fonctionnent de manière
 * fiable ici (les Many2one retournent `false` dans le contexte OWL fieldsToFetch).
 */
Many2ManyTagsContactField.fieldsToFetch = {
    display_name: { name: "display_name", type: "char" },
    email: { name: "email", type: "char" },
    // Nom du type de contact exposé comme Char related (voir res_partner_contact_details.py)
    is_type_contact_name: { name: "is_type_contact_name", type: "char" },
    // Code (is_code) du fournisseur parent exposé comme Char related (voir res_partner_contact_details.py)
    is_parent_is_code: { name: "is_parent_is_code", type: "char" },
};

// Enregistrement du widget sous le nom "many2many_tags_contact"
registry.category("fields").add("many2many_tags_contact", Many2ManyTagsContactField);
