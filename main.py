import sqlite3
import pandas as pd


class OrderFlow:

    def __init__(self, orderbook):
        """Initializing database connection"""
        self.con = sqlite3.connect(orderbook)
        self.cursor = self.con.cursor()

    @staticmethod
    def input_type():
        """asks user for order type (buy/sell)"""
        while True:
            # waits for user to input correct value
            order_type = str(input("select order type [buy/sell]: ")).lower()
            if order_type == 'sell' or order_type == 'buy':
                # breaks infinite loop when got correct value
                break
            else:
                print('No such order type.')
                # asks for correct value again
        return order_type

    @staticmethod
    def input_price():
        """asks user for stock price"""
        while True:
            try:
                order_price = float(input("input stock price: "))
                break
            except ValueError:
                print('Stock price must be integer or float.')
        return order_price

    @staticmethod
    def input_quantity():
        """asks user for stock quantity"""
        while True:
            try:
                order_quantity = float(input("input stock quantity: "))
                break
            except ValueError:
                print('Stock quantity must be integer or float.')
        return order_quantity

    def add_order(self):
        """method let's it user input order details and saves them in database"""
        order_type = self.input_type()
        order_price = self.input_price()
        order_quantity = self.input_quantity()
        row = (order_price, order_quantity, order_type, 1)
        # inserts new order into AddedOrders table
        with self.con:
            self.cursor.execute("INSERT INTO Orders(price, quantity, order_type, active) VALUES (?,?,?,?);", row)
            order_id = self.cursor.execute("SELECT MAX(order_id) FROM Orders;")
            print(f"Order saved. Your order's id: {order_id.fetchone()[0]}")

    def remove_order(self, order_id):
        """sets value in active column to 0 for a given order_id"""
        with self.con:
            try:
                self.cursor.execute(f"UPDATE Orders SET active = 0 where order_id = {order_id};")
                print(f"Order with id {order_id} was removed.")
            except TypeError:
                print("No such order.")

    def print_all_orders(self):
        """prints all orders on the book"""
        # checks if orderbook isn't empty
        record = self.cursor.execute("SELECT * FROM Orders;")
        # prints orders only if orderbook isn't empty -> record.fetchall() != []
        if record.fetchall():
            print()
            print(" " * 10, "All orders on the book")
            print(pd.read_sql_query("SELECT * FROM Orders;", self.con))
        else:
            print("No orders in order book.")

    def best_price_orders_value(self):
        """prints value of both types orders with the best price"""
        # checks if orderbook isn't empty
        record = self.cursor.execute("SELECT * FROM Orders;")
        # prints only when orderbook isn't empty -> record.fetchall() != []
        if record.fetchall():
            print()
            print(" "*10, "Best orders on the book")
            print(pd.read_sql_query("SELECT order_id, price, price*quantity AS value, order_type "
                                    "FROM Orders WHERE order_type = 'buy' AND price IN "
                                    "(SELECT MAX(price) FROM Orders WHERE order_type = 'buy' AND active = 1) "
                                    "UNION "
                                    "SELECT order_id, price, price*quantity AS value, order_type "
                                    "FROM Orders WHERE order_type = 'sell' AND price IN "
                                    "(SELECT MIN(price) FROM Orders WHERE order_type = 'sell' AND active = 1) "
                                    "ORDER BY order_type DESC;", self.con))
            print()


if __name__ == '__main__':
    of = OrderFlow("OrderBook.db")
    while True:
        of.best_price_orders_value()
        operation = str(input("choose operation type [add/remove/show orders/quit]: "))
        if operation == 'add':
            of.add_order()
        elif operation == 'remove':
            of.remove_order(str(input("input order id you want to remove: ")))
        elif operation == 'show orders':
            of.print_all_orders()
        elif operation == 'quit':
            break
        else:
            print('No such operation.')
