# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    logo = fields.Binary(related="product_id.product_brand_id.logo")
    product_brand = fields.Char(related="product_id.product_brand_id.name")
