# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from odoo import api, tools, SUPERUSER_ID
from odoo.modules.module import get_module_resource


# def _load_partner_escodoo(cr, env):
#     """
#     Loads the Escodoo partner into the database if not already present.

#     Args:
#         cr (odoo.sql_db.Cursor): Database cursor for executing SQL queries.
#         env (odoo.api.Environment): The Odoo environment for database access.
#     """
#     escodoo_partner = env['res.partner'].search([('cnpj_cpf', '=', '03.684.524/0001-37')], limit=1)
#     if not escodoo_partner:
#         tools.convert_file(
#             cr, "escodoo_setup_base_br", "data/res_partner.xml", None,
#             mode="init", noupdate=True, kind="init")
#     else:
#         env['ir.model.data']._update_xmlids([{
#             'xml_id': 'escodoo_setup_base_br.partner_escodoo',
#             'record': escodoo_partner, 'noupdate': True,
#         }])


# def _load_default_chart_of_accounts(env):
#     """
#     Loads a default chart of accounts for companies that do not have one.

#     Args:
#         env (odoo.api.Environment): The Odoo environment for database access.
#     """
#     # Identifies companies without a chart of accounts
#     companies_without_chart = env['res.company'].search([('chart_template_id', '=', False)])

#     # Loads a default chart of accounts (adjust as necessary)
#     chart_template = env.ref('l10n_br_coa_generic.l10n_br_coa_generic_template', raise_if_not_found=False)
#     if not chart_template:
#         # If the default chart of accounts is not found, return or raise an error as necessary
#         return

#     # Associates the chart of accounts with companies that do not have one
#     for company in companies_without_chart:
#         # Sets up the environment with the specific company to correctly load the chart of accounts
#         env_cr = api.Environment(env.cr, company.id, env.context)
#         chart_template.with_env(env_cr).try_loading(company=company)


def _update_companies(env):
    """
    Updates all companies by setting the Escodoo partner as technical support.

    Args:
        env (odoo.api.Environment): The Odoo environment for database access.
    """

    all_company_records = env['res.company'].search([])

    values = {}

    escodoo_partner = env.ref('escodoo_setup.partner_escodoo', raise_if_not_found=False)

    if escodoo_partner:
        values.update({'technical_support_id': escodoo_partner.id})

    # Fiscal Data Configuration
    values.update(
        {
            'document_type_id': env.ref('l10n_br_fiscal.document_55').id,
            'sale_create_invoice_policy': 'sale_order',
            'purchase_create_invoice_policy': 'purchase_order',
        }
    )

    for company in all_company_records:
        company.write(values)


def _update_res_config_settings(env):
    """
    adad

    Args:
        env (odoo.api.Environment): The Odoo environment for database access.
    """

    config_settings = env['res.config.settings'].create({})

    config_settings.write(
        {
            'default_invoice_policy': 'order',
            'default_purchase_method': 'purchase',
            'lock_confirmed_po': True,  # Purchase
            'group_auto_done_setting': True,  # Sale
            'group_stock_multi_locations': True,  # Multiplos Locais de Estoque
            'group_stock_adv_location': True,  # Multiplos passos de Estoque
            'group_stock_tracking_owner' : True,  # Dono do Produto
            'group_stock_tracking_lot': True,  # Pacotes de Produtos
        }
    )

    config_settings.execute()


def post_init_hook(cr, registry):
    """
    Post-initialization hook for configuring module setup.

    Args:
        cr (odoo.sql_db.Cursor): Database cursor for executing SQL queries.
        registry: Odoo database registry.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    # _load_partner_escodoo(cr, env)
    _update_companies(env)
    _update_res_config_settings(env)
