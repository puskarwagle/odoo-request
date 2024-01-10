from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class ReqTopicLink(models.Model):
    _name = 'service.reqtopiclink'
    _description = 'Request Topic Link'

    request_id = fields.Many2one(
        'service.requests',
        string='Request',
        required=True,
        ondelete='cascade',
    )

    amount = fields.Float(string='Amount')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id.id)
    amount_monetary = fields.Monetary(string='Amount in Currency', currency_field='currency_id',
                                      compute='_compute_amount_monetary', store=True)

    topic_id = fields.Many2one(
        'service.topics',
        string='Topic',
        required=True)

    topic_root_id = fields.Many2one(
        related='topic_id.service_topic_id',
        string="Topic Root",
        store=True,
    )
    rquest_branch_id = fields.Many2one(
        related='request_id.select_branch',
        string="Branch",
        store=True,
    )
    rquest_request_date_bs = fields.Char(
        related='request_id.requestdate_bs',
        string="Req Date(Bs)",
        store=True,
    )
    rquest_requested_by = fields.Char(
        related='request_id.requested_by',
        string="Requested By",
        store=True,
    )
    rquest_approve_date_bs = fields.Char(
        related='request_id.approved_date_bs',
        string="Appr Date(Bs)",
        store=True,
    )
    rquest_approved_by = fields.Char(
        related='request_id.approved_by',
        string="Approved By",
        store=True,
    )
    rquest_fiscal_year = fields.Many2one(
        related='request_id.fiscal_year_id',
        string="Fiscal Year",
        store=True,
    )
    max_amount = fields.Float(
        string='Max Amount',
        compute='_compute_max_amount',
        store=True,
    )

    remaining_amount = fields.Float(
        string='Remaining Amount',
        compute='_compute_remaining_amount',
        store=True,
    )
    request_request_state = fields.Selection(
        string='Stage of Request',
        related='request_id.request_state',
    )
    topic_account_id = fields.Many2one(
        'account.account',
        string='Account',
        related='topic_id.account_id',
        store=True,
        readonly=True,
    )

    account_root_id = fields.Many2one(
        related='topic_account_id.root_id',
        string="Account Root",
        store=True,
    )
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments")
    request_attachment_ids = fields.Many2many(
        'ir.attachment', string="Attach File", compute='_compute_supported_attachment_ids',
        inverse='_inverse_supported_attachment_ids')

    @api.onchange('amount')
    def _onchange_amount(self):
        if self.amount > self.remaining_amount:
            warning_msg = {
                'title': 'Warning!',
                'message': 'You are saving an amount less than the remaining amount.'
            }
            return {'warning': warning_msg}

    @api.depends('amount', 'currency_id')
    def _compute_amount_monetary(self):
        for record in self:
            record.amount_monetary = record.amount

    @api.depends('attachment_ids')
    def _compute_supported_attachment_ids(self):
        for request in self:
            request.request_attachment_ids = request.attachment_ids

    def _inverse_supported_attachment_ids(self):
        for request in self:
            request.attachment_ids = request.request_attachment_ids

    def action_documents(self):
        domain = [('id', 'in', self.attachment_ids.ids)]
        return {
            'name': _("Attach Documents"),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'context': {'create': False},
            'view_mode': 'kanban',
            'domain': domain
        }

    @api.depends('topic_id')
    def _compute_max_amount(self):
        for record in self:
            if record.topic_id:
                record.max_amount = record.topic_id.max_amount

    @api.depends('amount', 'topic_id', 'request_id.request_state', 'topic_id.remaining_amount')
    def _compute_remaining_amount(self):
        for record in self:
            if record.request_id.request_state == 'approved':
                total_amount = sum(link.amount for link in self.filtered(lambda x: x.topic_id == record.topic_id))
                record.remaining_amount = record.max_amount - total_amount
                record.topic_id.write({'remaining_amount': record.remaining_amount})
            else:
                record.remaining_amount = record.topic_id.remaining_amount if record.topic_id else 0.0
