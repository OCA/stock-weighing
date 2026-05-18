# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import ast

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    weighing_operations = fields.Boolean(related="picking_type_id.weighing_operations")
    has_weighing_operations = fields.Boolean(compute="_compute_has_weighing_operations")

    @api.depends("move_ids")
    def _compute_has_weighing_operations(self):
        for picking in self:
            picking.has_weighing_operations = picking.move_ids.filtered("has_weight")

    def action_weighing_operations(self):
        """Weighing operations for this picking"""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_weighing.weighing_operation_action"
        )
        any_operation_actions = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_weighing.any_operation_actions")
        )
        weight_moves = (
            self.move_ids
            if any_operation_actions
            else self.move_ids.filtered("has_weight")
        )
        action["name"] = self.env._("Weighing operations for %(name)s", name=self.name)
        action["domain"] = [("id", "in", weight_moves.ids)]
        action["context"] = dict(
            self.env.context,
            **ast.literal_eval(action["context"]),
            group_by=["picking_id"],
        )
        return action

    def button_validate(self):
        # Only sync quantity from the weighing wizard result; skip lines completed
        # directly from the reception screen (no recorded weight) to avoid zeroing them.
        move_lines_with_weight = self.move_ids.move_line_ids.filtered("has_weight")
        for move_line in move_lines_with_weight:
            if not move_line.has_recorded_weight:
                continue
            move_line.quantity = move_line.qty_picked
        return super().button_validate()
