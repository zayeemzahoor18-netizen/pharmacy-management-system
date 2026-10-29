
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
import math

app = Flask(__name__)
app.config["SECRET_KEY"] = "pharmacy-secret-key"

DATABASE = Path(__file__).resolve().parent / "pharmacy.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def medicine_object(row):
    data = dict(row)
    data["expiry_date"] = date.fromisoformat(data["expiry_date"])
    return SimpleNamespace(**data)


def sale_object(row):
    data = dict(row)
    data["sale_date"] = date.fromisoformat(data["sale_date"])
    return SimpleNamespace(**data)


def init_db():
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS medicine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT NOT NULL,
                batch TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0,
                expiry_date TEXT NOT NULL,
                low_stock_limit INTEGER NOT NULL DEFAULT 10
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS sale (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                total REAL NOT NULL,
                sale_date TEXT NOT NULL
            )
        """)


@app.route("/")
def dashboard():
    today = date.today()
    soon = today + timedelta(days=30)

    with get_db() as connection:
        rows = connection.execute(
            "SELECT * FROM medicine ORDER BY name"
        ).fetchall()

    medicines_list = [medicine_object(row) for row in rows]

    total_medicines = len(medicines_list)

    low_stock = [
        medicine for medicine in medicines_list
        if medicine.quantity <= medicine.low_stock_limit
    ]

    expired = [
        medicine for medicine in medicines_list
        if medicine.expiry_date < today
    ]

    expiring_soon = [
        medicine for medicine in medicines_list
        if today <= medicine.expiry_date <= soon
    ]

    return render_template(
        "dashboard.html",
        total_medicines=total_medicines,
        low_stock=low_stock,
        expired=expired,
        expiring_soon=expiring_soon
    )


@app.route("/medicines")
def medicines():
    search = request.args.get("search", "").strip()

    with get_db() as connection:
        if search:
            rows = connection.execute(
                """
                SELECT * FROM medicine
                WHERE name LIKE ?
                ORDER BY name
                """,
                (f"%{search}%",)
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM medicine ORDER BY name"
            ).fetchall()

    medicine_list = [medicine_object(row) for row in rows]

    return render_template(
        "medicines.html",
        medicines=medicine_list,
        search=search,
        today=date.today()
    )


@app.route("/add", methods=["GET", "POST"])
def add_medicine():
    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            company = request.form["company"].strip()
            batch = request.form["batch"].strip()
            quantity = int(request.form["quantity"])
            price = float(request.form["price"])
            expiry_date = date.fromisoformat(
                request.form["expiry_date"]
            )
            low_stock_limit = int(
                request.form.get("low_stock_limit", 10)
            )

            if (
                not name
                or not company
                or not batch
                or not math.isfinite(price)
                or quantity < 0
                or price < 0
                or low_stock_limit < 0
            ):
                raise ValueError

            with get_db() as connection:
                connection.execute("""
                    INSERT INTO medicine (
                        name, company, batch, quantity, price,
                        expiry_date, low_stock_limit
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    company,
                    batch,
                    quantity,
                    price,
                    expiry_date.isoformat(),
                    low_stock_limit
                ))

            flash("Medicine added successfully!", "success")
            return redirect(url_for("medicines"))

        except (ValueError, KeyError):
            flash("Please enter valid medicine details.", "danger")

    return render_template("medicine_form.html", medicine=None)


@app.route("/edit/<int:medicine_id>", methods=["GET", "POST"])
def edit_medicine(medicine_id):
    with get_db() as connection:
        row = connection.execute(
            "SELECT * FROM medicine WHERE id = ?",
            (medicine_id,)
        ).fetchone()

    if row is None:
        flash("Medicine not found.", "danger")
        return redirect(url_for("medicines"))

    medicine = medicine_object(row)

    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            company = request.form["company"].strip()
            batch = request.form["batch"].strip()
            quantity = int(request.form["quantity"])
            price = float(request.form["price"])
            expiry_date = date.fromisoformat(
                request.form["expiry_date"]
            )
            low_stock_limit = int(
                request.form.get("low_stock_limit", 10)
            )

            if (
                not name
                or not company
                or not batch
                or not math.isfinite(price)
                or quantity < 0
                or price < 0
                or low_stock_limit < 0
            ):
                raise ValueError

            with get_db() as connection:
                connection.execute("""
                    UPDATE medicine
                    SET name = ?, company = ?, batch = ?,
                        quantity = ?, price = ?, expiry_date = ?,
                        low_stock_limit = ?
                    WHERE id = ?
                """, (
                    name,
                    company,
                    batch,
                    quantity,
                    price,
                    expiry_date.isoformat(),
                    low_stock_limit,
                    medicine_id
                ))

            flash("Medicine updated successfully!", "success")
            return redirect(url_for("medicines"))

        except (ValueError, KeyError):
            flash("Please enter valid medicine details.", "danger")

    return render_template("medicine_form.html", medicine=medicine)


