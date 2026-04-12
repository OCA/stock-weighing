# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMoveWeightWizard(models.TransientModel):
    _inherit = "weighing.wizard"

    product_brand = fields.Char(related="product_id.product_brand_id.name")
    product_brand_logo = fields.Binary(related="product_id.product_brand_id.logo")
    product_brand_has_logo = fields.Boolean(
        compute="_compute_product_brand_has_logo",
    )

    @api.depends("product_brand_logo")
    def _compute_product_brand_has_logo(self):
        for rec in self:
            rec.product_brand_has_logo = bool(rec.product_id.product_brand_id.logo)
