from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking.batch"

    def action_done(self):
        self.ensure_one()
        self._check_company()
        # Before validating a batch picking, we need to validate the stock
        # pickings related to production orders and close the corresponding
        # production orders.
        pickings = self.mapped("picking_ids").filtered(
            lambda picking: picking.state == "waiting"
        )
        pickings.button_validate()
        return super().action_done()
