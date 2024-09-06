/** @odoo-module **/
/* Copyright 2024 Tecnativa - David Vidal
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import KanbanColumn from "web.KanbanColumn";
import KanbanController from "web.KanbanController";
import KanbanRenderer from "web.KanbanRenderer";
import KanbanView from "web.KanbanView";
import viewRegistry from "web.view_registry";

export const WeightRecordingKanbanColumn = KanbanColumn.extend({
    template: "WeightRecordingKanbanView.Group",
    events: _.extend({}, KanbanColumn.prototype.events || {}, {
        "click .toggle_kanban_fold": "_onToggleFold",
        "click .column_print_labels": "_onPrintLabels",
    }),
    /**
     * Show print button only when there are operations to print
     * @override
     */
    init() {
        this._super(...arguments);
        this.show_weighing_print_button = this.data_records.some((move) => {
            return move.data.show_weighing_print_button;
        });
    },
    /**
     * Bubble up to print labels of this group/column
     * @param {Event} event
     */
    _onPrintLabels(event) {
        event.preventDefault();
        this.trigger_up("column_print_labels");
    },
});

export const WeightRecordingKanbanController = KanbanController.extend({
    custom_events: Object.assign({}, KanbanController.prototype.custom_events, {
        column_print_labels: "_onPrintLabels",
    }),
    /**
     * Refresh the view after we change the record value so we can update filters,
     * progressbars, etc.
     * TODO: Depends on https://github.com/odoo/odoo/pull/161042 Otherwise we should
     * rewrite the whole method.
     * @override
     * @returns {Promise}
     */
    _reloadAfterButtonClick() {
        const def = this._super(...arguments);
        return def.then(() => {
            this.reload();
        });
    },
    /**
     * Print all the labels from a group
     * @param {Event} event
     * @returns {Promise}
     */
    _onPrintLabels(event) {
        const columnID = event.target.db_id || event.data.db_id;
        const moves = this.model.get(columnID).data.map((r) => {
            return r.res_id;
        });
        return this._rpc({
            model: "stock.move",
            method: "action_print_weight_record_label",
            args: [moves],
        });
    },
});

export const WeightRecordingKanbanRenderer = KanbanRenderer.extend({
    config: _.extend({}, KanbanRenderer.prototype.config, {
        KanbanColumn: WeightRecordingKanbanColumn,
    }),
});

export const WeightRecordingKanbanView = KanbanView.extend({
    config: _.extend({}, KanbanView.prototype.config, {
        Renderer: WeightRecordingKanbanRenderer,
        Controller: WeightRecordingKanbanController,
    }),
});

viewRegistry.add("base_weight_record_kanban", WeightRecordingKanbanView);
