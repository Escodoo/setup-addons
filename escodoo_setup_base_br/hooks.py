# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from odoo import api, tools, SUPERUSER_ID
from odoo.modules.module import get_module_resource


def demo_data_installed(env):
    """Check if demo data is installed."""
    demo_modules = env['ir.module.module'].search([('demo', '=', True)])
    return bool(demo_modules)


def _update_demo_partners(env):
    """Update partner names and contact information."""
    if demo_data_installed(env):
        target_partners = ['KMEE', 'Akretion', 'Engenere']
        partners = env['res.partner'].search([('name', 'ilike', '|'.join(target_partners))])
        for index, partner in enumerate(partners.filtered(lambda p: not p.parent_id), start=1):
            partner_name = f'Escodoo Company {index}'
            partner.write({
                'name': partner_name,
                'legal_name': partner_name,
                'website': 'https://escodoo.com.br',
                'email': 'test@escodoo.com.br',
                'image_1920': get_default_image(env)
            })
        for partner in partners.filtered(lambda p: p.parent_id):
            partner_name = f'{partner.parent_id.name} - {partner.state_id.name}'
            partner.write({
                'name': partner_name,
                'legal_name': partner_name,
                'website': 'https://escodoo.com.br',
                'email': 'test@escodoo.com.br'
            })
    else:
        print('Skipping partner update because demo data is not installed.')


def _set_company_permissions(env):

    if demo_data_installed(env):
        user_system_manager = env.ref('escodoo_setup.user_system_manager', raise_if_not_found=False)
        companies = env['res.company'].search([])
        user_system_manager.write({'company_ids': [(6, 0, companies.ids)]})
        return


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
            # 'sale_create_invoice_policy': 'sale_order',
            # 'purchase_create_invoice_policy': 'purchase_order',
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
            'group_stock_tracking_owner': True,  # Dono do Produto
            'group_stock_tracking_lot': True,  # Pacotes de Produtos
            'group_analytic_accounting': True, # Ativa contabilidade analitica
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
    _update_companies(env)
    _update_res_config_settings(env)
    _set_company_permissions(env)
    _update_demo_partners(env)
