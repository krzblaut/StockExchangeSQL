import sqlite3
import pandas as pd


class OrderFlow:

    def __init__(self, orderbook):
        self.con = sqlite3.connect(orderbook)
        self.cursor = self.con.cursor()

    def add_order(self):
        order_id = input(str("type order id: "))
        while True:
            order_type = str(input("select operation type [buy/sell]: ")).lower()
            if order_type == 'sell' or order_type == 'buy':
                break
            else:
                print('No such operation type.')
                continue
        while True:
            try:
                order_price = float(input("input stock price: "))
                break
            except ValueError:
                print('Stock price must be integer or float.')
                continue
        while True:
            try:
                order_quantity = float(input("input stock quantity: "))
                break
            except ValueError:
                print('Stock quantity must be integer or float.')
                continue
        row = (order_id, order_type, order_price, order_quantity, "Added")
        with self.con:
            self.cursor.execute("INSERT INTO AddedOrders VALUES (?,?,?,?,?);", row)

    def remove_order(self, order_id):
        with self.con:
            try:
                row = self.cursor.execute("SELECT order_id, transaction_type, price, quantity" +
                                          f" FROM AddedOrders where order_id ='{order_id}';")
                row = row.fetchone() + ("Added",)
                self.cursor.execute("INSERT INTO RemovedOrders VALUES (?,?,?,?,?);", row)
                self.cursor.execute(f"DELETE FROM AddedOrders where order_id ='{order_id}';")
            except TypeError:
                print("No such order.")

    def print_all_orders(self):
        record = self.cursor.execute("SELECT * FROM AddedOrders UNION SELECT * FROM RemovedOrders;")
        if record.fetchall():
            print()
            print(" " * 10, "All orders on the book")
            print(pd.read_sql_query("SELECT * FROM AddedOrders UNION SELECT * FROM RemovedOrders;", self.con))
        else:
            print("No orders in order book.")

    def best_price_orders_value(self):
        record = self.cursor.execute("SELECT * FROM AddedOrders UNION SELECT * FROM RemovedOrders;")
        if record.fetchall():  # print only when orderbook is not empty
            print()
            print(" "*10, "Best orders on the book")
            print(pd.read_sql_query("SELECT order_id, price, price*quantity AS value, transaction_type "
                                    "FROM AddedOrders "
                                    "WHERE price IN "
                                    "(SELECT MAX(price) FROM AddedOrders WHERE transaction_type = 'buy') "
                                    "UNION "
                                    "SELECT order_id, price, price*quantity AS value, transaction_type "
                                    "FROM AddedOrders "
                                    "WHERE price IN "
                                    "(SELECT MIN(price) FROM AddedOrders WHERE transaction_type = 'sell');", self.con))


if __name__ == '__main__':
    of = OrderFlow("OrderBook.db")
    while True:
        of.best_price_orders_value()
        operation = str(input("choose operation type [add/remove/print/quit]: "))
        if operation == 'add':
            of.add_order()
        elif operation == 'remove':
            of.remove_order(str(input("input order id you want to remove: ")))
        elif operation == 'print':
            of.print_all_orders()
        elif operation == 'quit':
            break
        else:
            print('No such operation.')
