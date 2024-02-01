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
    image = False
    image_path = get_module_resource('escodoo_setup_base_br', 'static/img', 'escodoo_badge.png')
    if image_path:
        image = base64.b64encode(open(image_path, 'rb').read())
    return image


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


def _load_default_chart_of_accounts(env):
    """
    Loads a default chart of accounts for companies that do not have one.

    Args:
        env: The Odoo environment for database access.
    """
    # Identifies companies without a chart of accounts
    companies_without_chart = env['res.company'].search([('chart_template_id', '=', False)])

    # Loads a default chart of accounts (adjust as necessary)
    chart_template = env.ref('l10n_br_coa_generic.l10n_br_coa_generic_template', raise_if_not_found=False)
    if not chart_template:
        # If the default chart of accounts is not found, return or raise an error as necessary
        return

    # Associates the chart of accounts with companies that do not have one
    for company in companies_without_chart:
        # Sets up the environment with the specific company to correctly load the chart of accounts
        env_cr = api.Environment(env.cr, company.id, env.context)
        chart_template.with_env(env_cr).try_loading(company=company)


def _update_companies(env):
    """
    Updates all companies by setting the Escodoo partner as technical support.

    Args:
        env: The Odoo environment for database access.
    """

    all_company_records = env['res.company'].search([])

    escodoo_partner = env.ref('escodoo_setup_base_br.partner_escodoo', raise_if_not_found=False)

    company_logo_path = get_module_resource('escodoo_setup_base_br', 'static/img', 'your_company_logo.png')
    company_logo_image = base64.b64encode(open(company_logo_path, 'rb').read()) if company_logo_path else False

    values = {
        'country_id': env.ref('base.br').id,
    }

    if company_logo_image:
        values.update({'logo': company_logo_image})

    if escodoo_partner:
        values.update({'technical_support_id': escodoo_partner.id})

    for company in all_company_records:
        company.write(values)

    # falta o regime pis/cofins
    # falta o regime do icms
    # ativar RIPI


def _update_res_config_settings(env):
    """
    Updates the 'pwa_icon' field in the res.config.settings of the Odoo environment
    by creating or updating an attachment for the icon image.

    Args:
        env: The Odoo environment for database access.
    """

    # Obter a imagem padrão codificada em base64
    image_base64 = _default_image(env)
    if image_base64:
        config_settings = env['res.config.settings'].create({})
        config_settings.write({'pwa_icon': image_base64})
        config_settings.execute()


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
    # _update_res_config_settings(env)
    _load_default_chart_of_accounts(env)
    _add_group_to_admin_user(env)
    _update_partners(env)

    # Configurar o ambiente Odoo
    config = tools.config

    # Obter o nome da base de dados
    db_name = config['db_name']

    db_name_uppercase = db_name.upper()

    env["ir.config_parameter"].set_param("auth_signup.invitation_scope", "b2b")
    env["ir.config_parameter"].set_param("pwa.manifest.background_color", "#7C7BAD")
    env["ir.config_parameter"].set_param("pwa.manifest.name", f"Odoo Online {db_name_uppercase}")
    env["ir.config_parameter"].set_param("pwa.manifest.short_name", f"Odoo {db_name_uppercase}")
    env["ir.config_parameter"].set_param("pwa.manifest.theme_color", "#FFFFFF")
    # env["ir.config_parameter"].set_param("support_company", "Escodoo Sistemas")
    # env["ir.config_parameter"].set_param("support_company_url", "https://www.escodoo.com.br")
    # env["ir.config_parameter"].set_param("support_branding_color", "#fff")
    # env["ir.config_parameter"].set_param("support_email", "suporte@escodoo.com.br")
    # env["ir.config_parameter"].set_param("support_release", "14.0")
