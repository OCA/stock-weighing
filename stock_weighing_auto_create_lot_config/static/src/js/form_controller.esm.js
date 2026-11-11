/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */
import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";

patch(FormController.prototype, {
    async saveButtonClicked() {
        const result = await super.saveButtonClicked(...arguments);
        const reopenAction = this.props.context?.active_weighing_wizard_action;
        if (result && reopenAction) {
            const lotId = this.model.root.resId;
            this.props.close?.();
            await this.env.services.action.doAction({
                ...reopenAction,
                context: {
                    ...reopenAction.context,
                    // Select created lot in the wizard after reopening
                    default_lot_id: lotId,
                },
            });
        }
        return result;
    },
});
