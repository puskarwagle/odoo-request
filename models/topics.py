import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import nepali_datetime
_logger = logging.getLogger(__name__)


class Topics(models.Model):
    _name = 'service.topics'
    _description = 'Service Topics'

    service_topic_id = fields.Many2one(
        'service.topictitle',
        string='Service Topic Title',
        required=True
    )
    request_sub_topic = fields.Char(string='Request Sub-topic', required=True)

    max_amount = fields.Float(string='Maximum Amount', required=True)

    description = fields.Text(string='Description')
    file_uploads_topics = fields.Image('Upload image file')

    account_id = fields.Many2one(
        comodel_name='account.account', readonly=False,
        string=' Account',
        domain="[('account_type', '=', 'expense')]")

    fiscal_year_id = fields.Many2one('account.fiscal.year', string='Fiscal Year')

    start_date_ad = fields.Date(string='Start Date', compute="_compute_english_date_start", store=True, readonly=False)
    end_date_ad = fields.Date(string='End Date', compute="_compute_english_date_end", store=True, readonly=False)
    start_date_bs = fields.Char(string='Start Date BS', compute="_compute_nepali_date_start", store=True, readonly=False)
    end_date_bs = fields.Char(string='End Date BS', compute="_compute_nepali_date_end", store=True, readonly=False)

    @api.depends("start_date_ad")
    def _compute_nepali_date_start(self):
        for record in self:
            if record.start_date_ad:
                record.start_date_bs = nepali_datetime.date.from_datetime_date(record.start_date_ad)
            else:
                record.start_date_bs = record.start_date_bs

    @api.depends("end_date_ad")
    def _compute_nepali_date_end(self):
        for record in self:
            if record.end_date_ad:
                record.end_date_bs = nepali_datetime.date.from_datetime_date(record.end_date_ad)
            else:
                record.end_date_bs = record.end_date_bs

    @api.depends("start_date_bs")
    def _compute_english_date_start(self):
        for record in self:
            if not (record.start_date_bs and record.end_date_bs):
                record.start_date_ad = record.start_date_ad
                record.end_date_ad = record.end_date_ad
            else:
                nepali_date_start = nepali_datetime.datetime.strptime(record.start_date_bs, '%Y-%m-%d')
                nepali_date_end = nepali_datetime.datetime.strptime(record.end_date_bs, '%Y-%m-%d')
                if nepali_date_end > nepali_date_start:
                    english_date_start = nepali_date_start.to_datetime_date()
                    english_date_end = nepali_date_end.to_datetime_date()
                    record.start_date_ad = english_date_start
                    record.end_date_ad = english_date_end
                else:
                    record.start_date_ad = record.start_date_ad
                    record.end_date_ad = record.end_date_ad

    @api.depends("end_date_bs")
    def _compute_english_date_end(self):
        for record in self:
            if not (record.start_date_bs and record.end_date_bs):
                record.start_date_ad = record.start_date_ad
                record.end_date_ad = record.end_date_ad
            else:
                nepali_date_start = nepali_datetime.datetime.strptime(record.start_date_bs, '%Y-%m-%d')
                nepali_date_end = nepali_datetime.datetime.strptime(record.end_date_bs, '%Y-%m-%d')
                if nepali_date_end > nepali_date_start:
                    english_date_start = nepali_date_start.to_datetime_date()
                    english_date_end = nepali_date_end.to_datetime_date()
                    record.start_date_ad = english_date_start
                    record.end_date_ad = english_date_end
                else:
                    record.start_date_ad = record.start_date_ad
                    record.end_date_ad = record.end_date_ad

    request_state = fields.Selection([
        ('to_submit', 'To Submit'),
        ('submitted', 'Submitted'),
        ('Approved', 'Approved'),
        ('Refused', 'Refused'),
    ], string='Stage of Request', default='Approved')

    requested_by = fields.Char(
        string='Requested By',
        readonly=True,
    )
    approved_by = fields.Char(
        string='Approved By',
        readonly=True,
    )

    remaining_amount = fields.Float(
        string='Remaining Amount',
        store=True,
    )

    _rec_name = 'request_sub_topic'

    # Dont allow branch users to CREATE a new form with Approved or Refused
    # Populate requested_by and approved_by automatically
    @api.model
    def create(self, vals):
        user_groups = self.env.user.groups_id.mapped('name')

        # Check if max_amount is more than 0
        if 'max_amount' in vals and vals['max_amount'] <= 0:
            raise ValidationError("Max Amount must be more than 0.")

        # Automatically populate 'requested_by' and 'approved_by'.
        vals['requested_by'] = self.env.user.name if 'branchUsers' in user_groups else False

        record = super(Topics, self).create(vals)
        return record

    # Buttons
    def set_to_submit_topics(self):
        self.write({'request_state': 'to_submit'})

    def set_submitted_topics(self):
        self.write({'request_state': 'submitted'})

    def set_approved_topics(self):
        user = self.env.user
        _logger.info("set_approved_topics method called by user: %s", user.name)

        # Log the groups the user belongs to
        user_groups = user.groups_id.mapped('name')
        _logger.info("User's Groups: %s", user_groups)

        if 'branchUsers' not in user_groups:
            _logger.info("User is NOT in the 'branchUsers' group. Allowing state update.")
            self.write({'request_state': 'Approved'})
        else:
            _logger.info("User is in the 'branchUsers' group. Denying permission.")
            raise ValidationError("You do not have permission to set request state to 'Approved'.")

    def set_refused_topics(self):
        user = self.env.user
        _logger.info("set_refused_topics method called by user: %s", user.name)

        # Log the groups the user belongs to
        user_groups = user.groups_id.mapped('name')
        _logger.info("User's Groups: %s", user_groups)

        if 'branchUsers' not in user_groups:
            _logger.info("User is NOT in the 'branchUsers' group. Allowing state update.")
            self.write({'request_state': 'Refused'})
        else:
            _logger.info("User is in the 'branchUsers' group. Denying permission.")
            raise ValidationError("You do not have permission to set request state to 'Refused'.")
