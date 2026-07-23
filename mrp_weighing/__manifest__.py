# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Weighing assistant in batch pickings",
    "summary": "Launch the weighing assistant from batch pickings",
    "version": "18.0.1.0.1",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-weighing",
    "license": "AGPL-3",
    "category": "MRP",
    "depends": ["stock_weighing", "mrp", "sale_mrp"],
    "data": [
        "data/quick_start_screens.xml",
        "views/mrp_production_view.xml",
        "views/stock_picking_views.xml",
        "views/stock_move_views.xml",
        "wizards/weighing_wizard_views.xml",
    ],
}
