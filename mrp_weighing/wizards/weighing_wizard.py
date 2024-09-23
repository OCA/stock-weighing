# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMoveWeightWizard(models.TransientModel):
    _inherit = "weighing.wizard"

    def record_weight(self):
        action = super().record_weight()
        sm = self.selected_move_line_id.move_id
        if sm.product_id == sm.production_id.product_id:
            sm.production_id.qty_producing = sm.quantity_done
        return action
