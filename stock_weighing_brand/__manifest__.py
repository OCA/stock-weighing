# Copyright 2025 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Show brand logo in Weighing assistant",
    "summary": "Show product logo in Weighing assistant",
    "version": "18.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-weighing",
    "license": "AGPL-3",
    "category": "Inventory",
    "depends": ["stock_weighing", "product_brand"],
    "data": [
        "views/stock_move_views.xml",
        "wizards/weighing_wizard_views.xml",
    ],
}
