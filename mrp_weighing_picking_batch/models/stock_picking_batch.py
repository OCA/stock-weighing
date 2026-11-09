# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    def action_done(self):
        # Pickings waiting for a production have nothing reserved, so the core
        # would detach them from the batch. Close their productions first so
        # they get reserved quantities and are validated with the batch.
        self.picking_ids.filtered(
            lambda picking: picking.state == "waiting" and picking.close_production
        )._close_production()
        return super().action_done()
