/* Copyright 2024 Tecnativa - David Vidal
 * Copyright 2026 Tecnativa - Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {KanbanHeader} from "@web/views/kanban/kanban_header";
import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class WeightRecordingKanbanHeader extends KanbanHeader {
    static template = "stock_weighing.KanbanHeader";
    setup() {
        super.setup();
        this.action = useService("action");
    }
    /**
     * Show print button only when there are operations to print
     */
    get show_weighing_print_button() {
        return this.group.list.records.some((move) => {
            return move.data.show_weighing_print_button;
        });
    }
    /**
     * Print all the labels from a group
     */
    async onPrintLabels() {
        const moves = this.group.list.records.map((record) => {
            return record.data.id;
        });
        const res = this.orm.call("stock.move", "action_print_weight_record_label", [
            moves,
        ]);
        this.action.doAction(res);
    }
    /**
     * Opens the related form view.
     */
    onOpenColumn() {
        this.action.doAction({
            context: {create: false},
            type: "ir.actions.act_window",
            target: "current",
            views: [[false, "form"]],
            res_model: this.group.groupByField.relation,
            res_id: this.group.serverValue,
            view_mode: "form",
        });
    }
}
export class WeightRecordingKanbanRenderer extends KanbanRenderer {
    static components = {
        ...KanbanRenderer.components,
        KanbanHeader: WeightRecordingKanbanHeader,
    };
}

export class WeightRecordingKanbanModel extends kanbanView.Model {
    // Core only opens the first 10 groups and folds the open ones beyond this
    // limit on every reload. Open enough groups to show all the operations to
    // weigh, while keeping a cap for unfiltered searches.
    static MAX_NUMBER_OPENED_GROUPS = 500;
}

export const WeightRecordingKanbanView = {
    ...kanbanView,
    Model: WeightRecordingKanbanModel,
    Renderer: WeightRecordingKanbanRenderer,
};

registry.category("views").add("base_weight_record_kanban", WeightRecordingKanbanView);
