Adds an **Auto package** toggle to the *Record Weight* wizard. When ON,
each detailed operation added through the wizard gets a freshly created
`stock.quant.package`. The toggle is remembered per product.

1. From a transfer (or the **Weighing** app) open a move kanban card and
   click **+** *(Add operation)* — this opens the wizard in
   *Add detailed operation* mode.
2. In the wizard set the **Weight**, optionally pick a *Destination
   Package*, and toggle **Auto package** in the footer.
3. Press **Add detailed operation**.

Outcome on the new move line:

- *Destination Package* selected → that package wins.
- Otherwise, *Auto package* ON → a new empty package is created and
  assigned.
- Neither → no package.
