# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools import clean_context


class StockMoveWeightWizard(models.TransientModel):
    _inherit = "weighing.wizard"

    component_quant_id = fields.Many2one(
        string="Select component lot",
        comodel_name="stock.quant",
        domain="[('id', 'in', component_available_stock_quant_ids)]",
    )
    component_available_stock_quant_ids = fields.Many2many(
        comodel_name="stock.quant",
        compute="_compute_component_available_stock_quant_ids",
    )
    is_production = fields.Boolean(compute="_compute_is_production", store=True)
    lot_id = fields.Many2one(compute="_compute_lot_id", store=True, readonly=False)

    @api.depends("component_quant_id")
    def _compute_lot_id(self):
        for wiz in self:
            if wiz.is_production and wiz.component_quant_id and not wiz.lot_id:
                existed_lot = self.env["stock.lot"].search(
                    [
                        ("product_id", "=", wiz.product_id.id),
                        ("company_id", "=", wiz.move_id.company_id.id),
                        ("name", "=", wiz.component_quant_id.lot_id.name),
                    ],
                    limit=1,
                )
                if existed_lot:
                    wiz.lot_id = existed_lot
                else:
                    wiz.lot_id = self.env["stock.lot"].create(
                        {
                            "product_id": wiz.product_id.id,
                            "company_id": wiz.move_id.company_id.id,
                            "name": wiz.component_quant_id.lot_id.name,
                        }
                    )

    @api.depends("move_id")
    def _compute_is_production(self):
        for wiz in self:
            wiz.is_production = bool(wiz.move_id.move_orig_ids.production_id)

    @api.depends("product_id")
    def _compute_component_available_stock_quant_ids(self):
        self.component_available_stock_quant_ids = False
        for wiz in self:
            production = wiz.move_id.move_orig_ids.production_id
            if not production:
                continue
            product_ids = production.move_raw_ids.product_id.ids
            wiz.component_available_stock_quant_ids = self.env["stock.quant"].search(
                [
                    ("product_id", "in", product_ids),
                    ("quantity", ">", 0),
                    ("location_id.usage", "=", "internal"),
                ],
                order="create_date desc",
                limit=5,
            )

    def _sync_production_weight(self, production):
        production.lot_producing_id = self.lot_id
        selected_component_lot = production.move_raw_ids.move_line_ids.filtered(
            lambda line: line.product_id == self.component_quant_id.product_id
            and line.lot_id == self.component_quant_id.lot_id
        )
        if not selected_component_lot:
            move_component = production.move_raw_ids.filtered(
                lambda r: r.product_id == self.component_quant_id.product_id
            )
            # We need to clean the context because the weighing wizard has own
            # context keys that can cause issues when writing on the production order
            selected_component_lot = self.env["stock.move.line"].create(
                {
                    "move_id": move_component.id,
                    "product_id": self.component_quant_id.product_id.id,
                    "lot_id": self.component_quant_id.lot_id.id,
                    "product_uom_id": self.component_quant_id.product_id.uom_id.id,
                    "location_id": move_component.location_id.id,
                    "location_dest_id": move_component.location_dest_id.id,
                    "company_id": self.env.company.id,
                }
            )
        self.selected_move_line_id.selected_quant_id = self.component_quant_id
        selected_component_lot.lot_id = self.component_quant_id.lot_id
        other_component_lots = production.move_raw_ids.move_line_ids.filtered(
            lambda line: line.product_id == self.component_quant_id.product_id
            and line.lot_id != self.component_quant_id.lot_id
            and line.qty_picked > 0
        )
        if other_component_lots:
            qty_done = production.move_raw_ids.should_consume_qty - sum(
                other_component_lots.mapped("qty_picked")
            )
        else:
            qty_done = production.move_raw_ids.should_consume_qty
        # pylint: disable=W8121
        # Force context to remove default_move_id when analytic line is created
        selected_component_lot.with_context(clean_context(self._context)).write(
            {"qty_picked": qty_done}
        )

    def add_operation_and_record(self):
        self = self.with_context(show_lot_product=True)
        return super().add_operation_and_record()

    def record_weight(self):
        action = super().record_weight()
        sm = self.selected_move_line_id.move_id
        production_id = self.move_id.move_orig_ids.production_id
        if sm.product_id == sm.production_id.product_id:
            sm.production_id.qty_producing = sm.quantity
            return action
        if production_id:
            production_id.qty_producing = sm.qty_picked
            if self.selected_move_line_id.selected_quant_id:
                self.component_quant_id = self.selected_move_line_id.selected_quant_id
            self._sync_production_weight(production_id)
        return action
