from odoo import models, fields, api


class TopicTitle(models.Model):
    _name = 'service.topictitle'
    _description = 'Service Topic Name'

    topic_title = fields.Char(string='Topic Title')
    topic_description = fields.Char(string='Topic description')

    _rec_name = 'topic_title'