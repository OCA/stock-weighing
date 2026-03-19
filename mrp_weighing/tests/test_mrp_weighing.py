from odoo.tests import Form, TransactionCase


class TestMrpWeighing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.config.settings"].write(
            {
                "group_stock_tracking_lot": True,
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        )
        cls.stock_production_lot_model = cls.env["stock.lot"]
        cls.manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.delivery_operation_type = cls.env.ref("stock.picking_type_out")
        cls.delivery_operation_type.write({"close_production": True})
        cls.mto_route.write({"active": True})
        cls.seller = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "consu",
                "lst_price": 100.0,
                "standard_price": 10.0,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "tracking": "lot",
                "is_storable": True,
                "seller_ids": [
                    (0, 0, {"partner_id": cls.seller.id, "min_qty": 1, "price": 10.0})
                ],
            }
        )
        cls.component = cls.env["product.product"].create(
            {
                "name": "Test Component",
                "type": "consu",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "tracking": "lot",
                "is_storable": True,
            }
        )
        cls.component_lot_1 = cls.stock_production_lot_model.create(
            {
                "name": "COMPONENTLOT001",
                "product_id": cls.component.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.quant_1 = cls.env["stock.quant"].create(
            {
                "lot_id": cls.component_lot_1.id,
                "quantity": 10,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "company_id": cls.env.company.id,
                "product_id": cls.component.id,
            }
        )
        cls.component_lot_2 = cls.stock_production_lot_model.create(
            {
                "name": "COMPONENTLOT002",
                "product_id": cls.component.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.quant_2 = cls.env["stock.quant"].create(
            {
                "lot_id": cls.component_lot_2.id,
                "quantity": 10,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "company_id": cls.env.company.id,
                "product_id": cls.component.id,
            }
        )
        cls.quant_1.action_apply_inventory()
        cls.quant_2.action_apply_inventory()
        cls.product_lot = cls.stock_production_lot_model.create(
            {
                "name": "PRODUCTLOT001",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.component.id, "product_qty": 1.1})
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

    def _create_sale_order(self):
        warehouse = self.env["stock.warehouse"].search([], limit=1)
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        sale_form.picking_policy = "direct"
        sale_form.warehouse_id = warehouse
        sale_form.company_id = self.env.company
        with sale_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 5
            line.price_unit = 100.0
        sale_order = sale_form.save()
        sale_order.action_confirm()
        return sale_order

    def test_weighing_from_wizard(self):
        sale_order = self._create_sale_order()
        wizard = self.env["weighing.wizard"].create(
            {
                "move_id": sale_order.picking_ids.move_ids[0].id,
            }
        )
        wizard.lot_id = self.product_lot
        wizard.weight = 5
        wizard.add_operation_and_record()
        self.assertEqual(5, sale_order.picking_ids.move_line_ids.qty_picked)

    def test_weighing_from_wizard_with_manufacturing(self):
        self.product.write(
            {
                "route_ids": [(6, 0, [self.manufacture_route.id, self.mto_route.id])],
            }
        )
        sale_order = self._create_sale_order()
        wizard = self.env["weighing.wizard"].create(
            {
                "move_id": sale_order.picking_ids.move_ids[0].id,
            }
        )
        wizard.component_quant_id = self.quant_1
        self.assertTrue(wizard.lot_id)
        wizard.weight = 4.5
        wizard.add_operation_and_record()
        picking = sale_order.picking_ids
        production = picking.move_ids.move_orig_ids.production_id
        self.assertEqual(4.5, picking.move_line_ids.qty_picked)
        self.assertEqual(4.5, production.qty_producing)
        self.assertEqual(wizard.lot_id, production.lot_producing_id)
        self.assertEqual(
            self.component_lot_1, production.move_raw_ids.move_line_ids.lot_id
        )
        picking.with_context(skip_backorder=True, skip_expired=True).button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(production.state, "done")

    def test_weighing_from_wizard_with_manufacturing_more_one_lot(self):
        self.product.write(
            {
                "route_ids": [(6, 0, [self.manufacture_route.id, self.mto_route.id])],
            }
        )
        sale_order = self._create_sale_order()
        wizard = self.env["weighing.wizard"].create(
            {
                "move_id": sale_order.picking_ids.move_ids[0].id,
            }
        )
        wizard.component_quant_id = self.quant_1
        self.assertTrue(wizard.lot_id)
        wizard.weight = 2.5
        wizard.with_context(reload_wizard_action=True).add_operation_and_record()
        wizard.component_quant_id = self.quant_2
        wizard.weight = 2
        wizard.with_context(reload_wizard_action=False).add_operation_and_record()
        picking = sale_order.picking_ids
        production = picking.move_ids.move_orig_ids.production_id
        self.assertEqual(4.5, sum(picking.move_line_ids.mapped("qty_picked")))
        self.assertEqual(4.5, production.qty_producing)
        self.assertEqual(wizard.lot_id, production.lot_producing_id)
        self.assertEqual(
            self.component_lot_1, production.move_raw_ids.move_line_ids[0].lot_id
        )
        self.assertEqual(
            self.component_lot_2, production.move_raw_ids.move_line_ids[1].lot_id
        )
        self.assertEqual(
            4.95,  # Each unit of product requires 1.1 unit of the component
            sum(production.move_raw_ids.mapped("qty_picked")),
        )
        picking.with_context(skip_backorder=True, skip_expired=True).button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(production.state, "done")
