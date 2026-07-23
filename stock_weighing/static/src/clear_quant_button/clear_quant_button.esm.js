/* Copyright 2026 Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */
import {patch} from "@web/core/utils/patch";
import {Many2OneField} from "@web/views/fields/many2one/many2one_field";

patch(Many2OneField.prototype, {
    async onClickClearQuant(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const changes = {
            [this.props.name]: false,
            lot_id: false,
        };
        if (this.props.update) {
            await this.props.update(changes);
        } else {
            await this.props.record.update(changes);
        }
    },
});
