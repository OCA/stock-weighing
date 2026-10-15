/** @odoo-module **/
// Copyright 2026 Tecnativa - Carlos Roca
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import {FieldOne2Many} from "web.relational_fields";
import fieldRegistry from "web.field_registry";

/**
 * The core x2many widget only sorts the records again after a drag and drop
 * when the subview is a list. Do the same for the kanban subview so the tares
 * are shown in the position where they were dropped.
 */
export const WeighingTareOne2Many = FieldOne2Many.extend({
    /**
     * @override
     */
    _render() {
        return Promise.resolve(this._super(...arguments)).then(() =>
            this._setupKanbanSortable()
        );
    },
    /**
     * The dragged card is moved inside the scrollable dialog by default, so its
     * position is wrongly computed when the dialog is scrolled. Drag a copy
     * attached to the body instead, above the dialog.
     *
     * @private
     */
    _setupKanbanSortable() {
        const $kanban = this.renderer && this.renderer.$el;
        if (!$kanban || !$kanban.sortable("instance")) {
            return;
        }
        $kanban.sortable("option", {
            helper: "clone",
            appendTo: "body",
            zIndex: 1100,
        });
    },
    /**
     * @override
     * @param {OdooEvent} ev
     */
    _onResequenceRecords(ev) {
        if (this.view.arch.tag !== "kanban") {
            return this._super(...arguments);
        }
        ev.stopPropagation();
        // Freeze the current order so the sort below isn't toggled to descending
        this.trigger_up("edited_list", {id: this.value.id});
        const {handleField, offset} = ev.data;
        const recordIds = ev.data.recordIds.slice();
        const lastRecordId = recordIds.pop();
        const proms = recordIds.map((recordId, index) =>
            this._setValue(
                {
                    operation: "UPDATE",
                    id: recordId,
                    data: {[handleField]: offset + index},
                },
                {notifyChange: false}
            )
        );
        const sortRecords = () =>
            this.trigger_up("toggle_column_order", {
                id: this.value.id,
                name: handleField,
            });
        return Promise.all(proms).then(() =>
            this._setValue({
                operation: "UPDATE",
                id: lastRecordId,
                data: {[handleField]: offset + recordIds.length},
            })
                .then(sortRecords)
                .guardedCatch(sortRecords)
        );
    },
});

fieldRegistry.add("weighing_tare_one2many", WeighingTareOne2Many);
