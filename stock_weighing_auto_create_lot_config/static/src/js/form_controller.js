/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */
odoo.define("stock_weighing_auto_create_lot_config.FormController", function (require) {
    "use strict";

    const FormController = require("web.FormController");

    FormController.include({
        _onSave: function () {
            this._super.apply(this, arguments);
            if (
                this.initialState.context &&
                this.initialState.context.action_weighing_wizard
            ) {
                this.do_action(this.initialState.context.action_weighing_wizard);
            }
        },
    });
});
