To configure your remote devices:

#. Go to *Settings > Technical > Devices > Remote devices*
#. Create a new one configuring the required info.
#. If the devices has an special port, set it up in the host data: e.g.: 10.1.1.2:3210

If you want to see the button in the top bar to set the user's remote device, you need
to have the "Show remote device button on navbar" group.

If you need the field to always be selected, you can use the ``always_selected``
attribute in the view definition, as shown in the following example:

.. code:: xml

    <field name="field_float" widget="remote_measure" always_selected="1"/>
