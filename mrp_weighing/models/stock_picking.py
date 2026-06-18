from odoo import fields, models
from odoo.tools.misc import clean_context


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    close_production = fields.Boolean()


class Picking(models.Model):
    _inherit = "stock.picking"

    close_production = fields.Boolean(
        related="picking_type_id.close_production", readonly=True
    )

    def _close_production(self):
        for picking in self:
            production_ids = picking.move_ids.move_orig_ids.production_id
            if production_ids:
                production_ids.move_raw_ids.picked = True
                # pylint: disable=W8121
                # Force context to remove default_group_id when analytic line is created
                move_lines_with_weight = (
                    production_ids.move_raw_ids.move_line_ids.filtered(
                        lambda line: line.qty_picked > 0
                    )
                )
                for line in move_lines_with_weight:
                    line.quantity = line.qty_picked
                production_ids.with_context(
                    clean_context(self._context),
                    skip_backorder=True,
                ).button_mark_done()
        return True

    def button_validate(self):
        with_close_production = self.filtered_domain([("close_production", "=", True)])
        if with_close_production:
            with_close_production._close_production()
        res = super().button_validate()
        return res
