# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
import odoo

def post_init_hook(cr, registry):
    """
    Este método é chamado após a instalação do módulo.
    Ele define pt_BR como o idioma de todos os usuários.
    Também desativa os outros idiomas.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Aplicar pt_BR a todos os usuários
    all_users = env['res.users'].search([])
    all_users.write({'lang': 'pt_BR'})

    # Aplicar pt_BR a todos os usuários
    all_users = env['res.partner'].search([])
    all_users.write({'lang': 'pt_BR'})

    # Desativar outros idiomas
    other_langs = env['res.lang'].search([('code', '!=', 'pt_BR')])
    other_langs.write({'active': False})
