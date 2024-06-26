# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class WeighingWizard(models.TransientModel):
    _inherit = "weighing.wizard"

    stock_weighing_auto_package = fields.Boolean(
        related="product_id.stock_weighing_auto_package",
        readonly=False,
        string="Auto package",
    )

    def _post_add_detailed_operation(self):
        res = super(WeighingWizard, self)._post_add_detailed_operation()
        if self.result_package_id:
            self.selected_move_line_id.result_package_id = self.result_package_id
        elif self.stock_weighing_auto_package:
            self.selected_move_line_id.result_package_id = self.env[
                "stock.quant.package"
            ].create({})
        return res
