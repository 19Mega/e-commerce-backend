import json

from datetime import datetime
from main import app, db
from models import User, Address, Payment , Product, Favorite, Cart, Order, OrderDetail, Advertising
from flask import request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_csrf_token, jwt_required, get_jwt_identity

bcrypt = Bcrypt()

# -----

# @app.route('/')
# def index():
#     return jsonify({"Choo Choo": f"Welcome to your Flask app"})

# @app.route('/create_table')
# def create_table():
#     db.create_all()
#     return "Tabla creada!"

# @app.route('/delete_table')
# def delete_table():
#     db.drop_all()
#     return "Tabla eliminada!"

# -----

# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# User : CREATE, READ, UPDATE, DELETE

@app.route('/signup', methods=['POST'])
def signup_user():
    body = json.loads(request.data)

    # user exist?
    user = User.query.filter_by(email=body["email"]).first()
    if user is None:  
        # hashing the password
        hashed_password = bcrypt.generate_password_hash(body["password"]).decode('utf-8')

        new_user = User(
            name = body["name"],
            email = body["email"],
            password = hashed_password,
            is_active = body["is_active"],
            is_admin = False,
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User created."}), 200
    
    return jsonify({"msg": "User already exists."}), 400

@app.route('/login', methods=['POST'])  
def login_user():
    body = json.loads(request.data)
    email = body["email"]
    password = body["password"]
    
    # user exist?
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password): #check hashed password
        return jsonify({'msg': 'Invalid username/password'}), 401

    access_token = create_access_token(identity= user.id)
    
    favorites = Favorite.query.filter(Favorite.user_id == user.id).all()      
    user_favorites = [favorite.serialize()['product_id'] for favorite in favorites]
        
    cart = Cart.query.filter(Cart.user_id == user.id).all()
    user_cart = [{"id": cart.product_id, "quantity": cart.quantity} for cart in cart]
    print(user_cart)
    print(access_token)

    if user.is_admin:
        return jsonify(access_token= access_token, 
                user_id= user.id,
                user_name = user.name,
                user_email = user.email,
                user_favorites = user_favorites,
                user_cart = user_cart,
                user_admin = user.is_admin 
                ), 200

    return jsonify(access_token= access_token, 
                    user_id= user.id,
                    user_name = user.name,
                    user_email = user.email,
                    user_favorites = user_favorites,
                    user_cart = user_cart   
                    ), 200

@app.route('/user/<int:user_id>/verify', methods=['GET'])
@jwt_required()
def veify_admin_token(user_id): 
    # verify user
    current_user_id = get_jwt_identity()
    if current_user_id == user_id:
        user = User.query.filter_by(id=user_id).first()
        if user.is_admin: 
            return jsonify(user_admin = user.is_admin), 200
    
    return jsonify({"msg": "Unauthorized."}), 401
   
# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 🏡 Address : CREATE, READ, UPDATE, DELETE

@app.route('/user/<int:user_id>/address', methods=['POST'])
@jwt_required()
def create_address(user_id):
    
    if user_id is None:
        return jsonify({"msg": "Invalid user id"}), 404

    # verify user
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"msg": "Unauthorized."}), 401 
    
    body = json.loads(request.data)
    
    new_address = Address(
        user_id = user_id,
        name_surname = body["name_surname"],
        phone = body["phone"],
        department = body["department"],
        city = body["city"],
        street = body["street"],
        street_number = body["street_number"],
        no_number = body["no_number"],
        references = body["references"]
    )
    db.session.add(new_address)
    db.session.commit()
    
    new_address_id = new_address.id
    
    return jsonify({"address_id": new_address_id}), 201

@app.route('/user/<int:user_id>/address', methods=['GET'])
@jwt_required()
def get_addresses(user_id):
    
    # verify user
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"msg": "Unauthorized."}), 401
    
    addresses = Address.query.filter_by(user_id= user_id).all()
    return jsonify([address.serialize() for address in addresses]), 200
  
