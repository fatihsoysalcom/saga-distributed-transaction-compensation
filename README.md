# SAGA Distributed Transaction Compensation

This example demonstrates the SAGA pattern for managing distributed transactions in a microservice architecture. It simulates an order processing flow (create order, reserve inventory, process payment) and shows how compensation actions are triggered in reverse order if any step fails, ensuring data consistency across services.

## Language

`python`

## How to Run

Save the code as `main.py` and run it from your terminal:
`python main.py`

## Original Article

This example accompanies the Turkish article: [Mikroservis Mimarilerinde ve Yapay Zeka Ajanlarında Güvenilirliği Sağlamak: SAGA ve Agent Harness](https://fatihsoysal.com/blog/mikroservis-mimarilerinde-ve-yapay-zeka-ajanlarinda-guvenilirligi-saglamak-saga-ve-agent-harness/).

## License

MIT — see [LICENSE](LICENSE).
