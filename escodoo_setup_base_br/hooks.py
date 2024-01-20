# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from odoo import api, tools, SUPERUSER_ID
from odoo.modules.module import get_module_resource


def _default_image(env):
    """
    Returns the default image encoded in base64 to be used for partners.

    Args:
        env: The Odoo environment for accessing resources.

    Returns:
        String: Default image encoded in base64.
    """
    image_path = get_module_resource('escodoo_setup_base_br', 'static/img', 'res_partner_escodoo-image.png')
    return base64.b64encode(open(image_path, 'rb').read())


def is_demo_data_installed(env):
    """
    Checks whether demo data is installed in the Odoo environment.

    Args:
        env: The Odoo environment for database access.

    Returns:
        Bool: True if demo data is installed, False otherwise.
    """
    demo_modules = env['ir.module.module'].search([('demo', '=', True)])
    return bool(demo_modules)


def _load_partner_escodoo(cr, env):
    """
    Loads the Escodoo partner into the database if not already present.

    Args:
        cr: Database cursor for executing SQL queries.
        env: The Odoo environment for database access.
    """
    escodoo_partner = env['res.partner'].search(
        [('cnpj_cpf', '=', '03.684.524/0001-37')], limit=1)
    if not escodoo_partner:
        tools.convert_file(
            cr, "escodoo_setup_base_br", "data/res_partner.xml", None,
            mode="init", noupdate=True, kind="init")
    else:
        env['ir.model.data']._update_xmlids([{
            'xml_id': 'escodoo_setup_base_br.partner_escodoo',
            'record': escodoo_partner, 'noupdate': True,
        }])


def _update_companies(env):
    """
    Updates all companies by setting the Escodoo partner as technical support.

    Args:
        env: The Odoo environment for database access.
    """
    escodoo_partner = env.ref(
        'escodoo_setup_base_br.partner_escodoo', raise_if_not_found=False)
    if escodoo_partner:
        all_company_records = env['res.company'].search([])
        all_company_records.write({'technical_support_id': escodoo_partner.id})


def _add_group_to_admin_user(env):
    """
    Adds the 'account.group_account_user' group to the admin user.

    Args:
        env: The Odoo environment for database access.
    """
    account_user_group = env.ref(
        'account.group_account_user', raise_if_not_found=False)
    admin_user_record = env.ref('base.user_admin', raise_if_not_found=False)
    if account_user_group and admin_user_record:
        admin_user_record.write({'groups_id': [(4, account_user_group.id)]})


def _update_partners(env):
    """
    Updates the names and contact information of specific partners.
    First updates partners without a parent_id, then updates partners with a parent_id.

    Args:
        env: The Odoo environment for database access.
    """
    if is_demo_data_installed(env):
        target_partner_names = ['KMEE', 'Akretion', 'Engenere']
        domain = [('name', 'ilike', name) for name in target_partner_names]
        filtered_partners = env['res.partner'].search(
            ['|'] * (len(domain) - 1) + domain)

        # First updates parent partners
        parent_index = 1
        for partner in filtered_partners.filtered(lambda p: not p.parent_id):
            partner_name = f'Escodoo Company {parent_index}'
            partner.write({
                'name': partner_name,
                'legal_name': partner_name,
                'website': 'https://www.escodoo.com.br',
                'email': 'test@escodoo.com.br',
                'image_1920': _default_image(env),
            })
            parent_index += 1

        # Then updates child partners
        for partner in filtered_partners.filtered(lambda p: p.parent_id):
            parent_name = partner.parent_id.name
            partner_name = f'{parent_name} - {partner.state_id.name}'
            partner.write({
                'name': partner_name,
                'legal_name': partner_name,
                'website': 'https://www.escodoo.com.br',
                'email': 'test@escodoo.com.br',
            })
    else:
        print('Skipping partner update because demo data is not installed.')


def post_init_hook(cr, registry):
    """
    Post-initialization hook for configuring module setup.

    Args:
        cr: Database cursor for executing SQL queries.
        registry: Odoo database registry.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    _load_partner_escodoo(cr, env)
    _update_companies(env)
    _add_group_to_admin_user(env)
    _update_partners(env)
