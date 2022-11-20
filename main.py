import sqlite3
import pandas as pd

"""
OrderBook.db schema:

CREATE TABLE Orders(
order_id INTEGER PRIMARY KEY,
price REAL NOT NULL,
quantity REAL NOT NULL,
order_type TEXT NOT NULL,
active INTEGER DEFAULT 1 NOT NULL);
"""


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

    @staticmethod
    def input_order_id():
        while True:
            try:
                order_id = int(input("input order id you want to remove: "))
                break
            except ValueError:
                print('Order id must be an integer.')
        return order_id

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

    def remove_order(self):
        """sets value in active column to 0 for a given order_id"""
        order_id = self.input_order_id()
        record = self.cursor.execute(f"SELECT * FROM Orders WHERE order_id = {order_id}")
        if record.fetchone():
            with self.con:
                self.cursor.execute(f"UPDATE Orders SET active = 0 where order_id = {order_id};")
                print(f"Order with id {order_id} was removed.")
        else:
            print("No order with such id in order book.")

    def print_all_orders(self):
        """prints all orders on the book"""
        # checks if orderbook isn't empty
        record = self.cursor.execute("SELECT * FROM Orders;")
        # prints orders only if orderbook isn't empty -> record.fetchall() != []
        if record.fetchall():
            print()
            print(" " * 10, "All orders on the book")
            sql_query = pd.read_sql_query("SELECT * FROM Orders;", self.con)
            df = pd.DataFrame(sql_query, columns=['order_id', 'order_type', 'price', 'quantity', 'active'])
            print(df.to_string(index=False))
            print()
        else:
            print("No orders in order book.")

    def best_prices(self):
        """prints sum of sell/buy orders with the best price"""
        record = self.cursor.execute(
            "SELECT order_type as 'order type', price as 'best price', SUM(quantity) as ' orders sum' "
            "FROM Orders WHERE active=1 AND order_type = 'buy' "
            "GROUP BY price ORDER BY price ASC LIMIT 1")
        buy_df = pd.DataFrame(record.fetchall(), columns=['order type', 'best price', 'orders sum'])
        record = self.cursor.execute(
            "SELECT order_type as 'order type', price as 'best price', SUM(quantity) as 'orders sum' "
            "FROM Orders WHERE active=1 AND order_type = 'sell' "
            "GROUP BY price ORDER BY price DESC LIMIT 1")
        sell_df = pd.DataFrame(record.fetchall(), columns=['order type', 'best price', 'orders sum'])
        print(" " * 7, "Current best prices")
        print((pd.concat([buy_df, sell_df])).to_string(index=False))


if __name__ == '__main__':
    of = OrderFlow("OrderBook.db")
    while True:
        of.best_prices()
        operation = str(input("choose operation type [add/remove/show orders/quit]: ")).lower()
        if operation == 'add':
            of.add_order()
        elif operation == 'remove':
            of.remove_order()
        elif operation == 'show orders':
            of.print_all_orders()
        elif operation == 'quit':
            break
        else:
            print('No such operation.')
