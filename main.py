# Global state to simulate failures and successful operations across 'microservices'
order_db = {}
inventory_db = {}
payment_db = {}

# --- Microservice Simulation Functions ---

def create_order_service(order_id, items, simulate_failure=False):
    """Simulates creating an order in the Order Service."""
    print(f"  [Order Service] Attempting to create order {order_id} with items: {items}")
    if simulate_failure:
        print(f"  [Order Service] SIMULATING FAILURE for order {order_id}")
        raise Exception("Order creation failed")
    order_db[order_id] = {"items": items, "status": "created"}
    print(f"  [Order Service] Order {order_id} created successfully.")
    return True

def cancel_order_service(order_id):
    """Compensation for create_order_service: cancels the order."""
    print(f"  [Order Service] Compensating: Cancelling order {order_id}")
    if order_id in order_db:
        order_db[order_id]["status"] = "cancelled"
        print(f"  [Order Service] Order {order_id} cancelled.")
    else:
        print(f"  [Order Service] Order {order_id} not found for cancellation.")
    return True

def reserve_inventory_service(order_id, items, simulate_failure=False):
    """Simulates reserving inventory in the Inventory Service."""
    print(f"  [Inventory Service] Attempting to reserve inventory for order {order_id}, items: {items}")
    if simulate_failure:
        print(f"  [Inventory Service] SIMULATING FAILURE for order {order_id}")
        raise Exception("Inventory reservation failed")
    # Simple simulation: assume inventory is always available
    inventory_db[order_id] = {"items": items, "status": "reserved"}
    print(f"  [Inventory Service] Inventory reserved for order {order_id}.")
    return True

def release_inventory_service(order_id, items):
    """Compensation for reserve_inventory_service: releases reserved inventory."""
    print(f"  [Inventory Service] Compensating: Releasing inventory for order {order_id}")
    if order_id in inventory_db and inventory_db[order_id]["status"] == "reserved":
        inventory_db[order_id]["status"] = "released"
        print(f"  [Inventory Service] Inventory for order {order_id} released.")
    else:
        print(f"  [Inventory Service] No reserved inventory found for order {order_id} to release.")
    return True

def process_payment_service(order_id, amount, simulate_failure=False):
    """Simulates processing payment in the Payment Service."""
    print(f"  [Payment Service] Attempting to process payment for order {order_id}, amount: ${amount}")
    if simulate_failure:
        print(f"  [Payment Service] SIMULATING FAILURE for order {order_id}")
        raise Exception("Payment processing failed")
    payment_db[order_id] = {"amount": amount, "status": "paid"}
    print(f"  [Payment Service] Payment processed for order {order_id}.")
    return True

def refund_payment_service(order_id, amount):
    """Compensation for process_payment_service: refunds the payment."""
    print(f"  [Payment Service] Compensating: Refunding payment for order {order_id}, amount: ${amount}")
    if order_id in payment_db and payment_db[order_id]["status"] == "paid":
        payment_db[order_id]["status"] = "refunded"
        print(f"  [Payment Service] Payment for order {order_id} refunded.")
    else:
        print(f"  [Payment Service] No payment found for order {order_id} to refund.")
    return True

# --- SAGA Coordinator ---

class OrderSaga:
    """Orchestrates the distributed transaction using the SAGA pattern."""
    def __init__(self, order_id, items, amount):
        self.order_id = order_id
        self.items = items
        self.amount = amount
        self.completed_steps = [] # Tracks successfully completed steps for compensation

        # Define the SAGA steps: (action_function, compensation_function, args)
        self.saga_steps = [
            (create_order_service, cancel_order_service, (order_id, items)),
            (reserve_inventory_service, release_inventory_service, (order_id, items)),
            (process_payment_service, refund_payment_service, (order_id, amount)),
        ]

    def run(self, simulate_failure_at_step=None):
        print(f"\n--- Starting SAGA for Order {self.order_id} ---")
        try:
            for i, (action, _, args) in enumerate(self.saga_steps):
                print(f"\nStep {i+1}: Executing {action.__name__}")
                # Simulate failure if specified for the current step
                if simulate_failure_at_step == i + 1:
                    action(*args, simulate_failure=True) # Pass simulate_failure to the service
                else:
                    action(*args)
                # If action succeeds, add its action, compensation, and args to completed_steps
                self.completed_steps.append((action, self.saga_steps[i][1], args))
                print(f"Step {i+1}: {action.__name__} completed successfully.")

            print(f"\n--- SAGA for Order {self.order_id} completed successfully! ---")
            return True

        except Exception as e:
            # If any step fails, catch the exception and initiate compensation
            print(f"\n--- SAGA for Order {self.order_id} FAILED at step {len(self.completed_steps) + 1} ({self.saga_steps[len(self.completed_steps)][0].__name__}) ---")
            print(f"Error: {e}")
            self._compensate() # Trigger compensation for all previously completed steps
            print(f"--- SAGA for Order {self.order_id} compensation completed. ---")
            return False

    def _compensate(self):
        """Executes compensation actions for all successfully completed steps in reverse order."""
        print("\n--- Initiating SAGA Compensation ---")
        # Compensate in reverse order of completion
        for action, compensation, args in reversed(self.completed_steps):
            print(f"Compensating for {action.__name__} by calling {compensation.__name__}")
            try:
                compensation(*args)
            except Exception as e:
                print(f"  WARNING: Compensation for {action.__name__} failed: {e}")
        print("--- SAGA Compensation Finished ---")

# --- Main Execution ---
if __name__ == "__main__":
    # Scenario 1: Successful SAGA
    print("==================================================")
    print("SCENARIO 1: Successful Order Process")
    print("==================================================")
    saga1 = OrderSaga("ORDER-001", ["Laptop", "Mouse"], 1200)
    saga1.run()
    print("\nFinal State (ORDER-001):")
    print(f"  Order DB: {order_db.get('ORDER-001')}")
    print(f"  Inventory DB: {inventory_db.get('ORDER-001')}")
    print(f"  Payment DB: {payment_db.get('ORDER-001')}")

    # Reset databases for next scenario
    order_db.clear()
    inventory_db.clear()
    payment_db.clear()

    # Scenario 2: SAGA fails at Payment step (Step 3), triggers compensation
    print("\n\n==================================================")
    print("SCENARIO 2: Order Process Fails at Payment (Step 3)")
    print("==================================================")
    saga2 = OrderSaga("ORDER-002", ["Keyboard"], 150)
    saga2.run(simulate_failure_at_step=3) # Simulate failure at payment step
    print("\nFinal State (ORDER-002) after compensation:")
    print(f"  Order DB: {order_db.get('ORDER-002')}")
    print(f"  Inventory DB: {inventory_db.get('ORDER-002')}")
    print(f"  Payment DB: {payment_db.get('ORDER-002')}")

    # Reset databases for next scenario
    order_db.clear()
    inventory_db.clear()
    payment_db.clear()

    # Scenario 3: SAGA fails at Inventory step (Step 2), triggers compensation
    print("\n\n==================================================")
    print("SCENARIO 3: Order Process Fails at Inventory (Step 2)")
    print("==================================================")
    saga3 = OrderSaga("ORDER-003", ["Monitor"], 300)
    saga3.run(simulate_failure_at_step=2) # Simulate failure at inventory step
    print("\nFinal State (ORDER-003) after compensation:")
    print(f"  Order DB: {order_db.get('ORDER-003')}")
    print(f"  Inventory DB: {inventory_db.get('ORDER-003')}")
    print(f"  Payment DB: {payment_db.get('ORDER-003')}")