@app.route('/user/<int:user_id>/address/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(user_id, address_id):
    
    # verify user
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"msg": "Unauthorized."}), 401
    
    # addres exist?
    user_address = Address.query.filter_by(user_id= user_id, id= address_id).first()
    if not user_address:
        return jsonify({"msg": "Address not found."}), 404
    
    body = json.loads(request.data)
    
    address = Address.query.get(address_id)
    address.user_id = user_id
    address.name_surname = body["name_surname"]
    address.phone = body["phone"]
    address.department = body["department"]
    address.city = body["city"]
    address.street = body["street"]
    address.street_number = body["street_number"]
    address.no_number = body["no_number"]
    address.references = body["references"]
    db.session.commit()
    
    return jsonify({"msg": "Address updated."}), 200

@app.route('/user/<int:user_id>/address/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(user_id, address_id):
    
    # verify user
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"msg": "Unauthorized."}), 401
    
    # addres exist?
    user_address = Address.query.filter_by(user_id= user_id, id= address_id).first()
    if not user_address:
        return jsonify({"msg": "Address not found."}), 404
    
    db.session.delete(user_address)
    db.session.commit()
    
    return jsonify({"msg": "Address deleted."}), 200

# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# ⭐ Favorite: CREATE, READ, DELETE
@app.route('/user/<int:user_id>/favorite/<int:product_id>', methods=['POST'])
@jwt_required()
def create_favorite(user_id, product_id):
    try:         
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
        
        # path is valid?
        if user_id is None or product_id is None:
            return jsonify({"msg": "Invalid request."}), 400
        
        # product exist?
        if not Product.query.filter_by(id= product_id).first():
            return jsonify({"msg": "Product not found."}), 404

        # favorite exist?
        if not Favorite.query.filter_by(user_id= user_id, product_id= product_id).first():
            new_favorite = Favorite(
                user_id = user_id,
                product_id = product_id
            )
            db.session.add(new_favorite)
            db.session.commit()
            
            favorites = Favorite.query.filter_by(user_id=user_id).all()
            
            return jsonify([favorite.serialize() for favorite in favorites]), 200

        return jsonify({"msg": "Favorite already exists."}), 400

    except Exception as e:
        return jsonify({"msg": f"Error creating favorite: {str(e)}"}), 500

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
@jwt_required()
def read_user_favorites(user_id):
    try:
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
        
        favorites = Favorite.query.filter_by(user_id= user_id).all()
        if favorites:
            return jsonify([favorite.serialize() for favorite in favorites]), 200
        else:
            return jsonify({"msg": "User has no favorites."}), 404
        
    except Exception as e:
        return jsonify({"msg": f"Error creating favorite: {str(e)}"}), 500

