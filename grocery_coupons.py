import os
import time
from pytextbelt import Textbelt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException

browser = None

def initialize():
    global browser

    path = os.getenv('GOOGLE_CHROME_SHIM') or None

    options = webdriver.ChromeOptions()
    options.binary_location = path
    #options.add_experimental_option('w3c', False)
    #if path:
    #    options.add_argument('headless')

    executable_path = 'chromedriver' if 'DYNO' in os.environ else './chromedriver'
    browser = webdriver.Chrome(executable_path=executable_path, options = options)

    print('Using ' + (path or executable_path))

def test(email, password, delay = 10, callback = None):
    result = { 'email': email, 'existingCount': 0, 'count': 0, 'message': None, 'screenshot': None }

    if callback:
        callback(result)

    return result

def shoprite(email, password, phone = None, delay = 10, callback = None):
    result = { 'email': email, 'existingCount': 0, 'count': 0, 'message': None, 'screenshot': None }

    initialize()

    if callback:
        result['message'] = 'Navigating to home page.'
        callback(result)

    try:
        browser.get('https://coupons.shoprite.com')

        if callback:
            result['message'] = 'Locating sign-in page.'
            callback(result)

        for i in range(3):
            try:
                # Wait for page load.
                WebDriverWait(browser, delay).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.login-to-load'))
                )
                break
            except Exception as e:
                result['message'] = 'Unable to load sign-in page, reloading page. Attempt ' + str(i+1) + '/3.'
                result['screenshot'] = browser.get_screenshot_as_base64()
                callback(result)
                browser.refresh()

        browser.find_elements_by_css_selector('a.login-to-load')[0].click()

        if callback:
            result['message'] = 'Waiting for login page.'
            result['screenshot'] = browser.get_screenshot_as_base64()
            callback(result)

        # Login
        time.sleep(2)
        WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.ID, "Email"))
        )

        if callback:
            result['message'] = 'Entering login details.'
            callback(result)

        # Send login info.
        browser.find_element_by_id('Email').send_keys(email)
        browser.find_element_by_id('Password').send_keys(password)
        browser.find_element_by_id('Password').send_keys(Keys.RETURN)

        if callback:
            result['message'] = 'Signing in.'
            result['screenshot'] = browser.get_screenshot_as_base64()
            callback(result)

        # Wait until the site loads, find the welcome page or error message.
        WebDriverWait(browser, delay).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.coupon-savings-count, .field-validation-error, .validation-summary-errors'))
        )

        if callback:
            result['message'] = 'Checking if login succeeded.'
            callback(result)

        # Check if the login succeeded.
        fields = browser.find_elements_by_xpath("//*[contains(text(), 'incorrect') or contains(text(), 'try again')]")
        if len(fields) > 0:
            # Invalid login?
            result['message'] = 'Error'
            result['error'] = 'Invalid login.'
            result['screenshot'] = browser.get_screenshot_as_base64()
            callback(result)
            count = -1
        else:
            if callback:
                result['message'] = 'Navigating to coupons.'
                callback(result)

            WebDriverWait(browser, delay).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.coupon-item-container'))
            )

            if callback:
                result['message'] = 'Loading coupons.'
                result['screenshot'] = browser.get_screenshot_as_base64()
                callback(result)

            WebDriverWait(browser, delay).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "coupon-item"))
            )

            # Read all coupons on the current page, then process all subsequent pages by clicking Next, until no more pages.
            if callback:
                result['message'] = 'Reading coupons.'
                callback(result)

            try:
                btnShowAll = browser.find_elements_by_xpath("//div[contains(@class, 'coupon-app')]/descendant::button[contains(text(), 'Show All')]")
                if len(btnShowAll) > 0:
                    btnShowAll[0].click()

                result['existingCount'] = len(browser.find_elements_by_class_name('clipped-coupon-circle'))
                result['screenshot'] = browser.get_screenshot_as_base64()

                # Click all the buttons to add the coupons to your card
                list_of_coupon_buttons = browser.find_elements_by_css_selector("a.available-to-clip:not(.ng-hide)")

                for count, coupon_button in enumerate(list_of_coupon_buttons, start=1):
                    # Check for a modal notice dialog.
                    modals = browser.find_elements_by_class_name('modal-dialog')
                    if modals:
                        modal = modals[0]

                        # Find the dialog title.
                        titles = modal.find_elements_by_class_name('modal-title')
                        titleText = titles[0].text if titles else ''

                        bodies = modal.find_elements_by_class_name('modal-body')
                        bodyText = bodies[0].text if bodies else ''

                        if callback:
                            result['message'] = 'Found dialog "' + titleText + '": ' + bodyText
                            callback(result)

                            # Try to find the 'OK' button, otherwise click the first button found.
                            buttons = modal.find_elements_by_xpath("button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ok')]")
                            if not buttons:
                                buttons = modal.find_elements_by_xpath("//button[contains(text(), 'Close')]")
                                if not buttons:
                                    # Just find the first button.
                                    buttons = modal.find_elements_by_class_name('btn')

                            if buttons:
                                # Click the button to accept the dialog.
                                buttons[0].click()

                    # Click the "Load to Card" button.
                    coupon_button.click()

                    if callback:
                        result['count'] += 1
                        result['message'] = 'Added ' + str(result['count']) + '. Already clipped ' + str(result['existingCount']) + '.'
                        if count % 10 == 0:
                            result['screenshot'] = browser.get_screenshot_as_base64()
                        callback(result)

                    time.sleep(.5)

                if callback:
                    result['screenshot'] = browser.get_screenshot_as_base64()
                    callback(result)
            except UnexpectedAlertPresentException as e:
                print("Dismissing alert " + repr(e))
                alert = browser.switch_to_alert()
                alert.accept()
            except Exception as e:
                print(e)

            if callback:
                result['message'] = 'Complete!'
                if phone and result['count'] > 0:
                    summary = 'Couponfire clipped ' + str(result['count']) + ' coupons. You now have ' + str(result['count'] + result['existingCount']) + ' total.'
                    recipient = Textbelt.Recipient(phone)
                    response = recipient.send(summary)
                    print(summary)
                    print(response)
                callback(result)
    except UnexpectedAlertPresentException as e:
        alert = browser.switch_to_alert()
        alert.accept()
    except Exception as e:
        if callback:
            print(e)
            result['message'] = 'Error'
            result['error'] = repr(e)
            result['screenshot'] = browser.get_screenshot_as_base64()
            callback(result)

    browser.close()

    return result

