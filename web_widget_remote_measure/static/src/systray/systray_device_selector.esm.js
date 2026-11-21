/* Copyright 2025 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
import {Component, onWillStart} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {user} from "@web/core/user";

export class SelectRemoteDeviceMenu extends Component {
    static template = "web_widget_remote_measure.RemoteDeviceSelectorButton";
    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        onWillStart(async () => {
            this.isRemoteDeviceUser = await user.hasGroup(
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
        action.res_id = user.userId;
        this.action.doAction(action, {
            onClose: () => this._refreshUserDevice(),
        });
    }

    /**
     * Keep the session settings in sync so the widgets use the new default
     * device without reloading the page.
     * @private
     */
    async _refreshUserDevice() {
        const [userData] = await this.orm.read(
            "res.users",
            [user.userId],
            ["remote_measure_device_id"]
        );
        user.updateUserSettings(
            "remote_measure_device_id",
            userData?.remote_measure_device_id || false
        );
    }
}

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
