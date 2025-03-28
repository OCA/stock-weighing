import {Component, onWillStart} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";
import {user} from "@web/core/user";
import {useService} from "@web/core/utils/hooks";

export class DeviceDialog extends Component {
    static template = "stock_weighing_remote_measure.DeviceDialog";
    static components = {Dialog};
    static props = {
        close: Function,
        device_field: Object,
    };
    setup() {
        this.orm = useService("orm");
        onWillStart(async () => {
            this.devices = await this.orm.call("remote.measure.device", "search_read", [
                [],
                ["id", "name"],
            ]);
        });
        this.user = user;
    }
    async onClickDevice(ev) {
        const device_id = parseInt(ev.currentTarget.dataset.device_id, 10);
        await this.orm.call("res.users", "write", [
            [user.userId],
            {remote_measure_device_id: device_id},
        ]);
        this.props.device_field.remote_device_data.id = device_id;
        this.props.device_field.uom = this.props.device_field.uom.id;
        await this.props.device_field._assignDevice();
        this.props.close();
    }
}
