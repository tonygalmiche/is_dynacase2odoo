/** @odoo-module **/
import { registry } from "@web/core/registry";
import { FieldOne2Many } from 'web.relational_fields';
import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";


console.log('## CustomListRendererPatch',FieldOne2Many);


// Étape 1 : Patch du ListRenderer pour intercepter la méthode de clic sur la ligne
// Nous ciblons 'focusCell' car c'est une méthode interne clé appelée lors d'un clic sur une ligne.
// En la remplaçant et en ne pas appelant this._super(), nous empêchons le comportement par défaut.
patch(ListRenderer.prototype, "is_dynacase2odoo.CustomListRendererPatch", {
    /**
     * Remplace la méthode focusCell pour empêcher le comportement de clic de ligne par défaut
     * (ouverture de la vue formulaire) et exécuter une logique personnalisée.
     *
     * @param {Object} column - L'objet colonne de la cellule en cours de focus.
     * @param {boolean} [forward=true] - Indique la direction du focus.
     * @override
     */
    focusCell(column, forward = true) {
        // Ce console.log s'exécutera lorsque vous cliquerez sur une ligne
        console.log('TEST : ListRenderer - focusCell déclenché pour la colonne :', column.name);

        // --- Votre logique personnalisée va ici ---
        // Par exemple, vous pouvez afficher une notification, ou exécuter une autre action.
        // Pour obtenir l'ID de l'enregistrement cliqué, vous pouvez utiliser :
        // const recordId = this.props.list.records.resId;
        // console.log("ID de l'enregistrement cliqué :", recordId);

        // IMPORTANT : Ne pas appeler this._super() ici.
        // En omettant this._super(), nous empêchons la logique originale de 'focusCell'
        // qui est responsable de l'ouverture de la vue formulaire.
        // Si vous l'appeliez, le formulaire s'ouvrirait toujours.
    },


    // Cette fonction est appellée partout dans Odoo à chaque clic
    // onGlobalClick(ev) {
    //     console.log('TEST : ListRenderer - onGlobalClick', ev);
    // },


    _onRowClicked(ev) {
        // Vérifie si le champ parent est en lecture seule.
        // this.props.readonly reflète l'attribut 'readonly' du champ <field> parent.
        const isFieldReadonly = this.props.readonly; 
        
        console.log('TEST : _onRowClicked détecté. Champ en lecture seule :', isFieldReadonly);

        // Empêche le comportement par défaut (ouverture de la vue formulaire)
        // et la propagation de l'événement. Ceci est fait systématiquement
        // pour prendre le contrôle du clic, que le champ soit en lecture seule ou non.
        ev.preventDefault();
        ev.stopPropagation();

        // --- Votre logique personnalisée ici ---
        // Cette section s'exécutera chaque fois qu'une ligne est cliquée.
        // Vous pouvez ajouter des conditions ici si vous voulez que la logique
        // personnalisée ne s'exécute que si le champ est en lecture seule, ou vice-versa.
        if (isFieldReadonly) {
            console.log("Clic sur une ligne de la liste en lecture seule. Le formulaire ne s'ouvrira pas.");
        } else {
            console.log("Clic sur une ligne de la liste éditable. Le formulaire ne s'ouvrira pas.");
        }

        // IMPORTANT : Ne pas appeler this._super(ev) ici si l'objectif est de TOUJOURS
        // empêcher l'ouverture du formulaire. Si vous l'appeliez, la logique originale
        // de _onRowClicked (qui pourrait inclure l'ouverture du formulaire) s'exécuterait.
    },




    // onButtonCellClicked(record, column, ev) {
    //     console.log('TEST : onButtonCellClicke:', column.name);
    // }

});

// Étape 2 : Créer un widget FieldOne2Many personnalisé
// Ce widget va s'assurer que notre ListRenderer patché est utilisé pour ce champ spécifique.
class CustomOne2ManyNoClick extends FieldOne2Many {
    /**
     * Surcharge la méthode _getRenderer pour retourner notre ListRenderer personnalisé.
     * Cela garantit que le comportement de clic sur la ligne est contrôlé par notre patch.
     * @returns {Class} Le ListRenderer personnalisé à utiliser.
     * @override
     */
    _getRenderer() {

        console.log('## CustomListRendererPatch 2',_getRenderer);



        // Si la vue est une vue en arborescence (tree view), nous retournons le ListRenderer patché.
        if (this.view.arch.tag === 'tree') {
            return ListRenderer; // ListRenderer est maintenant notre version patchée
        }
        // Pour les autres types de vues (par exemple, kanban), nous utilisons le rendu par défaut.
        return super._getRenderer();
    }
}

// Étape 3 : Enregistrer le widget personnalisé
// Le nom 'one2many_no_click' sera utilisé dans le XML pour appliquer ce widget.
registry.category("fields").add("one2many_no_click", CustomOne2ManyNoClick);