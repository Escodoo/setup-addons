# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

def post_init_hook(cr, registry):
    """Install required optional dependencies."""
    from odoo.modules.module import get_module_resource
    from odoo.service import common
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    modules_to_install = [
        "account_analytic_required",
        "account_asset_management",
        "account_due_list",
        "account_due_list_payment_mode",
        "account_financial_report",
        "account_move_base_import",
        "account_move_csv_import",
        "account_move_template",
        "account_payment",
        "account_payment_order",
        "account_payment_partner",
        "account_reconcile_oca",
        "account_statement_import_ofx",
        "auth_admin_passkey",
        "automation_oca",
        "base",
        "base_address_extended",
        "base_automation",
        "base_setup",
        "base_technical_features",
        "bi_sql_editor",
        "contacts",
        "contract",
        "crm",
        "currency_rate_update",
        "date_range",
        "date_range_account",
        "delivery",
        "delivery_carrier_partner",
        "fleet_vehicle_calendar_year",
        "fleet_vehicle_fuel_capacity",
        "fleet_vehicle_fuel_type_ethanol",
        "fleet_vehicle_inspection",
        "hr",
        "hr_contract",
        "hr_employee_age",
        "hr_skills",
        "hr_timesheet",
        "hr_timesheet_sheet",
        "mis_builder",
        "portal",
        "product",
        "product_expiry",
        "purchase",
        "purchase_default_terms_conditions",
        "purchase_order_line_menu",
        "remove_odoo_enterprise",
        "resource",
        "sale",
        "sale_management",
        "sale_stock",
        "scrap_reason_code",
        "spreadsheet_dashboard_oca",
        "stock",
        "stock_account",
        "stock_landed_costs",
        "stock_picking_analytic",
        "stock_picking_invoicing",
        "web_advanced_search",
        "web_escodoo_brand",
        "web_pwa_oca",
        "web_responsive",
        "web_theme_classic",
        "web_tour",
        "account_move_tier_validation",
        "purchase_tier_validation",
        "sale_tier_validation",
    ]

    modules = env["ir.module.module"].search([
        ("name", "in", modules_to_install),
        ("state", "=", "uninstalled"),
    ])
    modules.button_install()
