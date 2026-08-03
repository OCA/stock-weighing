# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def action_stock_batch_picking_weighing(self):
        """Used in the start screen"""
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_picking_batch.stock_picking_batch_action"
        )
        action["views"] = [[False, "kanban"], [False, "list"]]
        return action
