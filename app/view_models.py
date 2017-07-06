class CartItem(object):
    def __init__(self, name=None, price=None, quantity=None, total=None, 
            product_id=None, main_image=None):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.total = total
        self.id = product_id
        self.main_image = main_image
