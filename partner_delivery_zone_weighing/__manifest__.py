# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Weighing assistant with delivery zones",
    "summary": "Show delivery zones info in weighings",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-weighing",
    "license": "AGPL-3",
    "category": "Inventory",
    "depends": [
        "stock_weighing",
        "partner_delivery_zone",
    ],
    "data": ["views/stock_move_views.xml"],
}
