from odoo import models, fields, api
import nepali_datetime


class CustomFiscalYear(models.Model):
    _inherit = 'account.fiscal.year'

    start_date_bs = fields.Char(string='Start Date BS', compute="_compute_nepali_date_start", store=True, readonly=False)
    end_date_bs = fields.Char(string='End Date BS', compute="_compute_nepali_date_end", store=True, readonly=False)

    _rec_name = 'name'

    @api.depends("date_from")
    def _compute_nepali_date_start(self):
        for record in self:
            if record.date_from:
                record.start_date_bs = nepali_datetime.date.from_datetime_date(record.date_from)
                # record.start_date_bs = nepali_datetime.datetime.strptime(record.start_date_bs, '%Y/%M/%d')
            else:
                record.start_date_bs = record.start_date_bs

    @api.depends("date_to")
    def _compute_nepali_date_end(self):
        for record in self:
            if record.date_to:
                record.end_date_bs = nepali_datetime.date.from_datetime_date(record.date_to)
                # record.end_date_bs = nepali_datetime.datetime.strptime(record.end_date_bs, '%Y/%M/%d')
            else:
                record.end_date_bs = record.end_date_bs

    @api.depends("start_date_bs")
    def _compute_english_date_start(self):
        for record in self:
            if record.start_date_bs:
                record.date_from = nepali_datetime.date.from_datetime_date(record.start_date_bs)
            else:
                record.date_from = record.date_from

    @api.depends("end_date_bs")
    def _compute_english_date_end(self):
        for record in self:
            if record.end_date_bs:
                record.date_to = nepali_datetime.date.from_datetime_date(record.date_to)
            else:
                record.date_to = record.date_to

