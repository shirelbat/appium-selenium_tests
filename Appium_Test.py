import unittest
from appium import webdriver as appium_webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from appium.webdriver.common.appiumby import AppiumBy
from datetime import datetime
from random import randint
from time import sleep

appium_server_url_local = "http://localhost:4723/wd/hub"
capabilities = dict(
    platformName="Android",
    deviceName="Pixel7a",
    udid="emulator-5554",
    appPackage="com.google.android.dialer",
    appActivity="com.google.android.dialer.extensions.GoogleDialtactsActivity",
    platformVersion="35"
)

class Test_HOT(unittest.TestCase):
    def setUp(self) -> None:
        # Initialize Appium driver for Android Dialer application
        self.driver = appium_webdriver.Remote(appium_server_url_local, capabilities)

        # Open Chrome browser and retrieve phone number and working hours from HOT website
        chrome_service = ChromeService(ChromeDriverManager().install())
        self.driver_w = webdriver.Chrome(service=chrome_service)
        self.driver_w.get("https://www.hotmobile.co.il/HOTmobile_en/Pages/Contact-Us.aspx")
        self.driver_w.maximize_window()
        self.driver_w.implicitly_wait(20)

        # Extract phone number from the page (using partial link text that contains '053')
        self.the_phone_number = WebDriverWait(self.driver_w, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, '053'))
        ).text
        self.the_phone_number = self.the_phone_number.replace('-', '')

        # Extract working hours from the page using XPath
        activity_time = WebDriverWait(self.driver_w, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//*[@id="ctl00_PlaceHolderMain_PublishingPageContent__ControlWrapper_RichHtmlField"]/div[6]/div[1]/div[2]/span[2]'))
        ).text
        self.begin = activity_time[-32:-31]  # Extract opening time
        self.end = activity_time[-27:-25]    # Extract closing time
        print(self.begin)
        print(self.end)
        print(self.the_phone_number)
        self.driver_w.quit()

    def tearDown(self) -> None:
        # Close both Appium and Chrome drivers after the test
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
        if hasattr(self, 'driver_w') and self.driver_w:
            self.driver_w.quit()

    # Test 01: Verifying the ability to dial the retrieved phone number
    def test_01_phon(self):
        # Open dial pad
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/dialpad_fab'))).click()

        # Input the retrieved phone number
        number_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/digits')))
        number_field.send_keys(self.the_phone_number)

        # Click on the call button
        call_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/dialpad_voice_call_button')))
        call_button.click()

        # Verify the call is active by checking for the presence of the "End call" button
        hang_up_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.Button[@content-desc="End call"]')))
        print(type(hang_up_button))
        print(appium_webdriver.WebElement)
        self.assertEqual(type(hang_up_button), appium_webdriver.WebElement)
        self.assertTrue(hang_up_button.is_displayed())

        # End the call
        hang_up_button.click()
        sleep(4)
        self.driver.back()
        sleep(4)
        self.driver.back()

    # Test 02: Verifying the ability to send a message to the retrieved phone number
    def test_02_message(self):
        # Navigate back to the main screen and open the "Messages" app
        self.driver.back()
        sleep(4)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Messages"]'))).click()
        start_chat = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.apps.messaging:id/start_chat_fab')))
        start_chat.click()

        # Select the contact to send the message to
        hot = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.XPATH,'//android.view.View[@resource-id="contact_row_test_prefix_1"]/android.view.View/android.view.View[2]')))
        hot.click()

        # Write and send a message
        message_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.CLASS_NAME, 'android.widget.EditText')))
        the_message = 'call me back please' + str(randint(1, 100000))
        message_field.click()
        message_field.send_keys(the_message)
        print(the_message)
        send_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.XPATH, '//android.view.View[@content-desc="Send SMS"]')))
        send_button.click()
        self.driver.back()
        self.driver.back()

        # Verify that the send message is displayed in the conversation
        the_text_check = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.apps.messaging:id/conversation_snippet'))).text
        print(the_text_check)
        self.assertEqual('You: ' + the_message, the_text_check)
        self.driver.back()
        self.driver.back()

    # Test 03: Decide whether to call or send a message based on the current time and working hours
    def test_03_phon_or_message(self):
        current_time = datetime.now().time()  # Get the current time
        begin_time = datetime.strptime(self.begin, "%H").time()  # Convert opening time to time object
        end_time = datetime.strptime(self.end, "%H").time()      # Convert closing time to time object

        # Check if the current time is within the working hours
        if begin_time <= current_time <= end_time:
            print(f"The current time is within business hours, so a call will be placed.")

            # Open dial pad and input the phone number
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/dialpad_fab'))).click()
            number_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/digits')))
            number_field.send_keys(self.the_phone_number)

            # Click the call button
            call_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/dialpad_voice_call_button')))
            call_button.click()

            # Verify the call is active
            hang_up_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.Button[@content-desc="End call"]')))
            self.assertEqual(type(hang_up_button), appium_webdriver.WebElement)
            self.assertTrue(hang_up_button.is_displayed())

            # End the call
            hang_up_button.click()
            sleep(4)
            self.driver.back()
            sleep(4)
            self.driver.back()
            sleep(4)

        else:
            print(f"The current time is outside business hours, so a message will be sent.")

            # Navigate to "Messages" app and select contact
            self.driver.back()
            sleep(4)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Messages"]'))).click()
            start_chat = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.apps.messaging:id/start_chat_fab')))
            start_chat.click()

            hot = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.XPATH,'//android.view.View[@resource-id="contact_row_test_prefix_1"]/android.view.View/android.view.View[2]')))
            hot.click()

            # Write and send a message
            message_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.CLASS_NAME, 'android.widget.EditText')))
            the_message = 'call me back please' + str(randint(1, 10000))
            message_field.click()
            message_field.send_keys(the_message)
            print(the_message)
            send_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//android.view.View[@content-desc="Send SMS"]')))
            send_button.click()
            self.driver.back()
            self.driver.back()

            # Verify that the sent message is displayed in the conversation
            the_text_check = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.apps.messaging:id/conversation_snippet'))).text
            print(the_text_check)
            self.assertEqual('You: ' + the_message, the_text_check)
            self.driver.back()
            self.driver.back()

    # Test 04: Similar to Test 03 but specifically verifies the functionality of placing a call during business hours
    def test_04_pone_in_time_activity(self):
        current_time = datetime.now().time()  # Get the current time
        begin_time = datetime.strptime(self.begin, "%H").time()  # Convert opening time to time object
        end_time = datetime.strptime(self.end, "%H").time()      # Convert closing time to time object

        # Check if the current time is within the working hours
        if begin_time <= current_time <= end_time:
            print(f"The current time is within business hours, so a call will be placed.")

            # Open dial pad and input the phone number
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/dialpad_fab'))).click()
            number_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/digits')))
            number_field.send_keys(self.the_phone_number)

            # Click the call button
            call_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/dialpad_voice_call_button')))
            call_button.click()

            # Verify the call is active
            hang_up_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.Button[@content-desc="End call"]')))
            print(type(hang_up_button))
            print(appium_webdriver.WebElement)
            self.assertEqual(type(hang_up_button), appium_webdriver.WebElement)
            self.assertTrue(hang_up_button.is_displayed())

            # End the call
            hang_up_button.click()
            sleep(4)
            self.driver.back()
            sleep(4)

        else:
            print(f"The current time is outside business hours, so a message will be sent.")

        # Navigate to "Messages" app and select contact
        self.driver.back()
        sleep(4)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Messages"]'))).click()
        start_chat = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.apps.messaging:id/start_chat_fab')))
        start_chat.click()

        hot = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.view.View[@resource-id="contact_row_test_prefix_1"]/android.view.View/android.view.View[2]')))
        hot.click()

        # Write and send a message
        message_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.CLASS_NAME, 'android.widget.EditText')))
        the_message = 'give WI-FI code' + str(randint(1, 10000))
        message_field.click()
        message_field.send_keys(the_message)
        print(the_message)
        send_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.view.View[@content-desc="Send SMS"]')))
        send_button.click()
        self.driver.back()
        self.driver.back()

        # Verify that the sent message is displayed in the conversation
        the_text_check = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.apps.messaging:id/conversation_snippet'))).text
        print(the_text_check)
        self.assertEqual('You: ' + the_message, the_text_check)
        self.driver.back()
        self.driver.back()

    # Test 05: Verify that both calling and messaging functionalities work in sequence
    def test_05_phon_and_message(self):
        # Open dial pad and input the phone number
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/dialpad_fab'))).click()
        number_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/digits')))
        number_field.send_keys(self.the_phone_number)

        # Click the call button
        call_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.dialer:id/dialpad_voice_call_button')))
        call_button.click()

        # Verify the call is active
        hang_up_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.Button[@content-desc="End call"]')))
        print(type(hang_up_button))
        print(appium_webdriver.WebElement)
        self.assertEqual(type(hang_up_button), appium_webdriver.WebElement)
        self.assertTrue(hang_up_button.is_displayed())

        # End the call
        hang_up_button.click()
        sleep(4)
        self.driver.back()
        sleep(4)
        self.driver.back()
        sleep(4)

        # Navigate to "Messages" app and select contact
        self.driver.back()
        sleep(4)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Messages"]'))).click()
        start_chat = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.apps.messaging:id/start_chat_fab')))
        start_chat.click()

        hot = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.view.View[@resource-id="contact_row_test_prefix_1"]/android.view.View/android.view.View[2]')))
        hot.click()

        # Write and send a message
        message_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.CLASS_NAME, 'android.widget.EditText')))
        the_message = 'call me back please' + str(randint(1, 10000))
        message_field.click()
        message_field.send_keys(the_message)
        print(the_message)
        send_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.view.View[@content-desc="Send SMS"]')))
        send_button.click()
        self.driver.back()
        self.driver.back()

        # Verify that the sent message is displayed in the conversation
        the_text_check = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.google.android.apps.messaging:id/conversation_snippet'))).text
        print(the_text_check)
        self.assertEqual('You: ' + the_message, the_text_check)
        self.driver.back()
        self.driver.back()
