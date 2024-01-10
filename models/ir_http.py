# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hashlib
import json
import logging

import odoo
from odoo import api, http, models
from odoo.http import request
from odoo.tools import file_open, image_process, ustr
from odoo.tools.misc import str2bool

_logger = logging.getLogger(__name__)
ALLOWED_DEBUG_MODES = ['', '1', 'assets', 'tests', 'disable-t-cache']


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = self.env.user
        session_uid = request.session.uid
        version_info = odoo.service.common.exp_version()

        if session_uid:
            user_context = dict(self.env['res.users'].context_get())
            if user_context != request.session.context:
                request.session.context = user_context
        else:
            user_context = {}

        IrConfigSudo = self.env['ir.config_parameter'].sudo()
        max_file_upload_size = int(IrConfigSudo.get_param(
            'web.max_file_upload_size',
            default=12 * 1024 * 1024,  # 12MiB
        ))
        mods = odoo.conf.server_wide_modules or []
        param_value = self.env['ir.config_parameter'].with_company(user.active_company_id.id).sudo().get_param('account.fiscal.year')
        seting_fiscal_year = self.env['account.fiscal.year'].search([('id', '=', param_value)], limit=1)

        if request.db:
            mods = list(request.registry._init_modules) + mods
        session_info = {
            "uid": session_uid,
            "is_system": user._is_system() if session_uid else False,
            "is_admin": user._is_admin() if session_uid else False,
            "active_branch_id": user.active_branch_id.branch_name,
            "active_company_id": user.active_company_id.id,
            "active_branch_name_np": user.active_branch_id.branch_name_np,
            "active_company_name_np": user.active_company_id.full_name_np,
            "active_user_name_np": user.full_name_np,
            "current_fy_id": seting_fiscal_year.name,
            "user_context": user_context,
            "db": self.env.cr.dbname,
            "server_version": version_info.get('server_version'),
            "server_version_info": version_info.get('server_version_info'),
            "support_url": "https://www.odoo.com/buy",
            "name": user.name,
            "username": user.login,
            "partner_display_name": user.partner_id.display_name,
            "company_id": user.company_id.id if session_uid else None,  # YTI TODO: Remove this from the user context
            "partner_id": user.partner_id.id if session_uid and user.partner_id else None,
            "web.base.url": IrConfigSudo.get_param('web.base.url', default=''),
            "active_ids_limit": int(IrConfigSudo.get_param('web.active_ids_limit', default='20000')),
            'profile_session': request.session.profile_session,
            'profile_collectors': request.session.profile_collectors,
            'profile_params': request.session.profile_params,
            "max_file_upload_size": max_file_upload_size,
            "home_action_id": user.action_id.id,
            "cache_hashes": {
                "translations": self.env['ir.http'].sudo().get_web_translations_hash(
                    mods, request.session.context['lang']
                ) if session_uid else None,
            },
            "currencies": self.sudo().get_currencies(),
            'bundle_params': {
                'lang': request.session.context['lang'],
            },
        }
        if request.session.debug:
            session_info['bundle_params']['debug'] = request.session.debug
        if self.env.user.has_group('base.group_user'):
            # the following is only useful in the context of a webclient bootstrapping
            # but is still included in some other calls (e.g. '/web/session/authenticate')
            # to avoid access errors and unnecessary information, it is only included for users
            # with access to the backend ('internal'-type users)
            menus = self.env['ir.ui.menu'].load_menus(request.session.debug)
            ordered_menus = {str(k): v for k, v in menus.items()}
            menu_json_utf8 = json.dumps(ordered_menus, default=ustr, sort_keys=True).encode()
            session_info['cache_hashes'].update({
                "load_menus": hashlib.sha512(menu_json_utf8).hexdigest()[:64],  # sha512/256
            })
            session_info.update({
                # current_company should be default_company
                "user_companies": {
                    'current_company': user.company_id.id,
                    'allowed_companies': {
                        comp.id: {
                            'id': comp.id,
                            'name': comp.name,
                            'sequence': comp.sequence,
                        } for comp in user.company_ids
                    },
                },
                "show_effect": True,
                "display_switch_company_menu": user.has_group('base.group_multi_company') and len(user.company_ids) > 1,
            })
        return session_info
