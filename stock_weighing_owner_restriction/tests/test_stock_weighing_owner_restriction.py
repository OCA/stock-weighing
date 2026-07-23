# Copyright 2026 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestStockWeighingOwnerRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_out.owner_restriction = "picking_partner"
        cls.location = cls.picking_type_out.default_location_src_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.owner = cls.env["res.partner"].create({"name": "Owner test"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Weighed product",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
            }
        )
        cls.lot_owned = cls.env["stock.lot"].create(
            {"name": "LOT-OWNED", "product_id": cls.product.id}
        )
        cls.lot_mixed = cls.env["stock.lot"].create(
            {"name": "LOT-MIXED", "product_id": cls.product.id}
        )
        cls.lot_unowned = cls.env["stock.lot"].create(
            {"name": "LOT-UNOWNED", "product_id": cls.product.id}
        )
        quant_model = cls.env["stock.quant"]
        cls.quant_owned = quant_model.create(
            {
                "product_id": cls.product.id,
                "location_id": cls.location.id,
                "lot_id": cls.lot_owned.id,
                "owner_id": cls.owner.id,
                "quantity": 10,
            }
        )
        cls.quant_mixed_owned = quant_model.create(
            {
                "product_id": cls.product.id,
                "location_id": cls.location.id,
                "lot_id": cls.lot_mixed.id,
                "owner_id": cls.owner.id,
                "quantity": 5,
            }
        )
        cls.quant_mixed_unowned = quant_model.create(
            {
                "product_id": cls.product.id,
                "location_id": cls.location.id,
                "lot_id": cls.lot_mixed.id,
                "quantity": 5,
            }
        )
        cls.quant_unowned = quant_model.create(
            {
                "product_id": cls.product.id,
                "location_id": cls.location.id,
                "lot_id": cls.lot_unowned.id,
                "quantity": 10,
            }
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.owner.id,
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": cls.product.display_name,
                "product_id": cls.product.id,
                "picking_id": cls.picking.id,
                "product_uom_qty": 10,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )

    def _create_wizard(self, **vals):
        return self.env["weighing.wizard"].create(
            dict(move_id=self.move.id, wizard_state="new_move_line", **vals)
        )

    def test_available_lot_ids_excludes_unmatched_owner_lot(self):
        wizard = self._create_wizard()
        self.assertIn(self.lot_owned, wizard.available_lot_ids)
        self.assertIn(self.lot_mixed, wizard.available_lot_ids)
        self.assertNotIn(self.lot_unowned, wizard.available_lot_ids)

    def test_can_add_operation_with_mixed_lot(self):
        wizard = self._create_wizard(lot_id=self.lot_mixed.id, weight=1.0)
        wizard.add_operation_and_record()
        self.assertEqual(wizard.selected_move_line_id.lot_id, self.lot_mixed)

    def test_available_quant_ids_only_includes_matching_owner(self):
        wizard = self._create_wizard()
        self.assertIn(self.quant_owned, wizard.available_quant_ids)
        self.assertIn(self.quant_mixed_owned, wizard.available_quant_ids)
        self.assertNotIn(self.quant_mixed_unowned, wizard.available_quant_ids)
        self.assertNotIn(self.quant_unowned, wizard.available_quant_ids)

    def test_can_select_owned_quant(self):
        wizard = self._create_wizard(quant_id=self.quant_owned.id, weight=1.0)
        wizard.add_operation_and_record()
        self.assertEqual(wizard.selected_move_line_id.owner_id, self.owner)
        self.assertEqual(wizard.selected_move_line_id.lot_id, self.lot_owned)

    def test_standard_behavior_has_no_restriction(self):
        self.picking_type_out.owner_restriction = "standard_behavior"
        wizard = self._create_wizard()
        self.assertIn(self.lot_unowned, wizard.available_lot_ids)
        self.assertIn(self.quant_unowned, wizard.available_quant_ids)
        wizard = self._create_wizard(lot_id=self.lot_unowned.id, weight=1.0)
        wizard.add_operation_and_record()
        self.assertEqual(wizard.selected_move_line_id.lot_id, self.lot_unowned)
