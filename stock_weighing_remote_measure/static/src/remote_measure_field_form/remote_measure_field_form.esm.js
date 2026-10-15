import {
    RemoteMeasureField,
    remoteMeasureField,
} from "@web_widget_remote_measure/remote_measure_field/remote_measure_field.esm";
import {onWillStart, useState} from "@odoo/owl";
import {DeviceDialog} from "../device_dialog/device_dialog.esm";
import {FormViewDialog} from "@web/views/view_dialogs/form_view_dialog";
import {_t} from "@web/core/l10n/translation";
import {formatFloat} from "@web/views/fields/formatters";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {user} from "@web/core/user";

export class RemoteMeasureForm extends RemoteMeasureField {
    static props = {
        ...RemoteMeasureField.props,
        tares: {type: Object, optional: true},
    };
    static template = "stock_weighing_remote_measure.RemoteMeasureForm";
    setup() {
        super.setup();
        this.dialog = useService("dialog");
        this.state = useState({
            ...this.state,
            tare: 0,
            tares: this.props.tares || [],
            can_configure_tares: false,
        });
        this.manualTare = 0;
        this.formatFloat = (val) =>
            formatFloat(val, {
                digits: this.env.model.config.fields[this.props.name].digits,
            });
        // Load the configured tares unless they're forced from the view options
        onWillStart(async () => {
            if (this.props.tares || !this.uomId) {
                return;
            }
            this.state.can_configure_tares = await user.hasGroup(
                "stock.group_stock_manager"
            );
            await this._loadTares();
        });
    }
    get uomId() {
        return this.props.uom_field
            ? this.props.record.data[this.props.uom_field]?.[0]
            : false;
    }
    /**
     * Fetch the configured tares for the widget UoM
     */
    async _loadTares() {
        this.state.tares = await this.orm.call("weighing.tare", "get_widget_tares", [
            this.uomId,
        ]);
    }
    get extraMeasures() {
        const extraMeasures = super.extraMeasures;
        return extraMeasures + this.state.tare;
    }
    _set_tare(tare) {
        let value = tare;
        if (!value || isNaN(value)) {
            value = 0;
        }
        this.state.tare += value;
        this._setMeasure();
    }
    onClickTare(ev) {
        const tare = parseFloat(ev.currentTarget.dataset.tare);
        this._set_tare(tare);
    }
    onClickManualTare(ev) {
        // Remove the manual tare set to avoid increase the tare infinitely
        this._set_tare(-this.manualTare);
        const mode = ev.currentTarget.dataset.mode;
        const input = ev.currentTarget.parentElement.querySelector("input");
        if (mode === "minus") {
            input.stepDown();
        } else {
            input.stepUp();
        }
        this.manualTare = input.valueAsNumber;
        this._set_tare(this.manualTare);
    }
    onChangeTareManualTare(ev) {
        // Remove the manual tare set to avoid increase the tare infinitely
        this._set_tare(-this.manualTare);
        this.manualTare = ev.currentTarget.valueAsNumber;
        this._set_tare(this.manualTare);
    }
    onDeviceSelector() {
        this.dialog.add(DeviceDialog, {device_field: this});
    }
    /**
     * Open the tares configuration wizard and refresh the widget once saved
     */
    onConfigureTares() {
        this.measure_stop();
        this.dialog.add(FormViewDialog, {
            resModel: "weighing.tare.wizard",
            title: _t("Configure tares"),
            onRecordSaved: async (record) => {
                await this.orm.call("weighing.tare.wizard", "action_apply", [
                    [record.resId],
                ]);
                await this._loadTares();
            },
        });
    }
}

export const remoteMeasureForm = {
    ...remoteMeasureField,
    component: RemoteMeasureForm,
    supportedOptions: [
        ...remoteMeasureField.supportedOptions,
        {
            label: _t("Tares"),
            name: "tares",
            type: "string",
        },
    ],
    extractProps({options}) {
        const props = remoteMeasureField.extractProps(...arguments);
        props.tares = options.tares;
        return props;
    },
};

registry.category("fields").add("remote_measure_form", remoteMeasureForm);
