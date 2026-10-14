# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import ast

from odoo import _, api, fields, models
from odoo.tools import clean_context, float_compare


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    weighing_operations = fields.Boolean(related="picking_type_id.weighing_operations")
    has_weighing_operations = fields.Boolean(compute="_compute_has_weighing_operations")

    @api.depends("move_finished_ids")
    def _compute_has_weighing_operations(self):
        for mrp_production in self:
            mrp_production.has_weighing_operations = mrp_production.move_finished_ids

    def action_weighing_operations(self):
        """Weighing operations for this production order"""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_weighing.weighing_operation_action"
        )
        weight_moves = self.move_finished_ids
        action["name"] = _("Weighing operations for %(name)s", name=self.name)
        action["domain"] = [("id", "in", weight_moves.ids)]
        ctx = dict(
            self.env.context,
            **ast.literal_eval(action["context"]),
            group_by=["production_id"],
            show_weight_detail_buttons=True,
        )
        # We weigh mrp operations that are not in ready state
        ctx.pop("search_default_ready")
        action["context"] = ctx
        return action

    def _get_finished_product_move_lines(self):
        self.ensure_one()
        return self.move_finished_ids.filtered(
            lambda move: move.product_id == self.product_id
            and move.state not in ("done", "cancel")
        ).move_line_ids

    def _set_weighed_qty_producing(self, clear_if_unweighed=False):
        """Produce what has been weighed of the finished product.

        The weighed lines become the finished move lines to be done with their
        weights, and the quantity to produce is the sum of those weights. The rest
        of lines are emptied, so marking the order as done keeps the weighed lines
        instead of reducing the reserved ones.

        :param clear_if_unweighed: when no weight is left, reset the quantity to
            produce too, because it came from the removed weights. Productions whose
            finished product has never been weighed must be called without it.
        """
        for production in self:
            # Weighing wizard context keys (e.g. default_lot_id) must not reach
            # the component move lines created by _set_qty_producing, so the
            # context has to be replaced instead of updated
            # pylint: disable=W8121
            production = production.with_context(clean_context(self.env.context))
            move_lines = production._get_finished_product_move_lines()
            weighed_lines = move_lines.filtered("has_recorded_weight")
            if not weighed_lines and not clear_if_unweighed:
                continue
            (move_lines - weighed_lines).filtered("quantity").quantity = 0.0
            weighed_qty = 0.0
            for line in weighed_lines:
                if float_compare(
                    line.quantity,
                    line.qty_picked,
                    precision_rounding=line.product_uom_id.rounding,
                ):
                    line.quantity = line.qty_picked
                weighed_qty += line.product_uom_id._compute_quantity(
                    line.qty_picked, production.product_uom_id, round=False
                )
            if float_compare(
                weighed_qty,
                production.qty_producing,
                precision_rounding=production.product_uom_id.rounding,
            ):
                production.qty_producing = weighed_qty
                production._set_qty_producing(False)

    def pre_button_mark_done(self):
        self._set_weighed_qty_producing()
        return super().pre_button_mark_done()
