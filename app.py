# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, methods=['GET', 'POST', 'PUT', 'DELETE'])

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure Flask-Mail (Replace with your SMTP server details)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587  # Replace with your SMTP port
app.config['MAIL_USERNAME'] = 'mikeschmoyer@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'nbto bdzs ubmj umht'  # Replace with your email password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'mikeschmoyer@gmail.com'  # Replace with your email

mail = Mail(app)

# Database Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer, default=10)
    reorder_quantity = db.Column(db.Integer, default=50)

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    approval_status = db.Column(db.String(50), default='Pending Approval')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.DateTime, nullable=True)
    items = db.relationship(
        'PurchaseOrderItem',
        backref='purchase_order',
        lazy=True,
        cascade='all, delete-orphan'  # This ensures associated items are deleted
    )

class PurchaseOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

# API Endpoints

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    products = Product.query.all()
    inventory = {}
    for product in products:
        inventory[product.sku] = {
            'name': product.name,
            'quantity': product.quantity
        }
    return jsonify(inventory)

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = [{'sku': product.sku, 'name': product.name} for product in products]
    return jsonify(product_list)

@app.route('/api/purchase_orders', methods=['GET'])
def get_purchase_orders():
    orders = PurchaseOrder.query.all()
    purchase_orders = []
    for order in orders:
        supplier = db.session.get(Supplier, order.supplier_id)
        items = [{
            'sku': db.session.get(Product, item.product_id).sku,
            'quantity': item.quantity
        } for item in order.items]
        purchase_orders.append({
            'order_id': order.id,
            'supplier_name': supplier.name,
            'status': order.status,
            'items': items,
            'order_date': order.order_date.strftime('%Y-%m-%d'),
            'expected_delivery_date': order.expected_delivery_date.strftime('%Y-%m-%d') if order.expected_delivery_date else None
        })
    return jsonify(purchase_orders)

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    suppliers = Supplier.query.all()
    supplier_list = []
    for supplier in suppliers:
        supplier_list.append({
            'id': supplier.id,
            'name': supplier.name,
            'email': supplier.email,
            'address': supplier.address,
            'phone': supplier.phone
            # Include any additional fields
        })
    return jsonify(supplier_list)

