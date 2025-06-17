/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Many2ManyList } from "@web/views/fields/relational_fields";


console.log('TEST 1');


export class ConditionalTreeWidget extends Many2ManyList {
    setup() {
        super.setup();
        this.isReadonly = this.props.record.data.array_ids_ro;

        console.log('TEST 2');


    }

    get canCreate() {
        return !this.isReadonly && super.canCreate;
    }

    get canDelete() {
        return !this.isReadonly && super.canDelete;
    }
}

registry.category("fields").add("conditional_tree", ConditionalTreeWidget);