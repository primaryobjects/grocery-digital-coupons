# Install dependencies.
import subprocess
subprocess.call(['python', 'setup.py'])

import sys
import os
import grocery_coupons
import argparse
from configparser import RawConfigParser

def onStatus(status):
    print(status['message'])
    if 'error' in status:
        print(status['error'])

if __name__ == "__main__":
    arparser = argparse.ArgumentParser(description='Grocery Digital Coupons.')
    arparser.add_argument('--config', type=str, default='shoprite', help='Config section to read login from.')
    arparser.add_argument('--store', type=str, default='shoprite', nargs='?', help='Store to clip coupons [shoprite, acme, stop_and_shop].')
    arparser.add_argument('--user', type=str, nargs='?', help='Login username or read from config.ini.')
    arparser.add_argument('--password', type=str, nargs='?', help='Login password or read from config.ini.')
    arparser.add_argument('--notify', type=str, default=None, nargs='?', help='Phone number to send a text message summary of results.')
    args = arparser.parse_args()

    parser = RawConfigParser()
    parser.read('config.ini')

    # Get email/password from config file
    email = os.getenv('email') or args.user or parser.get(args.config, 'email')
    password = os.getenv('password') or args.password or parser.get(args.config, 'password')
    phone = os.getenv('notify') or args.notify or parser.get(args.config, 'notify') if parser.has_option(args.config, 'notify') else None
    delay = 10

    if args.store == 'shoprite':
        grocery_coupons.shoprite(email, password, phone, delay, onStatus)
    elif args.store == 'stop_and_shop':
        grocery_coupons.stop_and_shop(email, password, phone, delay, onStatus)
    elif args.store == 'acme':
        grocery_coupons.acme(email, password, phone, delay, onStatus)
    elif args.store == 'help':
        print('Usage: client.py [shoprite | acme | stop_and_shop]')
    else:
        print('Unknown store: ' + args.store)
