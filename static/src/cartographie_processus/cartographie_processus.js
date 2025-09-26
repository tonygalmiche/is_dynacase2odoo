/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

class CartographieProcessus extends Component {
    static template = "is_dynacase2odoo.CartographieProcessusTemplate";
}

registry.category("actions").add("is_dynacase2odoo.cartographie_processus", CartographieProcessus);