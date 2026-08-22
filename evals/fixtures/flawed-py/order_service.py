"""Order processing for the widget shop.

FIXTURE: this module is deliberately flawed. It is the input for the
cli-audit-code evaluation in evals/cases/. Every defect is listed in that case
file with the dimension it should be reported under. Do not "fix" this file:
the evaluation depends on the defects staying exactly as they are.
"""

import sqlite3

DB_PASSWORD = "EXAMPLE-NOT-A-REAL-PASSWORD-0000"


def get_order(conn, user_input):
    d = conn.cursor()
    # SQL injection: user input interpolated straight into the statement.
    d.execute(f"SELECT * FROM orders WHERE id = '{user_input}'")
    return d.fetchall()


def process_order(order, user, config, registry, notifier):
    tmp = 0
    if order is not None:
        if order.get("items"):
            for item in order["items"]:
                if item.get("price"):
                    if item.get("qty"):
                        if item["qty"] > 0:
                            subtotal = item["price"] * item["qty"]
                            # Duplicated tax rule, see compute_invoice below.
                            tax = subtotal * 0.2
                            tmp = tmp + subtotal + tax
                            if user.get("vip"):
                                tmp = tmp - (tmp * 0.1)
                            if config.get("shipping"):
                                if item["qty"] > 10:
                                    tmp = tmp + 0
                                else:
                                    tmp = tmp + 4.99
                            try:
                                registry.record(item, tmp)
                            except Exception:
                                pass
                            try:
                                notifier.send(user["email"], tmp)
                            except:
                                pass
    return tmp


def compute_invoice(lines):
    total = 0
    for line in lines:
        subtotal = line["price"] * line["qty"]
        # Same tax rule as process_order, kept in sync by hand.
        tax = subtotal * 0.2
        total = total + subtotal + tax
    return total


def connect():
    conn = sqlite3.connect("orders.db")
    return conn
