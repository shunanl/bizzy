import os

# Shopify Credentials
class ShopifyConfig():
	API_KEY = ""
	API_PWD = ""
	API_SECRET = ""
	API_URL = "https://%s:%s@shunanl.myshopify.com/admin" % (API_KEY, API_PWD)
	SHOPIFY_LOGIN = ""
	SHOPIFY_PWD = ""
	ADMIN_URL = 'https://shunanl.myshopify.com/admin/'
	LOGIN_URL = ADMIN_URL + 'auth/login'

# Email Service Credentials
class MainConfig():
	MAIL_USER = ""
	MAIL_PWD = ""