@app.route('/api/purchase_order', methods=['POST'])
def create_purchase_order():
    data = request.json
    #supplier_name = data['supplier_name']
    #supplier_email = data['supplier_email']
    supplier_id = data['supplier_id']
    items = data['items']
    expected_delivery_date = data.get('expected_delivery_date')
    if expected_delivery_date:
        expected_delivery_date = datetime.strptime(expected_delivery_date, '%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        expected_delivery_date = None

    # Get the supplier
    supplier = db.session.get(Supplier, supplier_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found'}), 404

    # Create purchase order
    purchase_order = PurchaseOrder(
        supplier_id=supplier.id,
        expected_delivery_date=expected_delivery_date
    )
    db.session.add(purchase_order)
    db.session.commit()

    # Add items to purchase order
    for item in items:
        sku = item['sku']
        quantity = int(item['quantity'])
        product = Product.query.filter_by(sku=sku).first()
        if not product:
            product = Product(sku=sku, name=f'New Product {sku}')
            db.session.add(product)
            db.session.commit()
        po_item = PurchaseOrderItem(
            purchase_order_id=purchase_order.id,
            product_id=product.id,
            quantity=quantity
        )
        db.session.add(po_item)
    db.session.commit()

    return jsonify({'status': 'success', 'order_id': purchase_order.id}), 201

@app.route('/api/suppliers', methods=['POST'])
def create_supplier():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    address = data.get('address')
    phone = data.get('phone')
    # Add any additional fields

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    # Check if supplier with same email already exists
    existing_supplier = Supplier.query.filter_by(email=email).first()
    if existing_supplier:
        return jsonify({'error': 'Supplier with this email already exists'}), 400

    supplier = Supplier(
        name=name,
        email=email,
        address=address,
        phone=phone
        # Add any additional fields
    )
    db.session.add(supplier)
    db.session.commit()

    return jsonify({'message': 'Supplier created successfully'}), 201


@app.route('/api/purchase_orders/<int:order_id>/approve', methods=['POST'])
def approve_purchase_order(order_id):
    purchase_order = db.session.get(PurchaseOrder, order_id)
    if not purchase_order:
        print(f"Purchase order not found: {order_id}")  # Debug line
        return jsonify({'error': 'Purchase order not found'}), 404
    if purchase_order.status == 'Approved':
        print(f"Purchase order already approved: {order_id}")  # Debug line
        return jsonify({'message': 'Purchase order already approved'}), 200
    purchase_order.status = 'Approved'
    print(f"Approval status before commit: {purchase_order.status}")  # Debug line
    db.session.commit()

    purchaser_email = 'mikeschmoyer@gmail.com'  # Replace with actual email
    send_notification_email(
        subject=f'Purchase Order #{order_id} Approved',
        recipient=purchaser_email,
        body=f'Purchase Order #{order_id} has been approved.'
    )

    return jsonify({'message': 'Purchase order approved'}), 200


@app.route('/api/receive_order/<int:order_id>', methods=['POST'])
def receive_order(order_id):
    order = db.session.get(PurchaseOrder, order_id)
    if order and order.status == 'Pending':
        for item in order.items:
            product = db.session.get(Product, item.product_id)
            product.quantity += item.quantity
        order.status = 'Received'
        db.session.commit()
        return jsonify({'status': 'Order received', 'order_id': order.id}), 200
    return jsonify({'status': 'Order not found or already received'}), 404

def generate_pdf(purchase_order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    p.setTitle(f"Purchase Order #{purchase_order.id}")

    # Company Information
    company_name = "Your Company Name"
    company_address = "123 Main Street\nCity, State, ZIP\nPhone: (555) 123-4567\nEmail: info@yourcompany.com"

    # Supplier Information
    supplier = db.session.get(Supplier, purchase_order.supplier_id)
    supplier_info = f"{supplier.name}\n{supplier.email}"

    # Draw Company Information
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, company_name)
    p.setFont("Helvetica", 10)
    text_object = p.beginText(50, height - 65)
    for line in company_address.split('\n'):
        text_object.textLine(line)
    p.drawText(text_object)

    # Draw Purchase Order Title
    p.setFont("Helvetica-Bold", 14)
    p.drawString(400, height - 50, f"Purchase Order")
    p.setFont("Helvetica", 12)
    p.drawString(400, height - 65, f"Order #: {purchase_order.id}")
    p.drawString(400, height - 80, f"Status: {purchase_order.status}")
    p.drawString(400, height - 95, f"Order Date: {purchase_order.order_date.strftime('%Y-%m-%d')}")
    if purchase_order.expected_delivery_date:
        p.drawString(400, height - 110, f"Expected Delivery: {purchase_order.expected_delivery_date.strftime('%Y-%m-%d')}")

    # Draw Supplier Information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 130, "Supplier:")
    p.setFont("Helvetica", 12)
    text_object = p.beginText(50, height - 145)
    for line in supplier_info.split('\n'):
        text_object.textLine(line)
    p.drawText(text_object)

    # Draw Table Headers
    p.setFont("Helvetica-Bold", 12)
    y = height - 180
    p.drawString(50, y, "SKU")
    p.drawString(150, y, "Product Name")
    p.drawString(400, y, "Quantity")

    # Draw Line Items
    y -= 20
    p.setFont("Helvetica", 12)
    for item in purchase_order.items:
        product = db.session.get(Product, item.product_id)
        p.drawString(50, y, product.sku)
        p.drawString(150, y, product.name)
        p.drawString(400, y, str(item.quantity))
        y -= 20
        if y < 50:
            p.showPage()
            y = height - 50

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def send_email_with_pdf(purchase_order, pdf_buffer):
    try:
        supplier = db.session.get(Supplier, purchase_order.supplier_id)
        msg = Message(
            subject=f"Purchase Order #{purchase_order.id}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[supplier.email]
        )
        msg.body = f"Dear {supplier.name},\n\nPlease find attached the purchase order."
        # Attach PDF
        msg.attach(
            f"PurchaseOrder_{purchase_order.id}.pdf",
            "application/pdf",
            pdf_buffer.getvalue()
        )
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_inventory_levels():
    products = Product.query.all()
    for product in products:
        if product.quantity <= product.reorder_point:
            # Create a purchase order for this product
            supplier = get_default_supplier_for_product(product)  # Implement this function
            purchase_order = PurchaseOrder(
                supplier_id=supplier.id
            )
            db.session.add(purchase_order)
            db.session.commit()

            po_item = PurchaseOrderItem(
                purchase_order_id=purchase_order.id,
                product_id=product.id,
                quantity=product.reorder_quantity
            )
            db.session.add(po_item)
            db.session.commit()

@app.route('/api/purchase_orders/<int:order_id>/update_status', methods=['POST'])
def update_purchase_order_status(order_id):
    data = request.json
    new_status = data.get('status')
    purchase_order = db.session.get(PurchaseOrder, order_id)
    if not purchase_order:
        return jsonify({'error': 'Purchase order not found'}), 404

    valid_transitions = {
        'Draft': ['Pending Approval', 'Cancelled'],
        'Pending Approval': ['Approved', 'Cancelled'],
        'Approved': ['Ordered', 'Cancelled'],
        'Ordered': ['Shipped', 'Cancelled'],
        'Shipped': ['Received', 'Cancelled'],
        'Received': ['Completed'],
        'Completed': [],
        'Cancelled': []
    }

    if new_status not in valid_transitions.get(purchase_order.status, []):
        return jsonify({'error': f'Invalid status transition from {purchase_order.status} to {new_status}'}), 400

    purchase_order.status = new_status
    db.session.commit()

    # if status moved to Ordered, then generate PDF and send email
    if new_status == 'Ordered':
        # Generate PDF
        pdf_buffer = generate_pdf(purchase_order)

        # Send Email with PDF
        send_email_with_pdf(purchase_order, pdf_buffer)

    return jsonify({'message': f'Purchase order status updated to {new_status}'}), 200

def send_notification_email(subject, recipient, body):
    msg = Message(subject=subject, recipients=[recipient], body=body)
    mail.send(msg)

@app.route('/api/purchase_orders/<int:order_id>', methods=['DELETE'])
def delete_purchase_order(order_id):
    purchase_order = db.session.get(PurchaseOrder, order_id)
    if not purchase_order:
        return jsonify({'error': 'Purchase order not found'}), 404

    try:
        db.session.delete(purchase_order)
        db.session.commit()
        return jsonify({'message': 'Purchase order deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
