# -*- coding: utf-8 -*-
import urllib
import urllib2
import random, string
from bs4 import BeautifulSoup
import shopify
import postmon
import settings


class addCouponError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def getCouponCode(length):
    return ''.join(random.choice(string.uppercase) for i in range(length))


def prepareCoupon(token, data):
    data.update({'authenticity_token': token})
    form_data = {
        'utf8': '✓',
        'discount[code]': getCouponCode(12),
        'discount[value]': '',
        'discount[applies_to_resource]': '',
        'usage_limit_type': 'no_limit',
        'discount[usage_limit]': '',
        'discount[applies_once_per_customer]': '0',
        'discount[starts_at]': '2016-05-03',
        'discount_never_expires': '',
    }
    if data['discount[minimum_order_amount]'] > 0:
        form_data.update(
            {'discount[applies_to_resource]': 'minimum_order_amount'})
    form_data.update({'authenticity_token': token})
    form_data.update(data)
    return form_data


def addDiscount(coupon):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)
    params = {'login': settings.ShopifyConfig.SHOPIFY_LOGIN,
              'password': settings.ShopifyConfig.SHOPIFY_PWD}
    encoded_params = urllib.urlencode(params)

    _file = opener.open(settings.ShopifyConfig.LOGIN_URL, encoded_params)
    response = _file.read()
    _file.close()

    soup = BeautifulSoup(response)
    auth_entry = soup.find('input', type='hidden',
                           attrs={'name': 'authenticity_token'})
    auth_token = auth_entry['value']
    post_headers = {
        'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
        'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; ' \
        'en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 ' \
        'Safari/534.7',
        'X-Prototype-Version': '1.7_rc2',
        'X-Requested-With': 'XMLHttpRequest',
    }

    headers = [(x, y) for x, y in post_headers.iteritems()]
    opener.addheaders = headers
    coupon = prepareCoupon(auth_token, coupon)
    encoded_post_data = urllib.urlencode(coupon)

    try:
        _file = opener.open(settings.ShopifyConfig.ADMIN_URL +
                            'discounts', encoded_post_data)
    except urllib2.HTTPError as e:
        raise addCouponError(e)

    response = _file.read()
    _file.close()
    return coupon


def publishCoupon(data):
    customers = getCustomers()
    coupon = addDiscount(data)
    msg = "Coupon Code: {0}, ${1} off.".format(coupon['discount[code]'],
                                               coupon['discount[value]'])
    sendNotification(customers, "Check it out", msg)


def getCustomers():
    shopify.ShopifyResource.set_site(settings.ShopifyConfig.API_URL)
    try:
        customers = shopify.Customer().find()
    except:
        return ['Shopify API error, please retry']
    selected_email = []
    for x in customers:
        if x.attributes['accepts_marketing']:
            selected_email.append(x.attributes['email'])
    return selected_email


def sendNotification(emails, subject, content):
    for e in emails:
        postmon.send(e, subject, content)


def getDiscounts():
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)
    params = {'login': settings.ShopifyConfig.SHOPIFY_LOGIN,
              'password': settings.ShopifyConfig.SHOPIFY_PWD}
    encoded_params = urllib.urlencode(params)

    _file = opener.open(settings.ShopifyConfig.LOGIN_URL, encoded_params)
    response = _file.read()
    _file.close()
    post_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,' \
        'image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_11_4; ' \
        'en-US) AppleWebKit/534.7 (KHTML, like Gecko) ' \
        'Chrome/7.0.517.41 Safari/534.7',
        'X-XHR-Referer': 'https://shunanl.myshopify.com/admin/discounts',
        'Referer': 'https://shunanl.myshopify.com/admin/discounts',
        'X-Prototype-Version': '1.7_rc2',
        'X-Requested-With': 'XMLHttpRequest'
    }

    headers = [(x, y) for x, y in post_headers.iteritems()]
    opener.addheaders = headers
    _file = opener.open(settings.ShopifyConfig.ADMIN_URL + 'discounts')
    response = _file.read()
    soup = BeautifulSoup(response)
    divs = soup.find_all('div', class_="discount")
    discounts = []
    for d in divs:
        discounts.append([d.find('span').string, d.find('p').string.strip()])
    return discounts


def addCustomer(customer):
    shopify.ShopifyResource.set_site(settings.ShopifyConfig.API_URL)
    new_customer = shopify.Customer()
    new_customer.email = customer['email']
    new_customer.first_name = customer['first_name']
    new_customer.last_name = customer['last_name']
    # By Default Always set new customer to accept market emails
    new_customer.accepts_marketing = True
    success = new_customer.save()
