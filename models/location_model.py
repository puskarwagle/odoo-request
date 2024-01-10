from odoo import models, fields,api,_

class LocationProvince(models.Model):
    # _inherit = 'fis.base.model'
    _name = 'location.province'
    _description = 'Province Name'
    _rec_name = 'name_np'

    name = fields.Char(string=_('Name'))
    name_np = fields.Char(string=_('Name NEP'))
    reference_id = fields.Char("Reference ID")
    reference_code = fields.Char("Reference Code")
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        store=True,
        readonly=True
    )

    def name_get(self):
        result = []
        if self._context["lang"]=='ne_NP':
            for rec in self:
                result.append((rec.id, rec.name_np))
        else:
            for rec in self:
                result.append((rec.id, rec.name))
        return result

class LocationDistrict(models.Model):
    # _inherit = 'fis.base.model'
    _name = 'location.district'
    _description = 'Location District Information'
    _rec_name = 'district_name_np'

    province_name = fields.Many2one('location.province',string=_('Province'))
    district_name = fields.Char(string=_('District'))
    district_name_np = fields.Char(string=_('District(NEP)'))
    reference_id = fields.Char("Reference ID")
    reference_code = fields.Char("Reference Code")
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        store=True,
        readonly=True
    )
    def name_get(self):
        result = []
        if self._context["lang"]=='ne_NP':
            for rec in self:
                result.append((rec.id, rec.district_name_np))
        else:
            for rec in self:
                result.append((rec.id, rec.district_name))
        return result
    
class LocationPalika(models.Model):
    # _inherit = 'fis.base.model'
    _name = 'location.palika'
    _description = 'Location Palika Information'
    _rec_name = 'palika_name_np'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        store=True,
        readonly=True
    )
    district_name = fields.Many2one('location.district',string=_('District'))
    palika_name = fields.Char(string=_('Palika'))
    palika_name_np = fields.Char(string=_('Palika(NEP)'))
    reference_id = fields.Char("Reference ID")
    reference_code = fields.Char("Reference Code")
    type = fields.Char("Type",compute="_compute_palika_type")
    type_np = fields.Char("Type NEP",compute="_compute_palika_type")

    def _compute_palika_type(self):
        for record in self:
            type = record.palika_name.split(' ')[-1]
            if 'rural municipality' in record.palika_name.lower() or 'rural minicipality' in record.palika_name.lower() or 'rural muncipalicity' in record.palika_name.lower() or 'rural mumcipality' in  record.palika_name.lower():
                record.type = 'Palika'
                record.type_np = 'पालिका'
            elif 'municipality' in record.palika_name.lower() or 'municipaltiy' in record.palika_name.lower() or 'muncipality' in record.palika_name.lower() or 'municipaity' in record.palika_name.lower():
                record.type = 'Municipal'
                record.type_np = 'नगरपालिका'
            elif 'submetropolitiancity' in record.palika_name.lower() or 'sub-metropolitan' in record.palika_name.lower() or 'Sub-Metropolitan' in record.palika_name:
                record.type = 'Sub Metropolitiancity Municipal'
                record.type_np = 'उपमहानगरपालिका'
            elif 'smc' in record.palika_name.lower():
                record.type = 'Sub Metropolitiancity Municipal'
                record.type_np = 'उपमहानगरपालिका'
            elif 'metropolian' in record.palika_name.lower() or 'metropolitian' in record.palika_name.lower() or 'metropolitan' in record.palika_name.lower():
                record.type = 'Metropolitiancity Municipal'
                record.type_np = 'महानगरपालिका'
            else:
                record.type = 'abc'
                record.type_np = 'abc'
            

    def name_get(self):
        result = []
        if self._context["lang"]=='ne_NP':
            for rec in self:
                result.append((rec.id, rec.palika_name_np))
        else:
            for rec in self:
                result.append((rec.id, rec.palika_name))
        return result


class PalikaTole(models.Model):
    # _inherit = 'fis.base.model'
    _name = 'location.tole'
    _description = 'Location Tole Information'
    _rec_name = 'tole_name_np'

    palika_name = fields.Many2one('location.palika', string=_('Palika'), empty_text="Palika")
    tole_name = fields.Char(string=_('Tole'))
    tole_name_np = fields.Char(string=_('Tole(NEP)'))
    ward_number = fields.Integer(string=_('Ward Number'))
    reference_id = fields.Char("Reference ID")
    reference_code = fields.Char("Reference Code")
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        store=True,
        readonly=True
    )

    def name_get(self):
        result = []
        if self._context["lang"]=='ne_NP':
            for rec in self:
                result.append((rec.id, rec.tole_name_np))
        else:
            for rec in self:
                result.append((rec.id, rec.tole_name))
        return result

