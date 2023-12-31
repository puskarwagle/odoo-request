from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fynpid = fields.Many2one('account.fiscal.year', required=True, config_parameter='account.fiscal.year')
