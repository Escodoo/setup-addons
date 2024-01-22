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
    image_path = get_module_resource('escodoo_setup_base_br', 'static/img', 'escodoo_icon.png')
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


def _load_default_chart_of_accounts(env):
    """
    Carrega um plano de contas padrão para empresas que não têm um plano de contas.

    Args:
        env: O ambiente Odoo para acesso ao banco de dados.
    """
    # Identifica as empresas sem um plano de contas
    companies_without_chart = env['res.company'].search([('chart_template_id', '=', False)])

    # Carrega um plano de contas padrão (ajuste conforme necessário)
    chart_template = env.ref('l10n_br_coa_generic.l10n_br_coa_generic_template', raise_if_not_found=False)
    if not chart_template:
        # Se o plano de contas padrão não for encontrado, retorne ou gere um erro conforme necessário
        return

    # Associa o plano de contas às empresas sem um
    for company in companies_without_chart:
        # Configura o ambiente com a empresa específica para carregar corretamente o plano de contas
        env_cr = api.Environment(env.cr, company.id, env.context)
        chart_template.with_env(env_cr).try_loading(company=company)


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
        all_company_records.write(
            {
                'technical_support_id': escodoo_partner.id,
            }
        )


# def _update_res_config_settings(env):
#     """
#     Updates the 'pwa_icon' field in the res.config.settings of the Odoo environment
#     by creating or updating an attachment for the icon image.

#     Args:
#         env: The Odoo environment for database access.
#     """
#     # Nome do anexo para identificação
#     attachment_name = "escodoo_pwa_icon.png"

#     # Obter a imagem padrão codificada em base64
#     image_base64 = _default_image(env)

#     # Busca por um anexo existente com o mesmo nome
#     existing_attachment = env['ir.attachment'].search([('name', '=', attachment_name)], limit=1)

#     # Se não existir um anexo, cria um novo
#     if not existing_attachment:
#         # Cria o anexo no Odoo
#         attachment = env['ir.attachment'].create({
#             'name': attachment_name,
#             'type': 'binary',
#             'datas': image_base64,
#             'store_fname': attachment_name,
#             'mimetype': 'image/png',
#         })

#         # Obtém a URL do anexo
#         attachment_url = f'/web/content/{attachment.id}/{attachment_name}'
#     else:
#         # Se já existir um anexo, atualiza com a nova imagem
#         existing_attachment.write({'datas': image_base64})
#         # Obtém a URL do anexo existente
#         attachment_url = f'/web/content/{existing_attachment.id}/{attachment_name}'

#     # Obtém o registro de configurações atuais
#     config_settings = env['res.config.settings'].create({})

#     # Escreve a URL do anexo no campo 'pwa_icon' das configurações
#     config_settings.write({'pwa_icon': attachment_url})

#     # Aplica as configurações
#     config_settings.execute()


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

    env["ir.config_parameter"].set_param("auth_signup.invitation_scope", "b2b")
    env["ir.config_parameter"].set_param("pwa.manifest.background_color", "#7C7BAD")
    env["ir.config_parameter"].set_param("pwa.manifest.name", "Odoo Escodoo")
    env["ir.config_parameter"].set_param("pwa.manifest.theme_color", "#7C7BAD")
    env["ir.config_parameter"].set_param("support_company", "Escodoo Sistemas")
    env["ir.config_parameter"].set_param("support_company_url", "https://www.escodoo.com.br")
    env["ir.config_parameter"].set_param("support_branding_color", "#7C7BAD")
    env["ir.config_parameter"].set_param("support_email", "suporte@escodoo.com.br")
    env["ir.config_parameter"].set_param("support_release", "14.0")
