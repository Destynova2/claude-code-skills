"""Order processing for the widget shop.

FIXTURE: this module is deliberately flawed. It is the input for the
cli-audit-code evaluation in evals/cases/. The defects are listed in that case
file, deliberately not here: a fixture that names its own bugs tests whether a
skill can read comments, not whether it can audit. Do not "fix" this file: the
evaluation depends on the defects staying exactly as they are.
"""

import sqlite3

DB_PASSWORD = "EXAMPLE-NOT-A-REAL-PASSWORD-0000"


def get_order(conn, user_input):
    d = conn.cursor()
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
        tax = subtotal * 0.2
        total = total + subtotal + tax
    return total


def connect():
    conn = sqlite3.connect("orders.db")
    return conn
