# Pharmacy Management System

A web-based Pharmacy Management System built using **Python, Flask, and SQLite**. This application helps manage medicine inventory, track stock levels and expiry dates, process sales, and maintain sales records.

## Features

- **Dashboard:** View total medicines, low-stock medicines, expired medicines, and medicines expiring soon.
- **Medicine Management:** Add, edit, delete, and search medicine records.
- **Stock Management:** Monitor medicine quantities and identify low-stock items.
- **Expiry Tracking:** Identify expired medicines and medicines expiring within the next 30 days.
- **Billing System:** Process medicine sales and calculate the total bill.
- **Automatic Stock Update:** Reduce medicine quantities after a successful sale.
- **Sales History:** View previous sales and total recorded revenue.
- **Data Storage:** Store medicine and sales records using an SQLite database.

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- Jinja2 Templates

## Project Structure

```text
Pharmacy-Management-System/
│
├── app.py
├── pharmacy.db
├── requirements.txt
├── README.md
├── .gitignore
│
└── templates/
    ├── dashboard.html
    ├── medicines.html
    ├── medicine_form.html
    ├── stock.html
    ├── billing.html
    └── sales.html
```

## Installation and Setup

### 1. Install Python

Install Python on your computer if it is not already installed.

### 2. Open the Project Directory

Open a terminal or command prompt in the project folder.

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

### 7. Open in Browser

Visit the following address:

http://127.0.0.1:5000/

## Application Pages

| Page | Route | Description |
|---|---|---|
| Dashboard | `/` | Displays inventory summaries and alerts |
| Medicines | `/medicines` | Lists and searches medicines |
| Add Medicine | `/add` | Adds a new medicine |
| Edit Medicine | `/edit/<medicine_id>` | Updates medicine details |
| Stock Management | `/stock` | Displays stock and expiry alerts |
| Billing | `/billing` | Processes medicine sales |
| Sales History | `/sales` | Displays sales records and revenue |

## Database

The application uses **SQLite** to store medicine and sales information.

The medicine table stores the medicine name, company, batch number, quantity, price, expiry date, and low-stock limit.

The sale table stores the medicine name, quantity sold, total sale amount, and sale date.

The application creates the required database tables when it is started directly using `python app.py`.

## Validation and Stock Control

- Prevents negative medicine quantities and prices.
- Validates medicine details before saving.
- Prevents sales of expired medicines.
- Prevents selling quantities greater than the available stock.
- Updates inventory automatically after successful sales.
- Displays alerts for low-stock and soon-to-expire medicines.

## Future Enhancements

- User authentication and role-based access.
- Printable invoices and receipts.
- Supplier and purchase management.
- Advanced sales reports.
- Improved security and production deployment.

## Security Notes

The built-in Flask development server is intended for development only. Before production deployment, configure a secure secret key using an environment variable and disable debug mode.

## Conclusion

The Pharmacy Management System provides a simple way to manage pharmacy inventory, monitor medicine expiry dates, process billing, and maintain sales records. It uses Python, Flask, and SQLite to provide a lightweight application for pharmacy management.

## License

No license has been specified for this project.
