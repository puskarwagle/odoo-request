/** @odoo-module **/

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { CheckBox } from "@web/core/checkbox/checkbox";
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { Component,useState } from "@odoo/owl";
import { symmetricalDifference } from "@web/core/utils/arrays";
const userMenuRegistry = registry.category("user_menuitems");

export class ReqUserMenu extends Component {
    setup() {
        this.user = useService("user");
        const { origin } = browser.location;
        const { userId } = this.user;
        this.userallitem = useService("myrequestUserService");
        this.source = `${origin}/web/image?model=res.users&field=avatar_128&id=${userId}`;
        this.companyService = useService("company");
        const availablessCompanies=this.companyService.availableCompanies;
        if (this.userallitem.active_company_name_np !=false){
            this.currentCompany = Object.values(availablessCompanies).find(item => item.id === this.userallitem.active_company_id);
            this.currentCompany.active_company_name_np=this.userallitem.active_company_name_np
            const request_allowed_company=[];
            request_allowed_company.push(this.userallitem.active_company_id);
            this.companyService.request_allowed_company=request_allowed_company;
        }

        else
            this.currentCompany = this.companyService.currentCompany;
        this.state = useState({ companiesToToggle: [] });

    }
    toggleCompany(companyId) {
        this.state.companiesToToggle = symmetricalDifference(this.state.companiesToToggle, [
            companyId,
        ]);
        browser.clearTimeout(this.toggleTimer);
        this.toggleTimer = browser.setTimeout(() => {
            this.companyService.setCompanies("toggle", ...this.state.companiesToToggle);
        }, this.constructor.toggleDelay);
    }
    logIntoCompany(companyId) {
        browser.clearTimeout(this.toggleTimer);
        this.companyService.setCompanies("loginto", companyId);
    }
    get selectedCompanies() {
        return symmetricalDifference(
            this.companyService.request_allowed_company==undefined?this.companyService.allowedCompanyIds:this.companyService.request_allowed_company,
            this.state.companiesToToggle
        );
    }

    getElements() {
        const sortedItems = userMenuRegistry
            .getAll()
            .map((element) => element(this.env))
            .sort((x, y) => {
                const xSeq = x.sequence ? x.sequence : 100;
                const ySeq = y.sequence ? y.sequence : 100;
                return xSeq - ySeq;
            });
        return sortedItems;
    }


}
ReqUserMenu.template = "service-approval.UserMenu";
ReqUserMenu.components = { Dropdown, DropdownItem, CheckBox };

export const systrayItem = {
    Component: ReqUserMenu,
    isDisplayed(env) {
        const { availableCompanies } = env.services.company;
        return Object.keys(availableCompanies).length >= 1;
    },
};
registry.category("systray").add("service-approval.UserMenu", systrayItem,{ sequence: 0});