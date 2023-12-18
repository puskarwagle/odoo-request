import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Topics(models.Model):
    _name = 'service.topics'
    _description = 'Service Topics'

    service_topic_id = fields.Many2one(
        'service.topictitle',
        string='Service Topic Title',
        required=True
    )
    request_sub_topic = fields.Char(string='Request Sub-topic')

    max_amount = fields.Integer(string='Maximum Amount', required=True)
    description = fields.Text(string='Description')
    file_uploads_topics = fields.Image('Upload image file')

    account_id = fields.Many2one(
        comodel_name='account.account', readonly=False,
        string=' Account',
        domain="[('account_type', '=', 'expense')]")

    fiscal_year_id = fields.Many2one('account.fiscal.year', string='Fiscal Year')

    start_date_ad = fields.Date(string='Start Date')
    end_date_ad = fields.Date(string='End Date')
    start_date_bs = fields.Char(string='Start Date BS')
    end_date_bs = fields.Char(string='End Date BS')

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

    remaining_amount = fields.Integer(
        string='Remaining Amount',
        compute='_compute_remaining_amount',
        store=True
    )

    _rec_name = 'request_sub_topic'

    @api.depends('max_amount')
    def _compute_remaining_amount(self):
        for topic in self:
            approved_requests = self.env['service.requests'].search([
                ('request_topic_id', '=', topic.ids),
                ('request_state', '=', 'Approved')
            ])
            used_amount = sum(approved_requests.mapped('amount'))
            topic.remaining_amount = topic.max_amount - used_amount

    # Dont allow branch users to CREATE a new form with Approved or Refused
    # Populate requested_by and approved_by automatically
    @api.model
    def create(self, vals):
        user_groups = self.env.user.groups_id.mapped('name')

        # Check if 'request_state' is present and is 'Approved' or 'Refused'
        # if 'request_state' in vals and vals['request_state'] in ['Approved', 'Refused']:
        #     raise ValidationError("Cannot set request state to 'Approved' or 'Refused' during record creation.")

        # Automatically populate 'requested_by' and 'approved_by'.
        vals['requested_by'] = self.env.user.name if 'branchUsers' in user_groups else False

        record = super(Topics, self).create(vals)
        return record

    # Dont allow branch users to WRITE a new form with Approved or Refused
    # @api.model
    # def write(self, vals):
    #     current_user = self.env.user
    #     user_groups = current_user.groups_id.mapped('name')
    #     _logger.info("User's Groups: %s", user_groups)
    #
    #     # Automatically populate 'requested_by' and 'approved_by'.
    #     vals['approved_by'] = self.env.user.name if 'centralApprovers' in user_groups else False

        # if 'request_state' in vals and vals['request_state'] in ['Approved', 'Refused']:
        #     if 'branchUsers' in user_groups:
        #         raise ValidationError(
        #             "Users in the 'branchUsers' group cannot set request state to 'Approved' or 'Refused'.")
        # result = super(Topics, self).write(vals)
        # return result

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