@app.route("/delete/<int:medicine_id>", methods=["POST"])
def delete_medicine(medicine_id):
    with get_db() as connection:
        connection.execute(
            "DELETE FROM medicine WHERE id = ?",
            (medicine_id,)
        )

    flash("Medicine deleted successfully!", "success")
    return redirect(url_for("medicines"))


@app.route("/stock")
def stock():
    today = date.today()
    soon = today + timedelta(days=30)

    with get_db() as connection:
        rows = connection.execute(
            "SELECT * FROM medicine ORDER BY expiry_date"
        ).fetchall()

    medicines_list = [medicine_object(row) for row in rows]

    low_stock = [
        medicine for medicine in medicines_list
        if medicine.quantity <= medicine.low_stock_limit
    ]

    expired = [
        medicine for medicine in medicines_list
        if medicine.expiry_date < today
    ]

    expiring = [
        medicine for medicine in medicines_list
        if today <= medicine.expiry_date <= soon
    ]

    return render_template(
        "stock.html",
        low_stock=low_stock,
        expired=expired,
        expiring=expiring
    )


@app.route("/billing", methods=["GET", "POST"])
def billing():
    if request.method == "POST":
        try:
            medicine_id = int(request.form["medicine_id"])
            quantity = int(request.form["quantity"])
            discount_percent = float(
                request.form.get("discount_percent", "0")
            )

            if (
                quantity <= 0
                or not math.isfinite(discount_percent)
                or not 0 <= discount_percent <= 100
            ):
                raise ValueError

        except (ValueError, KeyError):
            flash(
                "Enter a valid medicine, quantity and discount.",
                "danger"
            )
            return redirect(url_for("billing"))

        with get_db() as connection:
            # Recheck stock and expiry immediately before the sale.
            connection.execute("BEGIN IMMEDIATE")

            row = connection.execute(
                "SELECT * FROM medicine WHERE id = ?",
                (medicine_id,)
            ).fetchone()

            if row is None:
                flash("Medicine not found.", "danger")

            elif date.fromisoformat(row["expiry_date"]) < date.today():
                flash(
                    "This medicine has expired and cannot be sold.",
                    "danger"
                )

            elif row["quantity"] < quantity:
                flash("Not enough stock available.", "danger")

            else:
                subtotal = round(row["price"] * quantity, 2)
                discount_amount = round(
                    subtotal * discount_percent / 100, 2
                )
                final_total = round(subtotal - discount_amount, 2)

                connection.execute("""
                    UPDATE medicine
                    SET quantity = quantity - ?
                    WHERE id = ?
                """, (quantity, medicine_id))

                connection.execute("""
                    INSERT INTO sale (
                        medicine_name, quantity, total, sale_date
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    row["name"],
                    quantity,
                    final_total,
                    date.today().isoformat()
                ))

                flash(
                    f"Sale completed! Subtotal: ₹{subtotal:.2f}; "
                    f"Discount: ₹{discount_amount:.2f}; "
                    f"Final total: ₹{final_total:.2f}",
                    "success"
                )
                return redirect(url_for("sales"))

        return redirect(url_for("billing"))

    today = date.today()

    with get_db() as connection:
        rows = connection.execute("""
            SELECT * FROM medicine
            WHERE quantity > 0
            ORDER BY name
        """).fetchall()

    medicines_list = [
        medicine_object(row)
        for row in rows
        if date.fromisoformat(row["expiry_date"]) >= today
    ]

    return render_template(
        "billing.html",
        medicines=medicines_list
    )


@app.route("/sales")
def sales():
    with get_db() as connection:
        rows = connection.execute(
            "SELECT * FROM sale ORDER BY id DESC"
        ).fetchall()

    sales_list = [sale_object(row) for row in rows]
    total_revenue = sum(sale.total for sale in sales_list)

    return render_template(
        "sales.html",
        sales=sales_list,
        total_revenue=total_revenue
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
