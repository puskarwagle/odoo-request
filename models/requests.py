import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Requests(models.Model):
    _name = 'service.requests'
    _description = 'Service Requests'

    request_title = fields.Char(string='Request Title')

    req_topic_links = fields.One2many(
        'service.reqtopiclink',
        'request_id',
        string='Request Topic Links',
    )

    select_branch = fields.Many2one(
        'service.branches',
        required=True,
        string='Branch'
    )

    description = fields.Text(string='Description')

    request_state = fields.Selection([
        ('tosubmit', 'To Submit'),
        ('submitted', 'Submitted'),
        ('resubmit', 'Resubmit'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ], string='Stage of Request', default='submitted')

    newreq_attachments = fields.One2many(
        'ir.attachment',
        'res_id',
        domain=[('res_model', '=', 'service.requests')],
        string='Add Attachments',
    )

    @api.constrains('newreq_attachments')
    def check_file_size_limit(self):
        max_file_size = 5 * 1024 * 1024  # 5 MB

        for attachment in self:
            if attachment.datas and len(attachment.datas) > max_file_size:
                raise ValidationError("File size cannot exceed 5 MB.")

    requestdate_ad = fields.Datetime(string='Request Date AD')
    requestdate_bs = fields.Char(string='Request Date BS')

    requested_by = fields.Char(
        string='Requested By',
        readonly=True,
        tracking=True
    )
    approved_by = fields.Char(
        string='Approved By',
        readonly=True,
    )

    remarks = fields.Text(string='Remarks',tracking=True)

    # Dont allow branch users to CREATE a new form with Approved or Refused
    # Populate requested_by and approved_by automatically
    @api.model
    def create(self, vals):
        # Check if 'request_state' is present and is 'Approved' or 'Refused'
        if 'request_state' in vals and vals['request_state'] in ['Approved', 'Refused']:
            raise ValidationError("Cannot set request state to 'Approved' or 'Refused' during record creation.")

        # Automatically populate 'requested_by'
        user_groups = self.env.user.groups_id.mapped('name')
        vals['requested_by'] = self.env.user.name if 'branchUsers' in user_groups else False
        vals['requestdate_ad'] = fields.Datetime.now()

        record = super(Requests, self).create(vals)
        return record

    # Write method to enforce access control
    def write(self, values):
        # Check if the user belongs to 'branchUsers' or 'centralApprovers'
        user_groups = self.env.user.groups_id.mapped('name')

        # Users belonging to 'branchUsers'
        if 'branchUsers' in user_groups:
            # Users can only edit the request_state to 'tosubmit' or 'submitted'
            if 'request_state' in values and values['request_state'] not in ['tosubmit', 'submitted']:
                raise ValidationError(
                    "Users in 'branchUsers' group can only set request_state to 'tosubmit' or 'submitted'.")

            # Users cannot edit the 'remarks' field
            if 'remarks' in values:
                raise ValidationError("Users in 'branchUsers' group cannot edit the 'remarks' field.")

        # Users belonging to 'centralApprovers'
        elif 'centralApprovers' in user_groups:
            # Users can only edit the 'request_state' and 'remarks' fields
            allowed_fields = {'request_state', 'remarks'}
            if not set(values.keys()).issubset(allowed_fields):
                raise ValidationError(
                    "Users in 'centralApprovers' group can only edit 'request_state' and 'remarks' fields.")

            # 'centralApprovers' users can only set 'request_state' to 'Approved' or 'Refused'
            if 'request_state' in values and values['request_state'] not in ['approved', 'refused', 'resubmit']:
                raise ValidationError(
                    "Users in 'centralApprovers' group can only set request_state to 'Approved', 'Refused' or 'Resubmit'.")

            if 'Approved' in values.get('request_state', []):
                values['approved_by'] = self.env.user.name

        # Call the super method to perform the common write operation
        result = super(Requests, self).write(values)
        return result

    # Buttons
    def set_to_submit_new_requests(self):
        self.write({'request_state': 'tosubmit'})

    def set_submitted_new_requests(self):
        self.write({'request_state': 'submitted'})

    def set_resubmitted_new_requests(self):
        self.write({'request_state': 'resubmit'})

    def set_approved_new_requests(self):
        self.write({'request_state': 'Approved'})

    def set_refused_new_requests(self):
        self.write({'request_state': 'Refused'})

    # Send email when record created
    # @api.model
    # def create(self, values):
    #     record = super(Requests, self).create(values)
    #     if 'request_state' in values and values.get('request_state') == 'submitted':
    #         record.send_email_to_central_approvers()
    #     elif 'request_state' in values and values.get('request_state') in ['Refused', 'Approved']:
    #         record.send_email_to_requested_by_user()
    #     return record

    # Send email when record state is changed
    # @api.model
    # def write(self, values):
    #     result = super(Requests, self).write(values)
    #     if 'request_state' in values:
    #         if self.request_state == 'submitted':
    #             self.send_email_to_central_approvers()
    #         elif self.request_state in ['Refused', 'Approved']:
    #             self.send_email_to_requested_by_user()
    #     return result

    # def send_email_to_central_approvers(self):
    #     central_approvers_group = self.env['res.groups'].browse(25)
    #     central_approvers_emails = central_approvers_group.users.mapped('email')
    #     logger = logging.getLogger(__name__)
    #     logger.info(f"Email addresses of centralapprovers: {central_approvers_emails}")

    # def send_email_to_requested_by_user(self):
    #     requested_by_email = self.requested_by.email
    #     logger = logging.getLogger(__name__)
    #     logger.info(f"Email address of requested user: {requested_by_email}")
