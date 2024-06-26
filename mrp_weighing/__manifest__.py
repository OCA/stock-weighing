# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Weighing assistant in batch pickings",
    "summary": "Launch the weighing assistant from batch pickings",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-weighing",
    "license": "AGPL-3",
    "category": "MRP",
    "depends": [
        "stock_weighing",
        "mrp",
    ],
    "data": ["views/mrp_production_view.xml"],
}
