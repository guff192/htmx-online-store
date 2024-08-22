import urllib.parse

from schema.cart_schema import CartInCookie, CookieCartProduct
from schema.order_schema import OrderInCookie


def get_cart_from_cookies(cookies: dict[str, str]) -> CartInCookie:
    cookie_cart_str = cookies.get('_cart')
    if not cookie_cart_str:
        cookie_cart = CartInCookie(product_list=[])
    else:
        cookie_cart = CartInCookie.model_validate_json(cookie_cart_str)

    return cookie_cart


def add_product_to_cookie_cart(
    cookie_cart: CartInCookie, product_id: int, configuration_id: int
) -> CartInCookie:
    '''
        Adds product to cart. If product already in cart, increases count.
    '''
    products = cookie_cart.product_list
    try:
        found_product = list(filter(
            lambda p: p.product_id == product_id and p.configuration_id == configuration_id,
            products
        ))[0]
        found_product.count += 1
        
        return cookie_cart
    except IndexError:
        new_product = CookieCartProduct(
            product_id=product_id, configuration_id=configuration_id,
            count=1,
        )
        products.append(new_product)

    return cookie_cart


def remove_product_from_cookie_cart(
    cookie_cart: CartInCookie, product_id: int, configuration_id: int
) -> CartInCookie:
    '''
        Removes product from cart. Removed product always stays in cart
    '''
    products = cookie_cart.product_list
    try:
        product = list(filter(lambda p: p.product_id == product_id and p.configuration_id == configuration_id,
                              products))[0]
        product.count -= 1
    except IndexError:
        cookie_cart.product_list.append(
            CookieCartProduct(
                product_id=product_id, configuration_id=configuration_id, 
                count=0
            )
        )

    return cookie_cart


def get_order_from_cookies(cookies: dict[str, str]) -> OrderInCookie | None:
    cookie_order_str = cookies.get('_order')
    if not cookie_order_str:
        return None
    else:
        cookie_order_str = urllib.parse.unquote(cookie_order_str)
        return OrderInCookie.model_validate_json(cookie_order_str)

