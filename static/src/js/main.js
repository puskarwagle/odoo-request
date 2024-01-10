/** @odoo-module **/
import { registerService } from "@web/core/registry";
import { requestuserService } from './user_service';

import { registry } from '@web/core/registry';


const serviceRegistry = registry.category('services');
serviceRegistry.add('myrequestUserService', requestuserService);



