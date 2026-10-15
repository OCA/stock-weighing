# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockWeighing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kg = cls.env.ref("uom.product_uom_kgm")
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.product_kg, cls.product_kg_extra = cls.env["product.product"].create(
            [
                {
                    "name": name,
                    "type": "product",
                    "uom_id": cls.kg.id,
                    "uom_po_id": cls.kg.id,
                }
                for name in ("Product by weight", "Extra product by weight")
            ]
        )
        for product in cls.product_kg | cls.product_kg_extra:
            cls.env["stock.quant"]._update_available_quantity(product, cls.stock, 20)

    def _create_delivery(self):
        picking_form = Form(self.env["stock.picking"])
        picking_form.picking_type_id = self.picking_type_out
        picking_form.partner_id = self.env.ref("base.res_partner_1")
        with picking_form.move_ids_without_package.new() as move_form:
            move_form.product_id = self.product_kg
            move_form.product_uom_qty = 10
        picking = picking_form.save()
        picking.action_confirm()
        picking.action_assign()
        return picking

    def _weighing_wizard_form(self, move):
        """Open the wizard of the new operation button of the weighing kanban"""
        action = move.action_add_move_line()
        return Form(
            self.env[action["res_model"]].with_context(**action["context"]),
            view=action["view_id"][0],
        )

    def test_weigh_move_without_demand(self):
        picking = self._create_delivery()
        # A product without demand is added to the delivery to weigh it
        with Form(picking) as picking_form:
            with picking_form.move_ids_without_package.new() as move_form:
                move_form.product_id = self.product_kg_extra
        move = picking.move_lines.filtered(
            lambda sm: sm.product_id == self.product_kg_extra
        )
        self.assertFalse(move.product_uom_qty)
        # The wizard weighs it as a move with demand of the same kind
        move_with_demand = picking.move_lines - move
        self.assertEqual(
            self._weighing_wizard_form(move).has_weight,
            self._weighing_wizard_form(move_with_demand).has_weight,
        )
        wizard_form = self._weighing_wizard_form(move)
        wizard_form.weight = 4.2
        wizard_form.print_label = False
        wizard_form.save().add_operation_and_record()
        self.assertEqual(move.move_line_ids.qty_done, 4.2)
        self.assertEqual(move.move_line_ids.recorded_weight, 4.2)
