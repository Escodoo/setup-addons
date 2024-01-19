# -*- coding: utf-8 -*-
from odoo import api, tools, SUPERUSER_ID


def is_demo_data_installed(env):
    """
    Checks if demo data is installed in the Odoo environment.
    This is determined by checking if any module has demo data enabled.
    """
    demo_modules = env['ir.module.module'].search([('demo', '=', True)])
    return bool(demo_modules)


def _load_partner_escodoo(cr, env):
    """
    Loads the Escodoo partner if not already present in the database.
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
    Updates all companies with the Escodoo partner as technical support.
    """
    escodoo_partner = env.ref(
        'escodoo_setup_base_br.partner_escodoo', raise_if_not_found=False)
    if escodoo_partner:
        all_company_records = env['res.company'].search([])
        all_company_records.write({'technical_support_id': escodoo_partner.id})


def _add_group_to_admin_user(env):
    """
    Adds the 'account.group_account_user' group to the admin user.
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
    """
    if is_demo_data_installed(env):
        target_partner_names = ['KMEE', 'Akretion', 'Engenere']
        domain = [('name', 'ilike', name) for name in target_partner_names]
        filtered_partners = env['res.partner'].search(
            ['|'] * (len(domain) - 1) + domain)

        # Primeiro atualiza parceiros pais
        parent_index = 1
        for partner in filtered_partners.filtered(lambda p: not p.parent_id):
            partner_name = f'Escodoo Empresa {parent_index}'
            partner.write({
                'name': partner_name,
                'legal_name': partner_name,
                'website': 'https://www.escodoo.com.br',
                'email': 'teste@escodoo.com.br',
            })
            parent_index += 1

        # Depois atualiza parceiros filhos
        for partner in filtered_partners.filtered(lambda p: p.parent_id):
            parent_name = partner.parent_id.name
            partner_name = f'{parent_name} - {partner.state_id.name}'
            partner.write({
                'name': partner_name,
                'legal_name': partner_name,
                'website': 'https://www.escodoo.com.br',
                'email': 'teste@escodoo.com.br',
            })
    else:
        print('Skipping partner update because demo data is not installed.')


def post_init_hook(cr, registry):
    """
    Post-initialization hook for setting up module configuration.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    _load_partner_escodoo(cr, env)
    _update_companies(env)
    _add_group_to_admin_user(env)
    _update_partners(env)
