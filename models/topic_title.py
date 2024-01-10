from odoo import models, fields, api


class TopicTitle(models.Model):
    _name = 'service.topictitle'
    _description = 'Service Topic Name'

    topic_title = fields.Char(string='Topic Title')
    topic_description = fields.Char(string='Topic description')

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

    _rec_name = 'topic_title'

    # @api.model
    # def name_get(self):
    #     result = []
    #     for topictitle in self:
    #         name = f"{topictitle.topic_title}/{topictitle.secure_sequence_id.name}/{topictitle.secure_sequence_id.id}"
    #         result.append((topictitle.id, name))
    #     return result

    @api.model
    def _create_secure_sequence(self):
        """This function creates a secure sequence for the topic if not already present."""
        for topictitle in self:
            if not topictitle.secure_sequence_id:
                now = fields.Datetime.now()
                year = now.strftime('%y')
                hour = now.strftime('%H')
                minute = now.strftime('%M')
                second = now.strftime('%S')

                seq_name = f'{year}/{hour}{minute}{second}'
                secure_sequence = self.env['ir.sequence'].search([('name', '=', seq_name)], limit=1)
                if not secure_sequence:
                    seq_vals = {
                        'name': seq_name,
                        'code': f'SECURE-TOPIC-{year}-{hour}-{minute}-{second}',
                        'implementation': 'no_gap',
                        'prefix': '',
                        'suffix': '',
                        'padding': 0,
                        'company_id': topictitle.company_id.id
                    }
                    secure_sequence = self.env['ir.sequence'].create(seq_vals)

                # Update the secure_sequence_id field in the topictitle
                topictitle.secure_sequence_id = secure_sequence

    @api.model
    def create(self, vals):
        # Your custom logic goes here
        # For example, you can call the _create_secure_sequence method before creating the record
        topictitle = super(TopicTitle, self).create(vals)
        # topictitle._create_secure_sequence()
        return topictitle

