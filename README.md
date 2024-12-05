# Shorite Digital Coupon Clipper Automation

Automatically clip digital coupons from Shoprite and food store web sites.

## Quick Start

1. Install the required software for [Python](https://www.python.org/downloads/) *(version 3.8.3)*.
2. Download the [pip](https://bootstrap.pypa.io/get-pip.py) script and install it with `python get-pip.py`
3. Edit `config.ini` to include your login information.
4. Run the script with `python client.py shoprite`

- *If on Linux, set the permissions of `chromedriver` to executable.*
- *In Windows 10, use an Administrator Command Prompt to run scripts. First run `python3 setup.py`*

## Usage

The following steps may be used to run the program.

1. `python3 client.py`
2. `python3 client.py --store shoprite --user username --password password`

The full command-line arguments are shown below.

```text
usage: client.py [-h] [--config CONFIG] [--store [STORE]] [--user [USER]]
                 [--password [PASSWORD]]

Grocery Digital Coupons.

optional arguments:
  --help                  Show this help message and exit
  --config CONFIG         Config section to read login from.
  --store [STORE]         Store to clip coupons [shoprite, acme, stop_and_shop].
  --user [USER]           Login username or read from config.ini.
  --password [PASSWORD]   Login password or read from config.ini.
  --notify [000-000-0000] Phone number to send a text message summary of results.
```

## Dependencies
[Selenium](http://selenium-python.readthedocs.io/index.html)
[Chrome Driver](https://sites.google.com/a/chromium.org/chromedriver/downloads)

**Helpful Commands**

```bash
C:\Users\YOUR_USER_NAME\AppData\Local\Programs\Python\Python38-32\python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip
C:\Users\YOUR_USER_NAME\AppData\Local\Programs\Python\Python38-32\python client.py
alias coupons="cd ~/Documents/grocery-digital-coupons && python3 client.py --store shoprite --config shoprite1 && python3 client.py --store shoprite --config shoprite2"
```

## More Info

### What are grocery digital coupons?

Grocery stores - [ShopRite](http://www.shoprite.com), [ACME](https://www.acmemarkets.com), and [Stop and Shop](http://www.stopandshop.com/) - have a "digital coupon" feature, by which you can log onto their website and add "digital" coupons to your store loyalty card. If you buy a product and the corresponding digital coupon is added to your loyalty card, you'll save some money upon checkout.

### So what's the problem?

The problem is that the digital coupons have to be added manually. If you buy something and the coupon isn't present on your loyalty card at the time of checkout, you won't get the discount.

### What's the solution?

The script adds *all* digital coupons to your card each week. Then, you'll automatically get the discount when you buy a product without having to do any legwork.

### So how does the script work?

The script uses [Selenium](http://selenium-python.readthedocs.io/index.html) to launch the grocery store's website, login with your loyalty card information, and automatically add each available coupon to your card.

### Where is my login information saved?

The program may be executed from the command-line or by using a config file [config.ini](config.ini). See also "Usage".

## What's next?

*Also available as a [web app](https://github.com/primaryobjects/grocery-digital-coupons/tree/web).*

## License

MIT

## Author

Kory Becker http://www.primaryobjects.com

Based on original from Sheil Naik [on Twitter](http://www.twitter.com/sheilnaik).
