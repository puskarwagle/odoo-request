from odoo import models, fields, _


class CustomFiscalYear(models.Model):
    _inherit = 'account.fiscal.year'

    start_date_bs = fields.Char(string='Start Date BS')
    end_date_bs = fields.Char(string='End Date BS')
