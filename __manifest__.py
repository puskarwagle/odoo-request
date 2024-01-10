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
    'depends': ["base",'base_setup', 'account', 'om_fiscal_year','nepali_date_widget'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',

        'data/province_data.xml',
        'data/district_data.xml',
        'data/palika_data.xml',
        'data/mail_activity_type_data.xml',
        'data/cps_default_data.xml',

        'views/branch/branch_management.xml',
        'views/branch/configuration_location_views.xml',

        'views/topics/topic_titles.xml',
        'views/topics/request_topics.xml',

        'views/configuration/fiscalyear.xml',
        'views/configuration/res_config_settings_views.xml',

        'views/approve/submitted_requests_to_approve.xml',
        'views/approve/all_requests_to_approve.xml',
        'views/approve/approved_requests.xml',

        'views/request/create_new_request.xml',
        'views/request/my_requests.xml',
        'views/request/requests_to_submit.xml',
        'views/request/requests_to_resubmit.xml',

        'views/approve/request_summary.xml',

        'views/configuration/mail_activity_views.xml',
        'views/configuration/request_menu_item.xml',
        'views/configuration/res_users_views.xml',
        'views/configuration/res_company_views.xml',
        'views/configuration/employee.xml',
        'views/configuration/emp_department.xml',

        'report/adbl-petty/adblpetty.xml'
    ],

    'assets': {

        'web.assets_backend': [
            'service-approval/static/src/js/sidebar_menu.js',

            # 'service-approval/static/src/js/hooks.js',
            'service-approval/static/src/js/user_service.js',
            'service-approval/static/src/js/registry.js',
            # 'service-approval/static/src/js/env.js',
             'service-approval/static/src/js/user_menu.js',
            # 'service-approval/static/src/js/use_model.js',
            # 'service-approval/static/src/model/model_listener.js',
            'service-approval/static/src/scss/request_backend.scss',

            'service-approval/static/src/xml/sidebar.xml',
            'service-approval/static/src/xml/user_menu.xml',
            'service-approval/static/src/xml/request_user_menu.xml',
            #'service-approval/static/src/xml/request_switch_company.xml'



        ],
        'web.assets_backend_prod_only': [
            'service-approval/static/src/js/main.js'

        ],

    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
}
