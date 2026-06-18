# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    selected_quant_id = fields.Many2one(
        comodel_name="stock.quant",
        readonly=True,
    )

    def action_reset_weights(self):
        res = super().action_reset_weights()
        for move in self.move_id.filtered(
            lambda sm: sm.product_id == sm.production_id.product_id
        ):
            move.production_id.qty_producing = move.quantity
        for move in self.move_id.filtered(
            lambda sm: sm.move_orig_ids.production_id
            and sm.product_id == sm.move_orig_ids.production_id.product_id
        ):
            should_consume_qty = (
                move.move_orig_ids.production_id.move_raw_ids.should_consume_qty
            )
            production = move.move_orig_ids.production_id
            production.qty_producing = move.quantity
            if self.env.context.get("reset_all_lines", False):
                production.move_raw_ids.move_line_ids.quantity = 0.0
            else:
                move_line_id = production.move_raw_ids.move_line_ids.filtered(
                    lambda x: self.selected_quant_id.id in x.lot_id.quant_ids.ids
                )
                if move_line_id:
                    move_line_id.quantity -= (
                        should_consume_qty - production.move_raw_ids.should_consume_qty
                    )
        return res
