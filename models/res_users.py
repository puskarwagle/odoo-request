# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command


class User(models.Model):
    _inherit = "res.users"

    active_branch_id = fields.Many2one(
        'service.branches',
        string='Active Branch'
    )
    active_company_id = fields.Many2one(
        'res.company',
        string='Active Company'
    )
    full_name_np = fields.Char("NameNp")
