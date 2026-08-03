# Copyright 2026 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.osv import expression


class WeighingWizard(models.TransientModel):
    _inherit = "weighing.wizard"

    owner_restriction = fields.Selection(related="move_id.owner_restriction")
    restricted_owner_id = fields.Many2one(related="move_id.restricted_owner_id")
    available_quant_ids = fields.Many2many(
        comodel_name="stock.quant", compute="_compute_available_quant_ids"
    )

    def _owner_restriction_domain(self, field="owner_id"):
        """Domain leaf restricting ``field`` (a many2one to res.partner)
        according to the picking type owner restriction, mirroring the
        domain stock_owner_restriction applies to stock.move.line's
        quant_id field.
        """
        if self.owner_restriction == "unassigned_owner":
            return [(field, "=", False)]
        if self.owner_restriction == "picking_partner":
            return [(field, "=", self.restricted_owner_id.id)]
        if self.owner_restriction == "partner_or_unassigned":
            return expression.OR(
                [[(field, "=", False)], [(field, "=", self.restricted_owner_id.id)]]
            )
        return []

    @api.depends(
        "product_id", "location_id", "owner_restriction", "restricted_owner_id"
    )
    def _compute_available_quant_ids(self):
        for wiz in self:
            domain = [
                ("product_id", "=", wiz.product_id.id),
                ("location_id", "child_of", wiz.location_id.id),
            ]
            domain = expression.AND([domain, wiz._owner_restriction_domain()])
            wiz.available_quant_ids = self.env["stock.quant"].search(domain)

    def _available_lot_domain(self):
        domain = super()._available_lot_domain()
        return expression.AND(
            [domain, self._owner_restriction_domain("quant_ids.owner_id")]
        )
