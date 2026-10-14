# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockWeighing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kg = cls.env.ref("uom.product_uom_kgm")
        cls.gram = cls.env.ref("uom.product_uom_gram")
        cls.unit = cls.env.ref("uom.product_uom_unit")
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_out.create_backorder = "ask"
        cls.product_kg = cls.env["product.product"].create(
            {"name": "Product by weight", "is_storable": True, "uom_id": cls.kg.id}
        )
        cls.product_unit = cls.env["product.product"].create(
            {"name": "Product by unit", "is_storable": True, "uom_id": cls.unit.id}
        )
        for product in cls.product_kg | cls.product_unit:
            cls.env["stock.quant"]._update_available_quantity(product, cls.stock, 20)

    def _create_delivery(self, products):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock.id,
                "location_dest_id": self.customers.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": 10,
                            "location_id": self.stock.id,
                            "location_dest_id": self.customers.id,
                        },
                    )
                    for product in products
                ],
            }
        )
        picking.action_assign()
        return picking

    def _record_weight(self, move_line, weight):
        action = move_line.action_weighing()
        wizard = self.env[action["res_model"]].with_context(**action["context"])
        wizard.create({"weight": weight}).record_weight()

    def _validate_with_backorder(self, picking):
        action = picking.button_validate()
        self.assertEqual(action["res_model"], "stock.backorder.confirmation")
        Form(
            self.env[action["res_model"]].with_context(**action["context"])
        ).save().process()
        self.assertEqual(picking.state, "done")
        return self.env["stock.picking"].search([("backorder_id", "=", picking.id)])

    def test_move_qty_picked_in_move_unit(self):
        # One kilogram demanded, the line is weighed in grams
        picking = self._create_delivery(self.product_kg)
        move = picking.move_ids
        move.move_line_ids.write({"product_uom_id": self.gram.id, "quantity": 10000})
        move.move_line_ids.qty_picked = 8500
        self.assertEqual(move.qty_picked, 8.5)

    def test_weigh_less_than_demand(self):
        picking = self._create_delivery(self.product_kg)
        self._record_weight(picking.move_line_ids, 8.5)
        self.assertTrue(picking.move_line_ids.picked)
        self.assertEqual(picking.move_ids.qty_picked, 8.5)
        backorder = self._validate_with_backorder(picking)
        self.assertEqual(picking.move_ids.quantity, 8.5)
        self.assertEqual(backorder.move_ids.product_uom_qty, 1.5)

    def test_weighing_state(self):
        picking = self._create_delivery(self.product_kg)
        move = picking.move_ids
        if not move.has_weight:
            self.skipTest("An installed module excludes this product from weighing")
        self.assertEqual(move.weighing_state, "to_weigh")
        self._record_weight(move.move_line_ids, 8.5)
        self.assertEqual(move.weighing_state, "weighed")

    def test_weigh_more_than_demand(self):
        picking = self._create_delivery(self.product_kg)
        self._record_weight(picking.move_line_ids, 10.4)
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_ids.quantity, 10.4)

    def test_operations_not_weighed_go_to_backorder(self):
        # Once weighing has started, only the picked operations are validated
        picking = self._create_delivery(self.product_kg | self.product_unit)
        move_kg = picking.move_ids.filtered(lambda m: m.product_id == self.product_kg)
        self._record_weight(move_kg.move_line_ids, 10)
        backorder = self._validate_with_backorder(picking)
        self.assertEqual(backorder.move_ids.product_id, self.product_unit)
        self.assertEqual(backorder.move_ids.product_uom_qty, 10)

    def test_operation_done_from_weighing(self):
        picking = self._create_delivery(self.product_kg | self.product_unit)
        move_kg = picking.move_ids.filtered(lambda m: m.product_id == self.product_kg)
        move_unit = picking.move_ids - move_kg
        self._record_weight(move_kg.move_line_ids, 10)
        move_unit.set_product_uom_qty_to_qty_done_from_weighing()
        self.assertTrue(move_unit.picked)
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(move_unit.quantity, 10)

    def test_lines_without_weight_left_out(self):
        shelves = self.env["stock.location"].create(
            [
                {"name": f"Shelf {index}", "location_id": self.stock.id}
                for index in range(2)
            ]
        )
        product = self.env["product.product"].create(
            {"name": "Product on shelves", "is_storable": True, "uom_id": self.kg.id}
        )
        for shelf in shelves:
            self.env["stock.quant"]._update_available_quantity(product, shelf, 5)
        picking = self._create_delivery(product)
        move = picking.move_ids
        self.assertEqual(len(move.move_line_ids), 2)
        self._record_weight(move.move_line_ids[0], 6)
        backorder = self._validate_with_backorder(picking)
        self.assertEqual(move.move_line_ids.location_id, shelves[0])
        self.assertEqual(move.quantity, 6)
        self.assertEqual(backorder.move_ids.product_uom_qty, 4)

    def test_reset_weights(self):
        # Without any weight the reserved quantities are validated as usual
        picking = self._create_delivery(self.product_kg)
        self._record_weight(picking.move_line_ids, 8.5)
        picking.move_ids.action_reset_weights()
        self.assertFalse(picking.move_line_ids.picked)
        self.assertEqual(picking.move_ids.qty_picked, 0)
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_ids.quantity, 10)
