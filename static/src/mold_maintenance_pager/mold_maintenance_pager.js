/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { actionService } from "@web/webclient/actions/action_service";

// Précédent/Suivant buttons on the "Maintenance préventive moule" line forms
// re-open the same controller on another record. A normal type="object"
// button always pushes a new breadcrumb entry, so instead of letting Odoo's
// default doActionButton run for these two specific buttons, we call the
// Python method ourselves and replace the current breadcrumb entry.
const REPLACE_MODEL = "is.mold.maintenance.preventive.line";
const REPLACE_METHODS = ["action_precedent", "action_suivant"];

patch(actionService, "is_mold_maintenance_preventive_pager", {
    start(env) {
        const service = this._super(env);
        const originalDoActionButton = service.doActionButton;
        service.doActionButton = async function (params) {
            if (params.resModel === REPLACE_MODEL && REPLACE_METHODS.includes(params.name)) {
                const action = await env.services.rpc("/web/dataset/call_button", {
                    args: [[params.resId]],
                    kwargs: { context: params.context || {} },
                    method: params.name,
                    model: params.resModel,
                });
                if (action && typeof action === "object" && action.res_id) {
                    await service.doAction(action, {
                        stackPosition: "replaceCurrentAction",
                        onClose: params.onClose,
                    });
                }
                return;
            }
            return originalDoActionButton(params);
        };
        return service;
    },
});
