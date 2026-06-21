# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    remote_scale_id = fields.Many2one(
        comodel_name="remote.measure.device",
        compute="_compute_remote_scale_id",
        readonly=False,
    )

    @api.depends(
        "picking_id",
        "picking_id.picking_type_id.remote_scale_id",
        "picking_id.remote_scale_id",
        "product_uom",
    )
    def _compute_remote_scale_id(self):
        """Avoid measuring when the scale and move UoMs are in different categories."""
        for move in self:
            picking_scale = (
                move.picking_id.remote_scale_id
                or move.picking_id.picking_type_id.remote_scale_id
            )
            scale = (
                move.product_uom.category_id == picking_scale.uom_id.category_id
                and picking_scale
            )
            if not scale and self.env.context.get("force_user_measure_device"):
                scale = (
                    move.product_uom.category_id
                    == self.env.user.remote_measure_device_id.uom_id.category_id
                    and self.env.user.remote_measure_device_id
                )
            move.remote_scale_id = scale or False
