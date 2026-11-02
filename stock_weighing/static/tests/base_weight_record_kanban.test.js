/* Copyright 2026 Tecnativa - Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {animationFrame, click, press} from "@odoo/hoot-dom";
import {
    contains,
    defineModels,
    fields,
    getKanbanColumn,
    models,
    mountView,
} from "@web/../tests/web_test_helpers";
import {describe, expect, test} from "@odoo/hoot";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";

describe.current.tags("desktop");

const PICKING_IDS = [...Array(12).keys()].map((index) => index + 1);

class Picking extends models.Model {
    name = fields.Char();

    _records = PICKING_IDS.map((id) => ({id, name: `PICK/${id}`}));
}

class Move extends models.Model {
    picking_id = fields.Many2one({relation: "picking"});

    _records = PICKING_IDS.map((id) => ({id, picking_id: id}));
}

defineMailModels();
defineModels([Picking, Move]);

test("All the groups are unfolded and keep the user choice", async () => {
    await mountView({
        type: "kanban",
        resModel: "move",
        arch: `
            <kanban js_class="base_weight_record_kanban">
                <templates>
                    <t t-name="card">
                        <field name="picking_id"/>
                    </t>
                </templates>
            </kanban>`,
        groupBy: ["picking_id"],
    });
    // Core would only open the first 10 groups
    expect(".o_kanban_group").toHaveCount(12);
    expect(".o_column_folded").toHaveCount(0);
    expect(".o_kanban_record").toHaveCount(12);
    await contains(".fa-folder-open", {root: getKanbanColumn(0)}).click();
    expect(getKanbanColumn(0)).toHaveClass("o_column_folded");
    // Reload the view as it happens after each weighing
    await click(".o_searchview_input");
    await press("Enter");
    await animationFrame();
    expect(getKanbanColumn(0)).toHaveClass("o_column_folded");
    expect(".o_column_folded").toHaveCount(1);
    expect(".o_kanban_record").toHaveCount(11);
});
