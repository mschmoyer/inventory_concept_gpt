# seed.py
from app import app, db, Product

def seed_products():
    with app.app_context():
        products = [
            {'sku': 'STICKER001', 'name': 'Smiley Face Sticker'},
            {'sku': 'STICKER002', 'name': 'Rainbow Sticker'},
            {'sku': 'STICKER003', 'name': 'Unicorn Sticker'},
            {'sku': 'STICKER004', 'name': 'Space Rocket Sticker'},
            {'sku': 'STICKER005', 'name': 'Pineapple Sticker'},
            {'sku': 'STICKER006', 'name': 'Flamingo Sticker'},
            {'sku': 'STICKER007', 'name': 'Cactus Sticker'},
            {'sku': 'STICKER008', 'name': 'Pizza Slice Sticker'},
            {'sku': 'STICKER009', 'name': 'Ice Cream Sticker'},
            {'sku': 'STICKER010', 'name': 'Sunglasses Sticker'},
            {'sku': 'STICKER011', 'name': 'Mountain Sticker'},
            {'sku': 'STICKER012', 'name': 'Beach Ball Sticker'},
            {'sku': 'STICKER013', 'name': 'Donut Sticker'},
            {'sku': 'STICKER014', 'name': 'Cat Sticker'},
            {'sku': 'STICKER015', 'name': 'Dog Sticker'},
            {'sku': 'STICKER016', 'name': 'Robot Sticker'},
            {'sku': 'STICKER017', 'name': 'Alien Sticker'},
            {'sku': 'STICKER018', 'name': 'Lightning Bolt Sticker'},
            {'sku': 'STICKER019', 'name': 'Heart Sticker'},
            {'sku': 'STICKER020', 'name': 'Star Sticker'},
        ]
        for prod in products:
            product = Product(sku=prod['sku'], name=prod['name'])
            db.session.add(product)
        db.session.commit()
        print("Database seeded with products.")

if __name__ == '__main__':
    seed_products()
