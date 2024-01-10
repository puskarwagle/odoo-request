from odoo import models, fields, api,_



class Branches(models.Model):
    _name = 'service.branches'
    _description = 'Service Branches'

    branch_name = fields.Char(string='Name', required=True)
    branch_name_np = fields.Char(string='NameNp')
    location = fields.Char(string='Location', required=True)
    status = fields.Boolean(string='Branch Status', default=True)
    phone = fields.Char(string="Phone No")
    email = fields.Char(string='Email')

    contact_person = fields.Many2many(
        'res.partner',
        string='Branch Representative',
        domain="[('is_company', '=', False)]",
    )
    users_ids = fields.Many2many(
        'res.users',
        string='Branch Employees',
        domain="[('groups_id.name', '=', 'branchUsers')]"
    )

    farm_province = fields.Many2one('location.province', string=_('Province'))
    farm_district = fields.Many2one('location.district', string=_('District'))
    farm_palika = fields.Many2one('location.palika', string=_('Palika'))
    farm_ward_no = fields.Integer(string=_('Ward No'))
    farm_tole = fields.Many2one('location.tole', string=_('Tole'))

    @api.onchange('farm_province')
    def _clear_farm_province_name(self):
        if self.farm_district.province_name != self.farm_province:
            self.farm_district = None
        if self.farm_palika.district_name != self.farm_district:
            self.farm_palika = None

    @api.onchange('farm_district')
    def _clear_farm_district_name(self):
        if self.farm_district.district_name != self.farm_district:
            self.farm_palika = None


    #unused fields
    position = fields.Char(string='Position')
    mobile_no = fields.Char(string="Mobile No")



    _rec_name = 'branch_name'


class User(models.Model):
    _inherit = 'res.users'

    branch_ids = fields.Many2many('service.branches', string='Branches')
