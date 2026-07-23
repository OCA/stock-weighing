1. Configure the *Owner restriction* field on an *Operation Type* (provided
   by the `stock_owner_restriction` module).
2. Open the weighing wizard for a move of that operation type.
3. If the move shows the manual stock picker (*Pick From*), only quants
   matching the configured owner restriction are selectable.
4. If the product is tracked and no stock is manually picked, only lots
   having at least one quant matching the owner restriction are offered.
   A lot having both owned and unowned quants is still offered, since the
   restriction is applied at the quant level when the operation is
   reserved.
