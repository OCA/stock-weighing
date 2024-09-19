/** @odoo-module **/
import FormController from "web.FormController";
import FormRenderer from "web.FormRenderer";
import FormView from "web.FormView";
import viewRegistry from "web.view_registry";

const WeightRecordingFormController = FormController.extend({
    custom_events: _.extend({}, FormController.prototype.custom_events, {
        click_control_button: "_onClickControlButton",
    }),
    _onClickControlButton: function (ev) {
        if (this.$buttons) {
            ev.stopPropagation();
            this.$buttons.find(".default-enter:visible:first()").click();
        }
    },
});

const WeightRecordingFormRenderer = FormRenderer.extend({
    /**
     * Use enter key to trigger a controllable event
     *
     * @private
     * @override
     */
    _onNavigationMove: function (ev) {
        ev.stopPropagation();
        if (ev.data.direction !== "next_line") {
            return this._super.apply(this, arguments);
        }
        this.trigger_up("click_control_button");
    },
});

export const WeightRecordingFormView = FormView.extend({
    config: Object.assign({}, FormView.prototype.config, {
        Controller: WeightRecordingFormController,
        Renderer: WeightRecordingFormRenderer,
    }),
});

viewRegistry.add("weight_recording_form", WeightRecordingFormView);
