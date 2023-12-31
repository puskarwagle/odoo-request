import base64
import logging
from odoo import models, fields, api, _
import nepali_datetime
from odoo.exceptions import ValidationError


class Requests(models.Model):
    _name = 'service.requests'
    _description = 'Service Requests'

    _logger = logging.getLogger(__name__)

    request_title = fields.Char(string='Request Title', default='Petty Cash')

    req_topic_links = fields.One2many(
        'service.reqtopiclink',
        'request_id',
        string='Request Topic Links',
        required=True,
    )

    select_branch = fields.Many2one(
        'service.branches',
        required=True,
        string='Branch',
        default=lambda self: self.env.user.branch_ids and self.env.user.branch_ids[0].id or False
    )

    description = fields.Text(string='Description')

    request_state = fields.Selection([
        ('tosubmit', 'To Submit'),
        ('submitted', 'Submitted'),
        ('resubmit', 'Resubmit'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ], string='Stage of Request', default='tosubmit')

    newreq_attachments = fields.One2many(
        'ir.attachment',
        'res_id',
        domain=[('res_model', '=', 'service.requests')],
        string='Add Attachments',
    )

    requestdate_ad = fields.Date(string='Request Date')
    requestdate_bs = fields.Char(string='Request Date(BS)', compute="_compute_req_nep_date")
    approved_date_ad = fields.Date(string='Approved Date')
    approved_date_bs = fields.Char(string='Approved Date(BS)', compute="_compute_app_nep_date")

    requested_by = fields.Char(
        string='Request By',
        readonly=True,
        tracking=True
    )
    approved_by = fields.Char(
        string='Approved By',
        readonly=True,
    )
    secure_sequence_id = fields.Many2one(
        'ir.sequence',
        help='Sequence to use to ensure the securisation of data',
        check_company=True,
        readonly=True,
        copy=False
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        store=True,
        readonly=True
    )

    fiscal_year_id = fields.Many2one(
        'account.fiscal.year',
        string='Fiscal Year',
        default=lambda self: self.get_default_fiscal_year()
    )

    def get_default_fiscal_year(self):
        param_value = self.env['ir.config_parameter'].sudo().get_param('account.fiscal.year')
        fiscal_year = self.env['account.fiscal.year'].search([('id', '=', param_value)], limit=1)
        return fiscal_year.id if fiscal_year else False

    journal_created = fields.Boolean(string='Journal Entry Created', default=False)
    account_move_id = fields.Many2one('account.move', string='Related Journal Entry')
    is_centraluser = fields.Boolean(compute='_compute_is_centraluser', default=False, store=False)

    remarks = fields.Text(string='Remarks', tracking=True)

    # Compute method to determine if the user is a central user
    def _compute_is_centraluser(self):
        for record in self:
            user = self.env.user
            record.is_centraluser = user.has_group('service-approval.group_central_users')

    def name_get(self):
        result = []
        for request in self:
            name = f"{request.secure_sequence_id.name}/{request.secure_sequence_id.id}/{request.request_title or 'Request'}"
            result.append((request.id, name))
        return result

    def _create_secure_sequence(self):
        """This function creates a secure sequence for the request if not already present."""
        for request in self:
            if not request.secure_sequence_id:
                fiscal_year = request.fiscal_year_id.name

                now = fields.Datetime.now()
                hour = now.strftime('%H')
                minute = now.strftime('%M')
                second = now.strftime('%S')

                seq_name = f'REQ/{fiscal_year}/{hour}{minute}{second}'
                secure_sequence = self.env['ir.sequence'].search([('name', '=', seq_name)], limit=1)
                if not secure_sequence:
                    seq_vals = {
                        'name': seq_name,
                        'code': f'SECURE{fiscal_year}-{hour}-{minute}-{second}',
                        'implementation': 'no_gap',
                        'prefix': '',
                        'suffix': '',
                        'padding': 0,
                        'company_id': request.company_id.id
                    }
                    secure_sequence = self.env['ir.sequence'].create(seq_vals)

                # Update the secure_sequence_id field in the request
                request.secure_sequence_id = secure_sequence

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
            # allowed_fields = {'request_state', 'remarks', 'journal_created'}
            # if not set(values.keys()).issubset(allowed_fields):
            #     raise ValidationError(
            #         "Users in 'centralApprovers' group can only edit 'request_state' and 'remarks' fields.")

            # 'centralApprovers' users can only set 'request_state' to 'Approved' or 'Refused'
            if 'request_state' in values and values['request_state'] not in ['approved', 'refused', 'resubmit']:
                raise ValidationError(
                    "Users in 'centralApprovers' group can only set request_state to 'Approved', 'Refused' or 'Resubmit'.")

            if 'approved' in values.get('request_state', []):
                values['approved_by'] = self.env.user.name

            # if 'request_state' in values and values['request_state'] in ['refused', 'resubmit']:
            #     if 'remarks' not in values:
            #         raise ValidationError(
            #             "Users in 'centralApprovers' group must fill in the 'remarks' field when request_state is 'refused' or 'resubmit'.")

            values['approved_date_ad'] = fields.Datetime.now()

        # Call the super method to perform the common write operation
        result = super(Requests, self).write(values)
        return result

    @api.depends("requestdate_ad")
    def _compute_req_nep_date(self):
        for record in self:
            if record.requestdate_ad:
                record.requestdate_bs = nepali_datetime.date.from_datetime_date(record.requestdate_ad)
            else:
                record.requestdate_bs = record.requestdate_bs

    @api.depends("approved_date_ad")
    def _compute_app_nep_date(self):
        for record in self:
            if record.approved_date_ad:
                record.approved_date_bs = nepali_datetime.date.from_datetime_date(record.approved_date_ad)
            else:
                record.approved_date_bs = record.approved_date_bs

    # Buttons
    def set_to_submit_new_requests(self):
        self.write({'request_state': 'tosubmit'})

    def set_submitted_new_requests(self):
        self.write({'request_state': 'submitted'})

    def set_resubmitted_new_requests(self):
        self._validate_remarks_required()
        self.write({'request_state': 'resubmit'})

    def set_refused_new_requests(self):
        self._validate_remarks_required()
        self.write({'request_state': 'refused'})

    def _validate_remarks_required(self):
        """Validation method to check if 'remarks' field is filled."""
        user_groups = self.env.user.groups_id.mapped('name')

        if 'centralApprovers' in user_groups:
            if not self.remarks:
                raise ValidationError("Remarks field must be filled for resubmitting or refusing requests.")

    def set_approved_new_requests(self):
        self.write({'request_state': 'approved'})

    def print_approved_request(self):
        return

    def open_new_journal_entry_form(self):
        current_record = self.env['service.requests'].browse(self.id)
        self._logger.info("Arguments received in open_new_journal_entry_form: %s", locals())
        action = self.env.ref('account.action_move_journal_line').read()[0]

        action.update({
            'view_mode': 'form',
            'views': [(False, 'form')],
            # 'target': 'new',
        })

        # List for debit entries
        line_ids_default = [
            (0, 0, {
                'account_id': link.topic_account_id.id,
                'name': link.topic_id.request_sub_topic,
                'debit': link.amount_monetary,
                'balance': link.amount_monetary,
                # 'currency_id': 2
            })
            for link in current_record.req_topic_links
        ]

        # Additional tuple for credit entry
        accounts_info = self.env['account.account'].search([('code', '=', 'PETTYCPS0001')], limit=1)

        if accounts_info:
            account_info_id = accounts_info.id

        credit_entry = (0, 0, {
            'account_id': account_info_id,
            'name': 'Credit Entry',
            'credit': sum(link.amount_monetary for link in current_record.req_topic_links),
        })

        # Add the credit entry tuple to the list
        line_ids_default.append(credit_entry)

        default_values = {
            'ref': current_record.request_title,
            'line_ids': line_ids_default,
            'request_id': current_record.id,
        }

        # Create the account.move entry
        account_move = self.env['account.move'].create(default_values)

        # Post the journal entry
        account_move.action_post()

        # Retrieve the ID of the created account.move record
        account_move_id = account_move.id

        # Update your service.requests model with the account.move ID
        current_record.write({
            'account_move_id': account_move_id,
            'journal_created': True,  # Set journal_created to True
        })

        # Set the form as readonly in the context using the 'form_view_initial_mode' key
        action['context'] = {'default_' + key: value for key, value in default_values.items()}
        # action['context']['form_view_initial_mode'] = 'view'

        self._logger.info("line_ids_default: %s", line_ids_default)
        return action

    @api.model
    def create(self, vals):
        # Your original logic for checking 'request_state'
        if 'request_state' in vals and vals['request_state'] in ['Approved', 'Refused']:
            raise ValidationError("Cannot set request state to 'Approved' or 'Refused' during record creation.")

        # Your original logic for populating 'requested_by' and 'requestdate_ad'
        user_groups = self.env.user.groups_id.mapped('name')
        vals['requested_by'] = self.env.user.name if 'branchUsers' in user_groups else False
        vals['requestdate_ad'] = fields.Datetime.now()

        # Check if the state is 'submitted'
        if 'request_state' in vals and vals['request_state'] == 'submitted':
            group_id = self.env.ref('service-approval.group_central_users')
            if group_id:
                group_users = group_id.users
                followers = [(4, user.id) for user in group_users]

                # Post a message to the followers
                message = "A new record has been submitted: %s" % vals['request_title']
                # self.env['service.requests'].message_post(body=message, subtype='mt_comment', followers=followers)
                self.env.user.notify_info(message='My information message')

        # Call the method to create and associate secure sequence
        request = super(Requests, self).create(vals)
        request._create_secure_sequence()

        return request


class AccountMove(models.Model):
    _inherit = 'account.move'

    request_id = fields.Many2one('service.requests', string='Related Request')
























# def create(self, vals):
#     move = super(AccountMove, self).create(vals)
#     if move.request_id:
#         move.request_id.write({'journal_created': True})
#         _logger.info("Updated journal_created for service.requests record %s", move.request_id.id)
#     return move
#
# def write(self, vals):
#     result = super(AccountMove, self).write(vals)
#     for move in self:
#         if move.request_id:
#             move.request_id.write({'journal_created': True})
#             _logger.info("Updated journal_created for service.requests record %s", move.request_id.id)
#     return result

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
