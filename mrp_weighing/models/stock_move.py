# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    is_has_production = fields.Boolean(compute="_compute_is_has_production")

    @api.depends("move_line_ids", "move_orig_ids")
    def _compute_is_has_production(self):
        self.is_has_production = False
        for move in self:
            move.is_has_production = bool(
                move.created_production_id or move.move_orig_ids.mapped("production_id")
            )

    @api.model
    def action_mrp_production_weighing(self):
        """Used in the start screen"""
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_production_action")
        action["views"] = [[False, "kanban"], [False, "list"], [False, "form"]]
        ctx = {"search_default_todo": True}
        action["context"] = ctx
        return action

    def action_add_move_line(self):
        action = super().action_add_move_line()
        if not self.production_id.lot_producing_id:
            production_id = self.move_orig_ids.production_id
            if (
                production_id
                and self.product_id == production_id.product_id
                and production_id.state == "done"
            ):
                raise ValidationError(_("You can not add weight, the MO is done."))
            return action
        default_lot_id = False
        if self.product_id == self.production_id.product_id:
            default_lot_id = self.production_id.lot_producing_id.id
        else:
            last_lot = self.move_line_ids.lot_id[-1:]
            if last_lot:
                default_lot_id = last_lot.id
            elif self.has_tracking:
                lot = self.env["stock.lot"].search(
                    [
                        ("company_id", "=", self.company_id.id),
                        ("product_id", "=", self.product_id.id),
                        ("name", "=", self.production_id.lot_producing_id.name),
                    ],
                    limit=1,
                )
                if lot:
                    default_lot_id = lot.id
                else:
                    sml = self.move_line_ids[:1]
                    if not sml:
                        sml = self.env["stock.move.line"].new(
                            {
                                "lot_name": self.production_id.lot_producing_id.name,
                                "product_id": self.product_id.id,
                                "company_id": self.company_id.id,
                            }
                        )
                    sml._create_and_assign_production_lot()
                    default_lot_id = sml.lot_id.id
        if default_lot_id:
            action["context"].update({"default_lot_id": default_lot_id})
        return action
