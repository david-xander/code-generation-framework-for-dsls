class Process:
    def __init__(self, name):
        self.name = name

class Route:
    def __init__(self, processes):
        self.processes = processes  # List of Process instances

class ProductionOrder:
    def __init__(self, product, route):
        self.product = product
        self.route = route  # Route instance

def check_production_order_constraints(production_orders):
    for order in production_orders:
        processes = order.route.processes
        preparation_found = False
        valid_process_before_preparation = False
        
        for process in processes:
            if process.name == 'Preparation':
                preparation_found = True
                # If we found preparation, check if we had a valid process before it
                if valid_process_before_preparation:
                    break  # No need to check further, we can stop here
            elif process.name in ['Sublimation', 'Sewing']:
                valid_process_before_preparation = True
        
        # If preparation is found but no valid process before it, return False
        if preparation_found and not valid_process_before_preparation:
            return False
    
    return True  # All production orders comply with the constraints

# Example usage:
process1 = Process('Cutting')
process2 = Process('Sublimation')
process3 = Process('Preparation')

route1 = Route([process1, process2, process3])
production_order1 = ProductionOrder('Custom Shirt', route1)

process4 = Process('Cutting')
process5 = Process('Preparation')

route2 = Route([process4, process5])
production_order2 = ProductionOrder('Custom Pants', route2)

production_orders = [production_order1, production_order2]

# Check if all production orders comply with the constraint
result = check_production_order_constraints(production_orders)
print(result)  # Output: False, since production_order2 does not comply