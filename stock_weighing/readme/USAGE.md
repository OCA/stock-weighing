You've got several ways to start weighing pending operations:

**From the app menu**
1. Go to the app menu an click on *Weighing*
2. You'll be presented with your weighing options (Incoming, Outgoing or more if a third module extends it)
3. You can start weighing.

**From a weighing operation type**
1. Go to *Inventory > Overview*.
2. Those operation types with *weighing operation* active will show a button with the pending ones.
3. Click on it and you can start weighing.

**From a picking**
1. In any picking with weighing operations, you can click on the smart button and start processing them.

Using the assitant
------------------
You'll be presented with a list of operations to weigh. To weigh them, just press the red circle button to record a new weight:

  - If there's only one detailed operation reserved, a popup will show up to record the operation weight.
  - If there are several, you'll enter the detailed view and you'll be able to weigh every detailed operation.
  - If you just want to weigh one, you can force the operation as done using the checkmark button.

You can reset your weighing using the cross button.
You can print the label on demand using the printer button.
You can add a new detailed operation using the plus button.

Validating the operations
-------------------------
Each recorded weight is the picked quantity of its detailed operation, which
is flagged as picked. When the transfer is validated:

  - If nothing has been weighed or picked, the reserved quantities are validated as usual.
  - Once any operation has been weighed, only the picked detailed operations are validated,
    with their weights. The rest follow the backorder policy of the operation type.
  - Operations of products that aren't weighed are picked with the *Set reserved to done* button.
  - The detailed operations without weight of a weighed operation are left out.
  - Resetting a weight unpicks its detailed operation.

The picked quantities come from the *Stock Move Line Qty Picked* module, so they are shared
with other modules preparing operations, such as the barcode reader.
