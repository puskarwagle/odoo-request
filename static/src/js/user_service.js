/** @odoo-module **/

import { registry } from "./registry";
import { session } from "@web/session";

export const requestuserService = {
    dependencies: ["rpc"],
    // async: ["hasGroup"],
    start(env, { rpc }) {
        const groupProms = {};
        const user_details = {};

        const context = {
            ...session.user_context,
            uid: session.uid,
        };
        return {
            get context() {
                return Object.assign({}, context);
            },
            removeFromContext(key) {
                delete context[key];
            },
            updateContext(update) {
                Object.assign(context, update);
            },
            hasGroup(group) {
                if (!context.uid) {
                    return Promise.resolve(false);
                }
                if (!groupProms[group]) {
                    groupProms[group] = rpc("/web/dataset/call_kw/res.users/has_group", {
                        model: "res.users",
                        method: "has_group",
                        args: [group],
                        kwargs: { context },
                    });
                }
                return groupProms[group];
            },
            name: session.name,
            userName: session.username,
            isAdmin: session.is_admin,
            isSystem: session.is_system,
            partnerId: session.partner_id,
            home_action_id: session.home_action_id,
            showEffect: session.show_effect,
            active_company_id:session.active_company_id,
            active_branch_id:session.active_branch_id,
            active_branch_name_np:session.active_branch_name_np,
            active_company_name_np:session.active_company_name_np,
            active_user_name_np:session.active_user_name_np,
            active_fy_id:session.current_fy_id,
            get userId() {
                return context.uid;
            },
            get lang() {
                return context.lang;
            },
            get tz() {
                return context.tz;
            },
            get db() {
                const res = {
                    name: session.db,
                };
                if ("dbuuid" in session) {
                    res.uuid = session.dbuuid;
                }
                return res;
            },
            get getUserAllInfo(){
                 if (!context.uid) {
                    return Promise.resolve(false);
                }
                const userProm = rpc("/web/dataset/call_kw/res.users/read", {
                model: "res.users",
                method: "read",
                args: [context.uid], // Replace "user_id" with the actual user ID
                kwargs: { context },
                });
                return userProm;
            }
        };
    },
};


