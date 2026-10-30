import {
    contains,
    defineModels,
    fields,
    models,
    mountView,
    onRpc,
} from "@web/../tests/web_test_helpers";
import {expect, test} from "@odoo/hoot";
import {queryAll, waitUntil} from "@odoo/hoot-dom";

class UomUom extends models.Model {
    _name = "uom.uom";
    name = fields.Char();
    factor = fields.Float();

    _records = [
        {id: 1, name: "kg", factor: 1},
        {id: 2, name: "g", factor: 0.001},
    ];
}

class RemoteMeasureDevice extends models.Model {
    _name = "remote.measure.device";
    name = fields.Char();
    host = fields.Char();
    protocol = fields.Selection({selection: [["f501", "Scale F501"]]});
    connection_mode = fields.Selection({
        selection: [
            ["websockets", "Web Sockets"],
            ["tcp", "Direct connection"],
        ],
    });
    uom_id = fields.Many2one({relation: "uom.uom"});
    uom_factor = fields.Float();
    instant_read = fields.Boolean();
    non_stop_read = fields.Boolean();
    read_interval = fields.Integer();

    _records = [
        {
            id: 1,
            name: "Scale in grams",
            host: "127.0.0.1:1234",
            protocol: "f501",
            connection_mode: "tcp",
            uom_id: 2,
            uom_factor: 0.001,
        },
    ];
}

class Line extends models.Model {
    quantity = fields.Float();
    uom_id = fields.Many2one({relation: "uom.uom"});
    device_id = fields.Many2one({relation: "remote.measure.device"});

    _records = [
        {id: 1, quantity: 0, uom_id: 1, device_id: 1},
        {id: 2, quantity: 0, uom_id: false, device_id: 1},
        {id: 3, quantity: 2, uom_id: 1, device_id: 1},
    ];
}

defineModels([UomUom, RemoteMeasureDevice, Line]);

const START = ".o_field_widget[name='quantity'] .o_field_remote_device_start";
const INPUT = ".o_field_widget[name='quantity'] input";

function mountLine(resId, options = "") {
    return mountView({
        type: "form",
        resModel: "line",
        resId,
        arch: `
            <form>
                <field name="uom_id"/>
                <field name="device_id"/>
                <field
                    name="quantity"
                    widget="remote_measure"
                    options="{'remote_device_field': 'device_id', 'uom_field': 'uom_id'${options}}"
                />
            </form>`,
    });
}

test("measure from a TCP scale and convert it to the record UoM", async () => {
    // The scale weighs in grams: 1250 g (stable) must be recorded as 1.25 kg
    onRpc("/remote_measure_device/1", () => "\x02 +1250.00\x03");
    await mountLine(1);
    expect(START).toHaveCount(1);
    await contains(START).click();
    await waitUntil(() => queryAll(START).length === 1);
    expect(INPUT).toHaveValue("1.25");
});

test("no measure button without a UoM", async () => {
    await mountLine(2);
    expect(START).toHaveCount(0);
    expect(INPUT).toHaveCount(1);
});

test("additive measure adds to the current value", async () => {
    onRpc("/remote_measure_device/1", () => "\x02 +0500.00\x03");
    await mountLine(3, ", 'allow_additive_measure': True");
    // Measure + additive buttons
    expect(START).toHaveCount(2);
    await contains(`${START}.btn-link`).click();
    await waitUntil(() => queryAll(START).length === 2);
    expect(INPUT).toHaveValue("2.50");
});
