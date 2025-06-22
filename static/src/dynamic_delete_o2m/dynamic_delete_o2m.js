/** @odoo-module **/


/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

patch(ListRenderer.prototype, "dynamic_one2many_delete", {
    // Pas besoin de setup() ici sauf si tu ajoutes des hooks OWL
    isDeleteButtonVisible(record) {




        const parentRecord = this.props.list ? this.props.list.props.record : null;


        console.log('TEST 2 : isDeleteButtonVisible', parentRecord);


        if (parentRecord && parentRecord.data.array_ids_ro !== undefined) {
            return !parentRecord.data.array_ids_ro;
        }
        // Appelle le comportement natif si la condition ne s'applique pas
        return ListRenderer.prototype.isDeleteButtonVisible
            ? ListRenderer.prototype.isDeleteButtonVisible.call(this, record)
            : true;
    },
});





// import { patch } from "@web/core/utils/patch";
// import { ListRenderer } from "@web/views/list/list_renderer";

// // Patch du renderer pour masquer la poubelle dynamiquement
// patch(ListRenderer.prototype, "dynamic_one2many_delete", {
//     setup() {
//         super.setup();

//         console.log('TEST 1 : setup');



//     },
//     // Surcharge la méthode qui détermine l'affichage de la poubelle
//     isDeleteButtonVisible(record) {


//         // Récupère la valeur du champ booléen sur le parent
//         // Selon la structure, adapter l'accès au champ
//         const parentRecord = this.props.list ? this.props.list.props.record : null;

//         console.log('TEST 2 : isDeleteButtonVisible', parentRecord);



//         if (parentRecord && parentRecord.data.array_ids_ro !== undefined) {
//             return !parentRecord.data.array_ids_ro;
//         }
//         // Comportement natif sinon
//         return super.isDeleteButtonVisible ? super.isDeleteButtonVisible(record) : true;
//     },
// });







// import { registry } from '@web/core/registry';
// import { X2ManyField } from '@web/views/fields/x2many/x2many_field';

// console.log('TEST 1');

// export class DynamicDeleteO2M extends X2ManyField {
//     setup() {

//         console.log('TEST 2 : setup');


//         super.setup();
//         // Ajoutez ici toute logique d'initialisation si besoin
//     }

//     get canDelete() {

//         console.log('TEST 2 : canDelete');


//         // Récupère la valeur du champ parent
//         return !this.props.record.data.array_ids_ro;
//     }
// }
// DynamicDeleteO2M.template = 'DynamicDeleteO2M';

// console.log('TEST 4');



// registry.category('fields').add('dynamic_delete_o2m', DynamicDeleteO2M);
