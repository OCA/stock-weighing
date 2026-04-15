# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, TransactionCase


class TestMrpWeighingPickingBatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.delivery_type = cls.warehouse.out_type_id
        cls.delivery_type.close_production = True
        cls.env.ref("stock.route_warehouse0_mto").active = True
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.component = cls.env["product.product"].create(
            {
                "name": "Test Component",
                "is_storable": True,
                "tracking": "lot",
            }
        )
        cls.component_lot = cls.env["stock.lot"].create(
            {"name": "COMPONENTLOT001", "product_id": cls.component.id}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.component, cls.stock_location, 10, lot_id=cls.component_lot
        )
        cls.component_quant = cls.env["stock.quant"].search(
            [
                ("product_id", "=", cls.component.id),
                ("location_id", "=", cls.stock_location.id),
            ]
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Manufactured Product",
                "is_storable": True,
                "tracking": "lot",
                "route_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("mrp.route_warehouse0_manufacture").id,
                            cls.env.ref("stock.route_warehouse0_mto").id,
                        ],
                    )
                ],
            }
        )
        cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.component.id, "product_qty": 1.1})
                ],
            }
        )
        cls.other_product = cls.env["product.product"].create(
            {"name": "Test Other Product", "is_storable": True}
        )

    def _create_sale_order(self, product):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        sale_form.warehouse_id = self.warehouse
        with sale_form.order_line.new() as line:
            line.product_id = product
            line.product_uom_qty = 5
        sale_order = sale_form.save()
        sale_order.action_confirm()
        return sale_order

    def _weigh(self, picking, weight):
        wizard = self.env["weighing.wizard"].create({"move_id": picking.move_ids.id})
        wizard.component_quant_id = self.component_quant
        wizard.weight = weight
        wizard.add_operation_and_record()

    def _create_waiting_picking(self):
        """Delivery waiting for an internal transfer, not for a production"""
        internal = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.int_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.other_product.name,
                            "product_id": self.other_product.id,
                            "product_uom_qty": 3,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.stock_location.id,
                        },
                    )
                ],
            }
        )
        delivery = self.env["stock.picking"].create(
            {
                "picking_type_id": self.delivery_type.id,
                "partner_id": self.partner.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.other_product.name,
                            "product_id": self.other_product.id,
                            "product_uom_qty": 3,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.env.ref(
                                "stock.stock_location_customers"
                            ).id,
                            "move_orig_ids": [(6, 0, internal.move_ids.ids)],
                        },
                    )
                ],
            }
        )
        (internal + delivery).action_confirm()
        return delivery

    def test_batch_closes_unweighed_production(self):
        picking = self._create_sale_order(self.product).picking_ids
        production = picking.move_ids.move_orig_ids.production_id
        self.assertEqual(picking.state, "waiting")
        batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [(6, 0, picking.ids)]}
        )
        batch.action_confirm()
        batch.with_context(skip_backorder=True, skip_expired=True).action_done()
        self.assertEqual(production.state, "done")
        self.assertEqual(production.qty_produced, 5)
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.batch_id, batch)
        self.assertEqual(batch.state, "done")

    def test_batch_detaches_waiting_picking_without_production(self):
        picking = self._create_sale_order(self.product).picking_ids
        production = picking.move_ids.move_orig_ids.production_id
        self._weigh(picking, 4.5)
        waiting_picking = self._create_waiting_picking()
        self.assertEqual(waiting_picking.state, "waiting")
        batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [(6, 0, (picking + waiting_picking).ids)]}
        )
        batch.action_confirm()
        batch.with_context(skip_backorder=True, skip_expired=True).action_done()
        self.assertEqual(production.state, "done")
        self.assertEqual(picking.state, "done")
        self.assertEqual(waiting_picking.state, "waiting")
        self.assertFalse(waiting_picking.batch_id)
