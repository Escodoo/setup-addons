# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Escodoo Setup',
    'description': """
        Escodoo Setup""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Escodoo',
    'website': 'https://github.com/Escodoo/setup-addons',
    'depends': [
        'access_restricted',
        'auth_admin_passkey',
        'auth_signup_block_admin_password_reset',
        'base_address_city',
        'base_address_extended',
        'base_automation',
        'base_setup',
        # 'base_technical_features',
        'date_range',
        'remove_odoo_enterprise',
        'web_advanced_search',
        'web_pwa_oca',
        'web_responsive',
        'web_escodoo_brand',
        'web_tour',
    ],
    'data': [
        'data/res_partner.xml',
        'data/res_users.xml',
        'data/res_company.xml'
    ],
    'demo': [
    ],
    'post_init_hook': 'post_init_hook',
}
