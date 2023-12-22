from odoo import models, fields, api


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
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id)
    amount_monetary = fields.Monetary(string='Amount in Currency', currency_field='currency_id',
                                      compute='_compute_amount_monetary', store=True)

    @api.depends('amount', 'currency_id')
    def _compute_amount_monetary(self):
        for record in self:
            record.amount_monetary = record.amount

    topic_id = fields.Many2one(
        'service.topics',
        string='Topic',
        required=True,
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

    topic_account_id = fields.Many2one(
        'account.account',
        string='Account',
        related='topic_id.account_id',
        store=True,
        readonly=True,
    )

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

    # def create(self, values):
    #     values['currency_id'] = self.env.company.currency_id.id
    #     return super(ReqTopicLink, self).create(values)
    #
    # def write(self, values):
    #     values['currency_id'] = self.env.company.currency_id.id
    #     return super(ReqTopicLink, self).write(values)
