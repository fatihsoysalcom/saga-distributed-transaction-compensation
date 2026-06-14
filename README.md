# saga-distributed-transaction-compensation
This example demonstrates the SAGA pattern for managing distributed transactions in a microservice architecture. It simulates an order processing flow (create order, reserve inventory, process payment) and shows how compensation actions are triggered in reverse order if any step fails, ensuring data consistency across services.
