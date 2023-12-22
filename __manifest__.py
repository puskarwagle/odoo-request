# -*- coding: utf-8 -*-
{
    'name': "Approvals",

    'summary': """
        Petty Cash Management""",

    'description': """
        Through this module one can send request to central for funds
    """,

    'author': "Shangrila",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'om_fiscal_year'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',

        'views/branch/branch_management.xml',

        'views/topics/topic_titles.xml',
        # 'views/topics/topics_for_approvals.xml',
        'views/topics/request_topics.xml',
        'views/request/fiscalyear.xml',

        'views/approve/submitted_requests_to_approve.xml',
        'views/approve/all_requests_to_approve.xml',
        'views/approve/approved_requests.xml',

        'views/request/create_new_request.xml',
        'views/request/my_requests.xml',
        'views/request/requests_to_submit.xml',
        'views/request/requests_to_resubmit.xml',
    ],
    'installable': True,
    'auto_install': False,
}