@app.route('/user/<int:user_id>/favorite/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite(user_id, product_id):
    try:
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
        
        # path is valid?
        if user_id is None or product_id is None:
            return jsonify({"msg": "Invalid request."}), 400
        
        # favorite exist?
        favorite = Favorite.query.filter_by(user_id= user_id, product_id= product_id).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            
            favorites = Favorite.query.filter_by(user_id= user_id).all()
            return jsonify([favorite.serialize() for favorite in favorites]), 200
        
            #return jsonify({"msg": "Favorite deleted."}), 200   
        else:
            return jsonify({"msg": "Favorite not found."}), 404
        
    except Exception as e:
        return jsonify({"msg": f"Error deleting favorite: {str(e)}"}), 500

# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 🛒 Cart: 

@app.route('/user/<int:user_id>/cart/product/<int:product_id>/add', methods=['POST'])
@jwt_required()
def add_cart_item(user_id, product_id):
    try:
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401

        # path is valid?
        if user_id is None or product_id is None:
            return jsonify({"msg": "Invalid request."}), 400
        
        # product exist?
        if not Product.query.filter_by(id= product_id).first():
            return jsonify({"msg": "Product not found."}), 404

        # cart item exist?
        product_in_cart = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        
        if not product_in_cart:
            new_cart_item = Cart(
                user_id=user_id,
                product_id=product_id,
            )
            db.session.add(new_cart_item)
            db.session.commit()
            return jsonify({"msg": "Cart item added."}), 200
        
    except Exception as e:
        return jsonify({"msg": f"Error adding cart item: {str(e)}"}), 500

@app.route('/user/<int:user_id>/cart', methods=['GET'])
@jwt_required()
def read_cart(user_id):
    # TODO check stock
    cart_items = Cart.query.filter_by(user_id= user_id).all()
    if cart_items:
        return jsonify([cart_item.serialize() for cart_item in cart_items]), 200
    else:
        return jsonify({"msg": "Cart is empty."}), 404
    
@app.route('/user/<int:user_id>/cart/product/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_cart_item(user_id, product_id):
    try:
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
        
        # path is valid?
        if user_id is None or product_id is None:
            return jsonify({"msg": "Invalid request."}), 400
        
        # cart item exist?
        cart_item = Cart.query.filter_by(user_id= user_id, product_id= product_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            return jsonify({"msg": "Cart item deleted."}), 200
        else:
            return jsonify({"msg": "Cart item not found."}), 404
        
    except Exception as e:
        return jsonify({"msg": f"Error deleting cart item: {str(e)}"}), 500


# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 📦 Product: CREATE, READ, UPDATE, DELETE

@app.route('/product', methods=['POST'])
def create_product():
    try:
        body = json.loads(request.data)

        required_fields = ['short_description', 'price', 'stock', 'category', 'image_1']
        for field in required_fields:
            if field not in body or not body[field]:
                return jsonify({"msg": f"Field '{field}' is missing or empty."}), 400
            
        new_product = Product(
            short_description = body['short_description'],
            long_description = body['long_description'],
            category = body['category'],
            subcategory = body['subcategory'],
            
            price = body['price'],
            discount = body['discount'],
            stock = body['stock'],
            
            characteristic_1_title = body['characteristic_1_title'],
            characteristic_2_title = body['characteristic_2_title'],
            characteristic_3_title = body['characteristic_3_title'],
            characteristic_4_title = body['characteristic_4_title'],
            
            characteristic_1_description = body['characteristic_1_description'],
            characteristic_2_description = body['characteristic_2_description'],
            characteristic_3_description = body['characteristic_3_description'],
            characteristic_4_description = body['characteristic_4_description'],
            
            image_1 = body['image_1'],
            image_2 = body['image_2'],
            image_3 = body['image_3'],
            image_4 = body['image_4'],       
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"msg": "Product created."}), 200

    except Exception as e:
        return jsonify({"msg": f"Error creating product: {str(e)}"}), 500
    
@app.route('/product/<int:product_id>', methods=['GET'])
def read_one_product(product_id):
    product = Product.query.filter_by(id = product_id).first()
    if product:
        return jsonify(product.serialize_full()), 200
    else:
        return jsonify({"msg": "No products found."}), 404
    
@app.route('/product', methods=['GET'])
def read_products():
    products = Product.query.all()
    if products:
        return jsonify([product.serialize_basic() for product in products]), 200
    else:
        return jsonify({"msg": "No products found."}), 404
    
@app.route('/product/<string:category>', methods=['GET'])
def read_products_by_category(category):
    products = Product.query.filter_by(category=category).all()
    if products:
        return jsonify([product.serialize_basic() for product in products]), 200
    else:
        return jsonify({"msg": "No products found."}), 404
    
@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        body = json.loads(request.data)

        required_fields = ['short_description', 'price', 'stock', 'category', 'image_1']
        for field in required_fields:
            if field not in body or not body[field]:
                return jsonify({"msg": f"Field '{field}' is missing or empty."}), 400
        
        product = Product.query.get(product_id)
        if product:
            product.short_description = body['short_description']
            product.long_description = body['long_description']
            product.category = body['category']
            product.subcategory = body['subcategory']

            product.price = body['price']
            product.discount = body['discount']
            product.stock = body['stock']

            product.characteristic_1_title = body['characteristic_1_title']
            product.characteristic_2_title = body['characteristic_2_title']
            product.characteristic_3_title = body['characteristic_3_title']
            product.characteristic_4_title = body['characteristic_4_title']

            product.characteristic_1_description = body['characteristic_1_description']
            product.characteristic_2_description = body['characteristic_2_description']
            product.characteristic_3_description = body['characteristic_3_description']
            product.characteristic_4_description = body['characteristic_4_description']

            product.image_1 = body['image_1']
            product.image_2 = body['image_2']
            product.image_3 = body['image_3']
            product.image_4 = body['image_4']
            
            db.session.commit()
            return jsonify({"msg": "Product updated."}), 200
        
    except Exception as e:
        return jsonify({"msg": f"Error updating product: {str(e)}"}), 500
    
@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({"msg": "Product deleted."}), 200
        
    except Exception as e:
        return jsonify({"msg": f"Error deleting product: {str(e)}"}), 500
    
# FILTERING PRODUCTS
@app.route('/product/filter', methods=['GET'])
def filter_products():
    try:
        # get query parameters
        price = request.args.get('price')
        
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        
        category = request.args.get('category')
        subcategory = request.args.get('subcategory')
        discount = request.args.get('discount')

        filtered_products = Product.query
        if price:
            filtered_products = filtered_products.filter(Product.price <= price)          
        if min_price:
            filtered_products = filtered_products.filter(Product.price >= min_price)
        if max_price:
            filtered_products = filtered_products.filter(Product.price <= max_price)        
        if discount:
            filtered_products = filtered_products.filter(Product.discount <= discount, Product.discount != 0)
        if category:
            filtered_products = filtered_products.filter_by(category=category)
        if subcategory:
            filtered_products = filtered_products.filter_by(subcategory=subcategory)
        
        
        # execute the query and get results
        # filtered_products = filtered_products.all()

        # return filtered products
        if filtered_products:
            return jsonify([{"favorite": False, **product.serialize_basic()} for product in filtered_products]), 200
        else:
            return jsonify({"msg": "No products found based on the provided filter."}), 404

    except Exception as e:
        return jsonify({"msg": f"Error searching products: {str(e)}"}), 500

@app.route('/product/cart', methods=['POST'])
def get_cart_products():
    try:
        body = json.loads(request.data)
        if not body:
            return jsonify({"msg": "Invalid request body."}), 400
        
        cart_list = []
        
        for item_id in body:
            product = Product.query.filter_by(id=item_id).first()
            if product:
                cart_list.append(product.serialize_cart_item())
        
        if cart_list:
            return jsonify(cart_list), 200
        
    except Exception as e:
        return jsonify({"msg": f"Error creating product: {str(e)}"}), 500

# PRODUCT SEARCH 
@app.route('/product/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    search = f"%{query}%"
    products = Product.query.filter(
        db.or_(
            Product.short_description.ilike(search),
            Product.long_description.ilike(search),
            Product.category.ilike(search),
            Product.subcategory.ilike(search),
            Product.characteristic_1_title.ilike(search),
            Product.characteristic_2_title.ilike(search),
            Product.characteristic_3_title.ilike(search),
            Product.characteristic_4_title.ilike(search),
            Product.characteristic_1_description.ilike(search),
            Product.characteristic_2_description.ilike(search),
            Product.characteristic_3_description.ilike(search),
            Product.characteristic_4_description.ilike(search),
        )
    ).all()

    return jsonify([product.serialize_basic() for product in products])

# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 📄 OrderDetail: CREATE, READ, UPDATE, DELETE

@app.route('/user/<int:user_id>/order-detail', methods=['POST'])
@jwt_required()
def create_order_detail(user_id):
    try:
        body = json.loads(request.data)
        
        # para cada item del carrito, crear un nuevo order detail
        
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401

        # JSON is valid?
        if "order_id" not in body or "product_id" not in body or "product_quantity" not in body:
            return jsonify({"msg": "Invalid request body."}), 400
        
        new_order_detail = OrderDetail(
            order_id= body["order_id"],
            product_id= body["product_id"],
            user_id= body["user_id"],
            
            product_name= body["product_name"],
            product_price= body["product_price"],
            product_quantity= body["product_quantity"],
            product_category= body["product_category"],
            product_subcategory= body["product_subcategory"],
            
            product_offer= body["product_offer"],
            
            product_brand= body["product_brand"],
            product_model= body["product_model"],
            product_color= body["product_color"],
            product_size= body["product_size"],
            product_weight= body["product_weight"],
            
            product_guarantee= body["product_guarantee"],
            product_guarantee_description= body["product_guarantee_description"],
            
            subtotal= body["subtotal"],

        )
        db.session.add(new_order_detail)
        db.session.commit()
        return jsonify({"msg": "Order detail created."}), 200

    except Exception as e:
        return jsonify({"msg": f"Error creating order detail: {str(e)}"}), 500

@app.route('/user/<int:user_id>/order-detail/<int:order_detail_id>', methods=['GET'])
@jwt_required()
def read_one_order_detail(user_id, order_detail_id):
    try:
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
        
        order_detail = OrderDetail.query.filter_by(id = order_detail_id).first()
        if order_detail:
            return jsonify(order_detail.serialize()), 200
        else:
            return jsonify({"msg": "No order details found."}), 404
            
    except Exception as e:
        return jsonify({"msg": f"Error deleting order: {str(e)}"}), 500
    
@app.route('/user/<int:user_id>/order-detail', methods=['GET'])
@jwt_required()
def read_order_details(user_id):
    try:
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
            
        order_details = OrderDetail.query.all()
        if order_details:
            return jsonify([order_detail.serialize() for order_detail in order_details]), 200
        else:
            return jsonify({"msg": "No order details found."}), 404
            
    except Exception as e:
        return jsonify({"msg": f"Error deleting order: {str(e)}"}), 500
    
@app.route('/user/<int:user_id>/order-detail/<int:order_detail_id>', methods=['DELETE'])
@jwt_required()
def delete_order_detail(user_id, order_detail_id):
    try:     
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
        
        order_detail = OrderDetail.query.get(order_detail_id)
        if order_detail:
            db.session.delete(order_detail)
            db.session.commit()
            return jsonify({"msg": "Order detail deleted."}), 200
        
    except Exception as e:
        return jsonify({"msg": f"Error deleting order detail: {str(e)}"}), 500
    

# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 🚚 Order: CREATE, READ, DELETE

@app.route('/user/<int:user_id>/order/add', methods=['POST'])
@jwt_required()
def create_order(user_id):
    try:
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
        
        # path is valid?
        if user_id is None:
            return jsonify({"msg": "Invalid request."}), 400
        
                
        new_order = Order(
            user_id= current_user_id,
            taxes = 0,
            total = 0,
            date = datetime.now(),
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({"msg": "Order created."}), 200

    except Exception as e:
        return jsonify({"msg": f"Error creating order: {str(e)}"}), 500
    
@app.route('/user/<int:user_id>/order/<int:order_id>', methods=['GET'])
@jwt_required()
def read_one_order(user_id, order_id):
    
    try:
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
        
        # path is valid?
        if user_id is None or order_id is None:
            return jsonify({"msg": "Invalid request."}), 400
        
        order = Order.query.filter_by(id = order_id).first()
        
        if order:
            return jsonify(order.serialize()), 200
        else:
            return jsonify({"msg": "No orders found."}), 404
        
    except Exception as e:
        return jsonify({"msg": f"Error deleting order: {str(e)}"}), 500
    
@app.route('/user/<int:user_id>/order/', methods=['GET'])
@jwt_required()
def read_orders(user_id):
    try:
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
        
        # path is valid?
        if user_id is None:
            return jsonify({"msg": "Invalid request."}), 400
        
        orders = Order.query.all()
        if orders:
            return jsonify([order.serialize() for order in orders]), 200
        else:
            return jsonify({"msg": "No orders found."}), 404
    
    except Exception as e:
        return jsonify({"msg": f"Error deleting order: {str(e)}"}), 500
    
@app.route('/user/<int:user_id>/order/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(user_id ,order_id):
    try:   
        # verify user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"msg": "Unauthorized."}), 401
        
        # path is valid?
        if user_id is None:
            return jsonify({"msg": "Invalid request."}), 400
              
        order = Order.query.get(order_id)
        if order:
            db.session.delete(order)
            db.session.commit()
            return jsonify({"msg": "Order deleted."}), 200
        
    except Exception as e:
        return jsonify({"msg": f"Error deleting order: {str(e)}"}), 500
    
    
# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# Advertising
@app.route('/admin/<int:user_id>/banner/add', methods=['POST'])
@jwt_required()
def create_advertising(user_id):
    try:
        body = json.loads(request.data)

        # verify admin user
        current_user_id = get_jwt_identity()
        if current_user_id == user_id:
            user = User.query.filter_by(id=user_id).first()

        if user.is_admin: 
            new_advertising = Advertising(
            image_url = body["image_url"],
            product_id = body["product_id"],
            category = body["category"],
            )

            db.session.add(new_advertising)
            db.session.commit()   
            return jsonify({"msg": "Order created."}), 200

    except Exception as e:
        return jsonify({"msg": f"Error creating order: {str(e)}"}), 500
    



    

