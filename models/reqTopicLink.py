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

    @api.depends('topic_id')
    def _compute_max_amount(self):
        for record in self:
            if record.topic_id:
                record.max_amount = record.topic_id.max_amount

    @api.depends('amount', 'topic_id', 'request_id.request_state', 'topic_id.remaining_amount')
    def _compute_remaining_amount(self):
        for record in self:
            if record.request_id.request_state == 'Approved':
                total_amount = sum(link.amount for link in self.filtered(lambda x: x.topic_id == record.topic_id))
                record.remaining_amount = record.max_amount - total_amount

                record.topic_id.write({'remaining_amount': record.remaining_amount})
            else:
                record.remaining_amount = record.topic_id.remaining_amount if record.topic_id else 0.0
