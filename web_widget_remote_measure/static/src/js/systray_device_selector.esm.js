/* @odoo-module */
/* Copyright 2025 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
const {onWillStart} = owl.hooks;
const {Component} = owl;

export class SelectRemoteDeviceMenu extends Component {
    setup() {
        this.action = useService("action");
        this.user = useService("user");
        onWillStart(async () => {
            this.isRemoteDeviceUser = await this.user.hasGroup(
                "web_widget_remote_measure.remote_device_button_group"
            );
        });
    }

    /**
     * Go to user init action when clicking it
     * @private
     */
    async onClickSelectRemoteDevice() {
        const action = await this.action.loadAction(
            "web_widget_remote_measure.action_user_remote_device_selector"
        );
        action.res_id = this.user.userId;
        this.action.doAction(action);
    }
}

SelectRemoteDeviceMenu.template =
    "web_widget_remote_measure.RemoteDeviceSelectorButton";

export const systrayRemoteDeviceSelector = {
    Component: SelectRemoteDeviceMenu,
};

registry
    .category("systray")
    .add(
        "web_widget_remote_measure.remote_device_selector_button",
        systrayRemoteDeviceSelector,
        {
            sequence: 100,
        }
    );
