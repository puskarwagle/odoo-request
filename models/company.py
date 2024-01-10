from odoo import fields, models, api, _


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company"]

    comp_province = fields.Many2one('location.province', string=_('Province'))
    comp_district = fields.Many2one('location.district', string=_('District'))
    comp_palika = fields.Many2one('location.palika', string=_('Palika'))
    comp_ward_no = fields.Integer(string=_('Ward No'))
    comp_tole = fields.Many2one('location.tole', string=_('Tole'))
    full_address = fields.Char("Address", compute="_compute_full_address")
    full_name_np = fields.Char("NameNp")
    company_code = fields.Char(string=_('Company Code'), size=15)
    fax_number = fields.Char(string=_('Fax Number'),required=False)
    pan_number = fields.Char(string=_('PAN Number'),required=False)
    def _compute_full_address(self):
        for record in self:
            temp = ""
            if record.palika:
                temp += record.palika.palika_name
            if record.ward_no:
                temp += ' - ' + record.ward_no + ', '
            if record.district:
                temp += record.district.district_name + ', '
            if record.province:
                temp += record.province.name

            record.full_address = temp
    @api.onchange('comp_province')
    def _clear_comp_province_name(self):
        if self.comp_district.province_name != self.comp_province:
            self.comp_district = None
        if self.comp_palika.district_name != self.comp_district:
            self.comp_palika = None

    @api.onchange('comp_district')
    def _clear_farm_district_name(self):
        if self.comp_district.district_name != self.comp_district:
            self.comp_palika = None