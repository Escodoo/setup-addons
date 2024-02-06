 Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResUsers(models.Model):

    _inherit = "res.users"

    def action_reset_password(self):
        if self.id in [1, 2]:
            raise UserError(_('You cannot perform this action on an this user.'))
        else:
            super().action_reset_password()
