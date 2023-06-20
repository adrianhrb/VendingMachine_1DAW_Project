# ******************
# MÁQUINA DE VENDING
# ******************
import filecmp
from pathlib import Path


# LECTURA DE DATOS
def read_operations(operations_path: Path):
    processed_operations = []
    with open(operations_path) as operations:
        entry_operations = "".join(operations).strip().split("\n")
        for i, operation in enumerate(entry_operations, start=0):
            processed_operations.append([])
            subelements = operation.split()
            for subelement in subelements:
                if subelement.isdigit():
                    processed_operations[i].append(int(subelement))
                else:
                    processed_operations[i].append(subelement)
    return processed_operations

# ESCRITURA DE DATOS
def write_status(status_path: Path, vending: dict):
    with open(status_path, "w") as output: 
        output.write(f'{vending["cash"]}\n')
        for product, p_info in sorted(vending["products"].items()):
            stock, price = p_info
            output.write(f"{product} {stock} {price}\n")

# INTERACCION CON MONEDAS
def enough_cash(to_pay: int, cash: int) -> bool:
    return cash >= to_pay

# PAGO
def order(product: str, amount: int, cash: int, vending: dict):
    debt = amount * vending["products"][product][1]
    if enough_cash(debt, cash) and amount <= vending["products"][product][0]:
        vending["products"][product][0] -= amount
        vending["cash"] += debt

# CAMBIO DE PRECIO
def price_update(prod: str, price: int, vending: dict):
    if prod in vending["products"]:
        vending["products"][prod][1] = price

# ACTUALIZACIÓN DE EXISTENCIA
def restock(operation: list, vending: dict):
    prod, restocked_amount = operation
    if prod in vending["products"].keys():
        vending["products"][prod][0] += restocked_amount
    else:
        vending["products"][prod] = [restocked_amount, 0]


# ACTUALIZACIÓN DEL DINERO DE LA MÁQUINA
def cash_restock(cash: int, vending: dict):
    vending["cash"] += cash


# OPERACIONES DE CAMBIO DE PRECIO, REPOSICIÓN DE EXISTENCIAS, COMPRA Y REPOSICIÓN DE MONEDAS
ORDER_TYPES = ["P", "R", "O", "M"]
def check_products(operations: list, vending: dict) -> dict:
    price_change, product_restock, request_product, restock_cash = ORDER_TYPES
    for operation in operations:
        order_type = operation[0]
        if order_type == restock_cash:
            cash = operation[1]
            cash_restock(cash, vending)
        elif order_type == price_change:
            product, price = operation[1:]
            price_update(product, price, vending)
        elif order_type == request_product:
            product, amount, cash = operation[1:]
            if product in vending["products"].keys():
                order(product, amount, cash, vending)
        elif order_type == product_restock:
            restock(operation[1:], vending)
    return vending

def run(operations_path: Path) -> bool:
    machine_info = {"cash": 0, "products": {}}
    status_path = 'data/vending/status.dat'
    processed_operations = read_operations(operations_path)
    machine_info = check_products(processed_operations, machine_info)
    write_status(status_path, machine_info)
    return filecmp.cmp(status_path, 'data/vending/.expected', shallow=False)

if __name__ == '__main__':
    run('data/vending/operations.dat')