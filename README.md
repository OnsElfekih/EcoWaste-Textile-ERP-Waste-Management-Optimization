# EcoWaste Textile – ERP Waste Management Optimization

## Project Overview

EcoWaste Textile is an ERP project developed using **Odoo 17 Community Edition**, **Python**, and **PostgreSQL**.

The project focuses on improving textile waste management through automated waste classification, recovery recommendations, and inventory tracking.

## Objectives

- Optimize textile waste management.
- Automate waste recovery recommendations.
- Improve waste traceability and inventory monitoring.
- Support sustainable resource management in the textile industry.

## Technologies

| Technology | Purpose |
|------------|---------|
| Python | Backend development and business logic |
| Odoo 17 Community | ERP platform |
| PostgreSQL | Database management |
| XML | Interface customization |
| PyCharm | Development environment |
| Git & GitHub | Version control |

## Features

- Extension of the existing Odoo `stock.scrap` model.
- Textile material classification.
- Waste origin and cause identification.
- Waste quality and size evaluation.
- Automated recovery recommendations.
- Integration with Odoo Inventory.
- Waste tracking through stock operations.

## Recovery Recommendation System

The system generates recovery recommendations based on textile quality and waste size.

### Input Parameters

- **Textile Material:** Cotton, Polyester, Mixed
- **Waste Origin:** Cutting, Sewing, Quality Control
- **Waste Cause:** Offcut, Defect, Error
- **Textile Quality:** Good, Medium, Poor
- **Scrap Size:** Small, Medium, Large

### Recovery Recommendations

| Recommendation | Description |
|----------------|-------------|
| Reuse | Reuse textile waste when suitable |
| Recycle | Process textile waste for recycling |
| Review | Require additional evaluation |
| Disposal | Dispose of waste when recovery is unsuitable |

The recommendation updates automatically when the relevant waste characteristics change.

## Project Architecture

```text
Odoo 17 Community
        |
        v
Custom EcoWaste Textile Module
        |
        v
Waste Classification
        |
        v
Recovery Recommendation System
        |
        v
Odoo Inventory Management
        |
        v
PostgreSQL Database
```

## Project Structure

```text
ecowaste-textile-odoo/
|
|-- EcoWasteTextile/
|   |-- __init__.py
|   |-- __manifest__.py
|   |
|   |-- models/
|   |   |-- __init__.py
|   |   |-- stock_scrap.py
|   |
|   |-- views/
|       |-- stock_scrap_views.xml
|
|-- screenshots/
|   |-- waste-classification.png
|   |-- recovery-recommendation.png
|   |-- inventory-tracking.png
|
|-- README.md
|-- .gitignore
|-- LICENSE
```

## Installation

### Prerequisites

- Odoo 17 Community Edition
- Python
- PostgreSQL

### Steps

1. Clone the repository.

```bash
git clone https://github.com/OnsElfekih/ecowaste-textile-odoo.git
```

2. Copy the `EcoWasteTextile` module into your Odoo custom addons directory.

3. Add the custom addons directory to the `addons_path` parameter in your Odoo configuration.

4. Restart the Odoo server.

5. Activate Developer Mode in Odoo.

6. Navigate to **Apps** and select **Update Apps List**.

7. Search for **EcoWaste Textile** and install the module.

## Screenshots

### Waste Classification

![Waste Classification](screenshots/waste-classification.png)

### Automated Recovery Recommendation

![Recovery Recommendation](screenshots/recovery-recommendation.png)

### Inventory Tracking

![Inventory Tracking](screenshots/inventory-tracking.png)

## Project Status

**Current Progress:**

- [x] Odoo 17 Community environment setup
- [x] Custom module development
- [x] Extension of the stock.scrap model
- [x] Textile waste classification
- [x] Automated recovery recommendations
- [x] Inventory integration
- [x] Functional testing
- [ ] Machine learning integration
- [ ] Analytics dashboards
- [ ] Waste reduction KPIs

## Future Improvements

- Integrate machine learning for recovery recommendations.
- Develop waste analytics dashboards.
- Introduce waste reduction KPIs.
- Improve reporting and traceability.

## Author

**Ons Elfekih**

Business Intelligence Engineering Student

GitHub: [OnsElfekih](https://github.com/OnsElfekih)
