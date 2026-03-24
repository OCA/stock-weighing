from lxml import etree

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockPickingBatchWeighing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.partner = cls.env["res.partner"].create({"name": "Test customer"})
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.picking_type = cls.warehouse.out_type_id
        cls.picking_type.weighing_operations = True
        cls.product_weighted = cls.env["product.product"].create(
            {
                "name": "Weighted product",
                "type": "consu",
            }
        )
        cls.picking_1 = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )
        cls.picking_2 = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )
        cls.move_weighted = cls.env["stock.move"].create(
            {
                "name": "Move weighted",
                "product_id": cls.product_weighted.id,
                "product_uom_qty": 2.0,
                "product_uom": cls.product_weighted.uom_id.id,
                "picking_id": cls.picking_1.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )
        cls.batch = cls.env["stock.picking.batch"].create(
            {
                "company_id": cls.company.id,
                "picking_ids": [(6, 0, (cls.picking_1 | cls.picking_2).ids)],
            }
        )

    def test_action_stock_batch_picking_weighing_returns_batch_action(self):
        action = self.env["stock.move"].action_stock_batch_picking_weighing()
        self.assertTrue(action)
        self.assertIn("views", action)
        self.assertEqual(action["views"], [[False, "kanban"], [False, "list"]])

    def test_get_weighing_start_screen_actions_includes_batch_pickings(self):
        screen_action = self.env.ref("stock_weighing.quick_start_screen_weighing")
        batch_action = screen_action.action_ids.filtered(
            lambda a: a.name == "Batch Picking"
        )
        self.assertTrue(batch_action, "Batch Picking action not found in start screen")
        self.assertEqual(batch_action["icon_name"], "fa-truck")

    def test_kanban_contains_action_weighing_operations_button(self):
        model = self.env["stock.picking.batch"]
        view = self.env.ref("stock_picking_batch.stock_picking_batch_kanban")
        result = model.get_view(view_id=view.id, view_type="kanban")
        arch = etree.fromstring(result["arch"].encode())
        buttons = arch.xpath("//button[@name='action_weighing_operations']")
        self.assertTrue(buttons)
        self.assertEqual(buttons[0].get("type"), "object")
