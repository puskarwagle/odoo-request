from odoo import models, fields, api


class Branches(models.Model):
    _name = 'service.branches'
    _description = 'Service Branches'

    branch_name = fields.Char(string='Branch Name', required=True)
    location = fields.Char(string='Location', required=True)
    status = fields.Boolean(string='Branch Status', default=True)
    phone = fields.Char(string="Phone No")
    email = fields.Char(string='Email')
    contact_person = fields.Char(string='Contact Person')
    position_of_contact_person = fields.Char(string='Position')
    mobile_no = fields.Char(string="Mobile No")

    _rec_name = 'branch_name'
