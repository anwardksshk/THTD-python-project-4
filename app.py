from peewee import *
from collections import OrderedDict

import csv
import datetime
import os
import re

db = SqliteDatabase('inventory.db')
class Product(Model):
    product_id = IntegerField(primary_key=True, unique=True)
    product_name = CharField(max_length=255, unique=True)
    product_price = IntegerField(default=0)
    product_quantity = IntegerField(default=0)
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


def clear():
    """Clear screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def initialize():
    """Create/open database and the table"""
    db.connect()
    db.create_tables([Product], safe=True)
    with open('inventory.csv', newline='') as csvfile:
        inventory = csv.DictReader(csvfile, delimiter=',')
        rows = list(inventory)
        for value in rows:
            try:
                Product.create(product_name=value['product_name'], 
                            product_price=format_int(value['product_price']),
                            product_quantity=int(value['product_quantity']),
                            date_updated=datetime.datetime.strptime(value['date_updated'], '%m/%d/%Y'))
            except IntegrityError:
                product_record = Product.get(product_name=value['product_name'])
                product_record.product_price = format_int(value['product_price'])
                product_record.product_quantity = int(value['product_quantity'])
                product_record.date_updated = datetime.datetime.strptime(value['date_updated'], '%m/%d/%Y')
                product_record.save()


def as_currency(cents):
    """Format price in cents to $x.xx dollar format."""
    real_price = cents / 100
    return "${:.2f}".format(real_price)


def format_int(str_num):
    """Convert string price to integer price in cents."""
    unwanted_char = ['$', '.']
    for char in unwanted_char:
        str_num = str_num.replace(char, '').lstrip("0") #lstrip removes leading zeros
    return int(str_num)


def menu():
    """Show Menu"""
    choice = None

    while choice != 'q':
        clear()
        print("MENU\n" + "=" * 10)
        for key, value in menu_list.items():
            print('({}) {}'.format(key, value.__doc__))
        print("Enter 'q' to quit.")

        try:
            choice = input("\nAction=> ").lower().strip()

            if choice not in menu_list and choice.lower() != 'q':
                raise ValueError
        except ValueError:
            print("ERROR! That is not a valid menu option. Try again.")
            if input("Press enter to continue.."):
                continue
        
        if choice in menu_list:
            clear()
            menu_list[choice]()           


def view_product():
    """View a single product's inventory"""
    clear()
    while True:
        try:
            query = int(input("Look for product ID: "))
            product = Product.get(Product.product_id == query)
        except DoesNotExist:
            print("No item with an ID of {} exists, please enter a valid ID".format(query))
        else:
            clear()

            print(
                "ID: {}\n".format(product.product_id) +
                "Item: {}\n".format(product.product_name) +
                "Price: {}\n".format(as_currency(product.product_price)) +
                "Quantity: {}\n".format(product.product_quantity) +
                "Last updated: {}\n".format(product.date_updated)
            ) 

            view_again = input("\nWould you like to view another product? (Y/N) ")
            if view_again.lower() != 'y':
                break


def add_product():
    """Add a new product to the database"""
    clear()
    print("Adding a product\n" + "=" * 10)
    product_name = input("Product Name: ")

    while True: #get product price in the correct format
        try: 
            product_price = input("Product Price: $")
            if "." in product_price:
                if len(product_price.split(".", 1)[1]) < 2 or len(product_price.split(".", 1)[0]) == 0: #if price in the form of $2.3 or .3 or .32 or 2.
                    raise ValueError("Please enter in the $x.xx format.")
            elif "." not in product_price: #if $2 or $200 or $30
                raise ValueError("Please enter in the $x.xx format.")
        except ValueError as err:
            print("{}".format(err))
        else:
            product_price = format_int(product_price)
            break 
    
    while True: #get product quantity only numbers
        try:
            product_quantity = input("Quantity: ")
            if re.search(r'[\D]', product_quantity):
                raise ValueError("Please only key in a number value.")
        except ValueError as err:
            print("{}".format(err))
        else:
            product_quantity = int(product_quantity)
            break 

    date_added = datetime.datetime.now().strftime('%d/%m/%Y')

    confirm = input("Add product? (Y/N) ")
    if confirm.lower() == 'y':
        try: #if duplicate exist ovewrites
            Product.create(product_name=product_name, 
                            product_price=product_price,
                            product_quantity=product_quantity,
                            date_updated=date_added) 
        except IntegrityError:
            product_record = Product.get(product_name=product_name)
            product_record.product_price = product_price
            product_record.product_quantity = product_quantity
            product_record.date_updated = date_added
            product_record.save()


def backup():
    """Make a backup of the entire inventory"""
    clear()
    with open("backup.csv", "w") as csvfile:
        fieldnames = ['product_name', 
            'product_price', 
            'product_quantity', 
            'date_updated']
        backupwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        backupwriter.writeheader()

        inventory = Product.select().order_by(Product.product_id)
        for product in inventory:
            backupwriter.writerow({
                'product_name': "{}".format(product.product_name),
                'product_price': "{}".format(as_currency(product.product_price)),
                'product_quantity': "{}".format(product.product_quantity),
                'date_updated': "{}".format(product.date_updated)
            })

    print("BACKUP COMPLETE!")
    confirm = input("Press enter to continue...")
    if confirm:
        pass


#===================================MAIN PROGRAM===================================
if __name__ == '__main__':
    menu_list = OrderedDict([
        ('v', view_product),
        ('a', add_product),
        ('b', backup)
    ])

    initialize()
    menu()  

    print("\n(END PROGRAM)")