def stop_and_shop(email, password, phone = None, delay = 10, callback = None, complete = None):
    initialize()

    # Get email/password from config file
    email = parser.get('stop and shop', 'email')
    password = parser.get('stop and shop', 'password')

    # Visit the Login page
    browser.get('https://stopandshop.com/login/')

    # Login
    help_element = browser.find_element_by_link_text('help')
    help_element.send_keys(Keys.TAB)
    username_element = browser.switch_to.active_element
    username_element.send_keys(email)
    username_element.send_keys(Keys.TAB)
    password_element = browser.switch_to.active_element
    password_element.send_keys(password)
    password_element.send_keys(Keys.RETURN)

    # Wait until link to go to coupons page is ready
    WebDriverWait(browser, delay).until(
        EC.presence_of_element_located((By.LINK_TEXT, 'coupons'))
    )

    # Go to coupons page
    browser.get('https://stopandshop.com/dashboard/coupons-deals/')

    # Wait until coupons are ready
    WebDriverWait(browser, delay).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'load-to-card'))
    )

    # Click all the buttons to add the coupons to your card
    list_of_coupon_buttons = browser.find_elements_by_class_name('load-to-card')

    for count, coupon_button in enumerate(list_of_coupon_buttons, start=1):
        try:
            coupon_button.click()
            if callback:
                result['message'] = 'Added ' + str(count) + ' coupons!'
                result['count'] = count
                callback(result)
            time.sleep(1)
        except:
            continue

    result['screenshot'] = browser.get_screenshot_as_base64()

    if callback:
        result['message'] = 'Complete!'
        callback(result)

    browser.close()

    return result

def acme(email, password, phone = None, delay = 10, callback = None):
    result = { 'email': email, 'existingCount': 0, 'count': 0, 'message': None, 'screenshot': None }

    initialize()

    if callback:
        result['message'] = 'Navigating to home page.'
        callback(result)

    try:
        browser.get('https://www.acmemarkets.com/account/sign-in.html?goto=/content/www/acmemarkets/en/justforu/coupons-deals.html')

        if callback:
            result['message'] = 'Locating sign-in page.'
            callback(result)

            # Wait for page load.
            WebDriverWait(browser, delay).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#label-email'))
            )

        # Login
        if callback:
            result['message'] = 'Entering login details.'
            callback(result)

        # Send login info.
        browser.find_element_by_id('label-email').send_keys(email)
        browser.find_element_by_id('label-password').send_keys(password)
        browser.find_element_by_id('label-password').send_keys(Keys.RETURN)

        if callback:
            result['message'] = 'Signing in.'
            result['screenshot'] = browser.get_screenshot_as_base64()
            callback(result)

        # Wait until the site loads, find the welcome page or error message.
        WebDriverWait(browser, delay).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'button.load-more'))
        )

        # Read all coupons on the current page, then process all subsequent pages by clicking Next, until no more pages.
        if callback:
            result['message'] = 'Reading coupons.'
            callback(result)

        try:
            btnLoadMore = browser.find_element_by_css_selector('button.load-more');
            while btnLoadMore:
                btnLoadMore.click();
                time.sleep(1)
                try:
                    btnLoadMore = browser.find_element_by_css_selector('button.load-more');
                except:
                    break

            result['existingCount'] = len(browser.find_elements_by_class_name('coupon-clipped-container'))
            result['screenshot'] = browser.get_screenshot_as_base64()

            # Click all the buttons to add the coupons to your card
            list_of_coupon_buttons = browser.find_elements_by_css_selector("button.grid-coupon-btn")

            for count, coupon_button in enumerate(list_of_coupon_buttons, start=1):
                try:
                    # Click the "Load to Card" button.
                    coupon_button.click()

                    if callback:
                        result['count'] += 1
                        result['message'] = 'Added ' + str(result['count']) + '. Already clipped ' + str(result['existingCount']) + '.'
                        if count % 10 == 0:
                            result['screenshot'] = browser.get_screenshot_as_base64()
                        callback(result)

                    time.sleep(.25)
                except:
                    continue

            if callback:
                result['screenshot'] = browser.get_screenshot_as_base64()
                callback(result)
        except Exception as e:
            print(e)

        if callback:
            result['message'] = 'Complete!'
            if phone and result['count'] > 0:
                summary = 'Couponfire clipped ' + str(result['count']) + ' coupons. You now have ' + str(result['count'] + result['existingCount']) + ' total.'
                recipient = Textbelt.Recipient(phone)
                response = recipient.send(summary)
                print(summary)
                print(response)
            callback(result)
    except Exception as e:
        if callback:
            print(e)
            result['message'] = 'Error'
            result['error'] = repr(e)
            result['screenshot'] = browser.get_screenshot_as_base64()
            callback(result)

    browser.close()

    return result