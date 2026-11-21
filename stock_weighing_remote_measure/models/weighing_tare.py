# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import html_escape

HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
DEFAULT_COLOR = "#00A09D"


class WeighingTare(models.Model):
    _name = "weighing.tare"
    _description = "Weighing tare"
    _order = "sequence, id"

    def _default_sequence(self):
        """Place new tares after the existing ones, as shown when adding them"""
        last_tare = self.with_context(active_test=False).search(
            [], order="sequence desc, id desc", limit=1
        )
        return last_tare.sequence + 1 if last_tare else 10

    name = fields.Char(string="Display text", required=True, translate=True)
    sequence = fields.Integer(default=lambda self: self._default_sequence())
    active = fields.Boolean(default=True)
    value = fields.Float(required=True, digits="Stock Weight")
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        required=True,
        default=lambda self: self.env.ref("uom.product_uom_kgm"),
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_kgm").id)
        ],
    )
    color = fields.Char(required=True, default=DEFAULT_COLOR)
    text_color = fields.Char(compute="_compute_text_color")
    preview = fields.Html(compute="_compute_preview", sanitize=False)

    _sql_constraints = [
        ("value_positive", "CHECK(value > 0)", "The tare value must be positive."),
    ]

    @api.constrains("color")
    def _check_color(self):
        for tare in self:
            if not HEX_COLOR_RE.match(tare.color):
                raise ValidationError(
                    _("The color must be an hexadecimal value like #00A09D.")
                )

    def _get_valid_color(self):
        """The color may be invalid while it is being edited"""
        self.ensure_one()
        return self.color if HEX_COLOR_RE.match(self.color or "") else DEFAULT_COLOR

    @api.depends("color")
    def _compute_text_color(self):
        for tare in self:
            tare.text_color = self._get_text_color(tare._get_valid_color())

    @api.depends("name", "color", "text_color")
    def _compute_preview(self):
        """Tare buttons as they are shown in the weighing widget"""
        for tare in self:
            style = "--tare-color: {}; --tare-text-color: {}".format(
                tare._get_valid_color(), tare.text_color
            )
            tare.preview = (
                '<div class="btn-group btn-group-lg o_weighing_tare_preview">'
                '<span class="btn btn-tare-outline" style="{style}">-</span>'
                '<span class="btn btn-tare" style="{style}">{name}</span>'
                '<span class="btn btn-tare-outline" style="{style}">+</span>'
                "</div>"
            ).format(style=style, name=html_escape(tare.name or "..."))

    @api.model
    def _get_text_color(self, color):
        """Black or white text depending on the background luminance"""
        red, green, blue = (int(color[i : i + 2], 16) for i in (1, 3, 5))
        luminance = 0.299 * red + 0.587 * green + 0.114 * blue
        return "#000000" if luminance > 150 else "#FFFFFF"

    @api.model
    def get_widget_tares(self, uom_id):
        """Tares to be shown in the weighing widget converted to the given UoM"""
        uom = self.env["uom.uom"].browse(uom_id)
        return [
            {
                "name": tare.name,
                "tare": tare.uom_id._compute_quantity(tare.value, uom, round=False),
                "color": tare.color,
                "text_color": self._get_text_color(tare.color),
            }
            for tare in self.search([])
            if tare.uom_id.category_id == uom.category_id
        ]
