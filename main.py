import sqlite3
import pandas as pd


class OrderFlow:

    def __init__(self, orderbook):
        """Initializing database connection"""
        self.con = sqlite3.connect(orderbook)
        self.cursor = self.con.cursor()

    def add_order(self):
        """method let's it user input order details and saves them in database"""
        order_id = input(str("type order id: "))
        while True:
            # waits for user to input correct value
            order_type = str(input("select operation type [buy/sell]: ")).lower()
            if order_type == 'sell' or order_type == 'buy':
                # breaks infinite loop when got correct value
                break
            else:
                print('No such operation type.')
                # asks for correct value again
                continue
        while True:
            # waits for user to input correct value
            try:
                order_price = float(input("input stock price: "))
                # breaks infinite loop when got correct value
                break
            except ValueError:
                print('Stock price must be integer or float.')
                # asks for correct value again
                continue
        while True:
            # waits for user to input correct value
            try:
                order_quantity = float(input("input stock quantity: "))
                # breaks infinite loop when got correct value
                break
            except ValueError:
                print('Stock quantity must be integer or float.')
                # asks for correct value again
                continue
        row = (order_id, order_type, order_price, order_quantity, "Added")
        # inserts new order into AddedOrders table
        with self.con:
            try:
                self.cursor.execute("INSERT INTO AddedOrders VALUES (?,?,?,?,?);", row)
            except sqlite3.IntegrityError:
                print("Cannot save order. Order with such id already exists.")

    def remove_order(self, order_id):
        """method removes order from AddedOrders and saves it in RemovedOrders table based on order_id"""
        with self.con:
            try:
                # gets order details from AddedOrders table
                row = self.cursor.execute("SELECT order_id, transaction_type, price, quantity" +
                                          f" FROM AddedOrders where order_id ='{order_id}';")
                row = row.fetchone() + ("Removed",)
                # saves order to RemovedOrders table
                self.cursor.execute("INSERT INTO RemovedOrders VALUES (?,?,?,?,?);", row)
                # deletes order from AddedOrders table
                self.cursor.execute(f"DELETE FROM AddedOrders where order_id ='{order_id}';")
            except TypeError:
                print("No such order.")

    def print_all_orders(self):
        # checks if orderbook isn't empty
        record = self.cursor.execute("SELECT * FROM AddedOrders UNION SELECT * FROM RemovedOrders;")
        # prints orders only if orderbook isn't empty -> record.fetchall() != []
        if record.fetchall():
            print()
            print(" " * 10, "All orders on the book")
            print(pd.read_sql_query("SELECT * FROM AddedOrders UNION SELECT * FROM RemovedOrders;", self.con))
        else:
            print("No orders in order book.")

    def best_price_orders_value(self):
        # checks if orderbook isn't empty
        record = self.cursor.execute("SELECT * FROM AddedOrders UNION SELECT * FROM RemovedOrders;")
        # prints only when orderbook isn't empty -> record.fetchall() != []
        if record.fetchall():
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
