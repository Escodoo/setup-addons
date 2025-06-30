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
        "account_move_template",
        "account_payment_partner",
        "account_reconcile_oca",
        "account_statement_import_ofx",
        "auth_admin_passkey",
        "base",
        "base_address_extended",
        "base_automation",
        "base_name_search_improved",
        "base_setup",
        "base_technical_features",
        "bi_sql_editor",
        "contacts",
        "contract",
        "crm",
        "date_range",
        "date_range_account",
        "delivery",
        "delivery_carrier_partner",
        "disable_odoo_online",
        "hr",
        "hr_contract",
        "hr_employee_age",
        "hr_skills",
        "hr_timesheet",
        "hr_timesheet_sheet",
        "mail_debrand",
        "mis_builder",
        "mis_builder_analytic"
        "mis_builder_budget",
        "mis_builder_cash_flow",
        "mis_template_financial_report",
        "partner_contact_access_link",
        "password_security",
        "portal",
        "product",
        "product_expiry",
        "purchase",
        "purchase_default_terms_conditions",
        "purchase_order_line_menu",
        "queue_job",
        "remove_odoo_enterprise",
        "report_xlsx",
        "resource",
        "sale",
        "sale_management",
        "sale_stock",
        "scrap_reason_code",
        "server_action_mass_edit",
        "session_db",
        "spreadsheet_dashboard_oca",
        "stock",
        "stock_account",
        "stock_landed_costs",
        "stock_picking_analytic",
        "stock_picking_invoicing",
        "web_advanced_search",
        "web_dialog_size",
        "web_escodoo_brand",
        "web_listview_range_select",
        "web_pwa_oca",
        "web_responsive",
        "web_refresher",
        "web_search_with_and",
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
