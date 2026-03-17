/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */
odoo.define(
    "stock_weighing_auto_create_lot_config.quick_create_lot",
    function (require) {
        "use strict";

        const fieldRegistry = require("web.field_registry");
        const relationalFields = require("web.relational_fields");

        const FieldMany2One = relationalFields.FieldMany2One;

        const QuickCreateLot = FieldMany2One.extend({
            template: "stock_weighing_auto_create_lot_config.QuickCreateLot",

            events: Object.assign({}, FieldMany2One.prototype.events, {
                "click .o_m2o_quick_create_btn": "_onQuickCreateClick",
            }),

            _createContext: function () {
                const res = this._super.apply(this, arguments);
                res.default_product_id = this.recordData.product_id.res_id;
                return res;
            },

            _onQuickCreateClick: function (ev) {
                ev.preventDefault();
                ev.stopPropagation();

                const valueContext = this._createContext();
                return this._searchCreatePopup("form", false, valueContext);
            },
        });

        fieldRegistry.add("quick_create_lot", QuickCreateLot);

        return QuickCreateLot;
    }
);
