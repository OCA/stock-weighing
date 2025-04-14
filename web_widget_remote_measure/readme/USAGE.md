The remote device has to be in the users network so their web clients
can reach them.

In order to test a device you can:

1.  Go to *Settings \> Technical \> Devices \> Remote devices*
2.  In the Kanban view you'll wich devices can be reached as they'll
    have a green dot in their card.
3.  Go to one of those and click *Edit*.
4.  You can start measuring from the remote device in the *Test measure*
    field.

On the technical side, you can use the widget in your own Float\`.
You'll need to provide an uom field so records that aren't in that UoM
don't measure from the device.

``` xml
<field name="float_field" widget="remote_measure" options="{'remote_device_field': 'measure_device_id', 'uom_field': 'uom_id'}" />
```

The users are able to change their default remote device by using the button with the
balance icon set on the navbar.
