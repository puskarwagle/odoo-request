from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fynpid = fields.Many2one('account.fiscal.year', config_parameter='account.fiscal.year')
