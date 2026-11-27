/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */
import {Many2OneField, many2OneField} from "@web/views/fields/many2one/many2one_field";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class QuickCreateLotField extends Many2OneField {
    static template = "stock_weighing_auto_create_lot_config.QuickCreateLot";

    setup() {
        super.setup();
        this.action = useService("action");
    }

    get extraCreateContext() {
        const ctx = {...(this.props.record.context || {})};
        const product = this.props.record.data.product_id;
        if (product && product[0]) {
            ctx.default_product_id = product[0];
        }
        // It's need to reopen the weighing wizard after creating new lot
        ctx.active_weighing_wizard_action = {
            type: "ir.actions.act_window",
            res_model: this.props.record.resModel,
            views: [[false, "form"]],
            target: "new",
            context: {...this.props.record.context},
        };
        return ctx;
    }

    async onClickQuickCreate(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "stock.lot",
            views: [[false, "form"]],
            target: "new",
            context: this.extraCreateContext,
        });
    }
}

export const quickCreateLotWidget = {
    ...many2OneField,
    component: QuickCreateLotField,
    supportedTypes: ["many2one"],
};
registry.category("fields").add("quick_create_lot", quickCreateLotWidget);
