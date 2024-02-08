import base64
import random
import string
from odoo import api, tools, SUPERUSER_ID
from odoo.modules.module import get_module_resource


def generate_random_password(length=48):
    """Generate a random password using a mix of upper and lower case letters and numbers."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


def get_default_image(env):
    """Return the default image encoded in base64."""
    image_path = get_module_resource('escodoo_setup', 'static/src/img', 'escodoo_badge.svg')
    return base64.b64encode(open(image_path, 'rb').read()) if image_path else False


def update_companies(env):
    """Update all companies with the Escodoo partner logo."""
    all_companies = env['res.company'].search([])
    logo_path = get_module_resource('escodoo_setup', 'static/src/img', 'your_company_logo.png')
    logo_image = base64.b64encode(open(logo_path, 'rb').read()) if logo_path else False

    for company in all_companies:
        company.write({'logo': logo_image} if logo_image else {})


def update_res_config_settings(env):
    """Update 'pwa_icon' in res.config.settings."""
    config_settings = env['res.config.settings'].create({})
    values = {
        'user_default_rights': True,
        'external_report_layout_id': env.ref("web.external_layout_background"),
        'pwa_icon': get_default_image(env) if get_default_image(env) else None
    }
    config_settings.write(values)
    config_settings.execute()


def add_group_to_admin_user(env):
    """Add 'account.group_account_user' group to the admin user."""
    account_user_group = env.ref('account.group_account_user', raise_if_not_found=False)
    admin_user = env.ref('base.user_admin', raise_if_not_found=False)
    if account_user_group and admin_user:
        admin_user.write({'groups_id': [(4, account_user_group.id)]})


def post_init_hook(cr, registry):
    """Post-initialization hook for module setup."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    update_companies(env)
    update_res_config_settings(env)
    add_group_to_admin_user(env)

    db_name = tools.config['db_name'].upper()
    env["ir.config_parameter"].set_param("auth_signup.invitation_scope", "b2b")
    env["ir.config_parameter"].set_param("pwa.manifest.background_color", "#7C7BAD")
    env["ir.config_parameter"].set_param("pwa.manifest.name", f"Odoo Online {db_name}")
    env["ir.config_parameter"].set_param("pwa.manifest.short_name", f"Odoo {db_name}")
    env["ir.config_parameter"].set_param("pwa.manifest.theme_color", "#FFFFFF")

    admin_user = env["res.users"].browse(2)
    admin_user.write({"name": "Administrador Escodoo", "password": generate_random_password()})