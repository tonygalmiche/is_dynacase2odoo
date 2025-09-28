/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class CartographieProcessus extends Component {
    static template = "is_dynacase2odoo.CartographieProcessusTemplate";

    setup() {
        this.actionService = useService("action");
    }

    /**
     * Ouvre un document via une action Odoo
     * @param {Event} ev - L'événement de clic
     */
    onOpenDocument(ev) {
        ev.preventDefault();
        
        const resId = parseInt(ev.currentTarget.dataset.resId);
        const resModel = ev.currentTarget.dataset.resModel;
        
        if (resId && resModel) {
            this.actionService.doAction({
                type: 'ir.actions.act_window',
                res_model: resModel,
                res_id: resId,
                views: [[false, 'form']],
                view_mode: 'form',
                target: 'current',
            });
        }
    }
}

registry.category("actions").add("is_dynacase2odoo.cartographie_processus", CartographieProcessus);