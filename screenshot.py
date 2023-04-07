from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from selenium.common.exceptions import NoSuchElementException

# Config
screenshotDir = "Screenshots"
screenWidth = 400
screenHeight = 800



#  check for a Google login popup and close it before proceeding
# def close_google_login_popup(driver, wait):
#     try:
#         # Wait for a few seconds before attempting to locate the close button
#         time.sleep(5)
#         # Locate the close button using its class name with an increased timeout
#         close_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg.Bz112c.Bz112c-r9oPif')))
#         close_button.click()
#     except TimeoutException:
#         print("Could not find the Google login popup close button or it took too long to load.")
#         pass



def close_google_login_popup(driver, wait):
    try:
        # Wait for a few seconds before attempting to locate the close button
        time.sleep(5)

        # Locate the SVG element using the 'svg' tag with an increased timeout
        svg_elements = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'svg')))

        # Check if the 'd' attribute of the first path element inside the SVG matches the desired value
        target_d_value = "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
        for svg in svg_elements:
            try:
                path = svg.find_element(By.TAG_NAME, 'path')
                if path.get_attribute('d') == target_d_value:
                    svg.click()
                    break
            except NoSuchElementException:
                continue

    except TimeoutException:
        print("Could not find the Google login popup close button or it took too long to load.")
        pass


def accept_cookies(driver, wait):
    try:
        # Replace 'cookie_accept_button_selector' with the actual selector of the button
        accept_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, '_1tI68pPnLBjR1iHcL7vsee')))
        accept_button.click()
    except TimeoutException:
        print("Could not find the cookie accept button or it took too long to load.")
        
        pass




def enable_dark_mode(driver, wait):
    try:
        # Click on the profile icon to open the dropdown menu
        profile_icon = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, '_3x3dhQasGAuYcXVQ02QUzy')))
        profile_icon.click()

        # Click on the dark mode toggle button to enable dark mode
        dark_mode_toggle = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, '_2e2g485kpErHhJQUiyvvC2')))
        dark_mode_toggle.click()

        # Click on the profile icon again to close the dropdown menu
        profile_icon.click()
    except TimeoutException:
        print("Could not find the required elements or they took too long to load.")
        pass

def getPostScreenshots(filePrefix, script):
    print("Taking screenshots...")
    driver, wait = __setupDriver(script.url)

    # Close the Google login popup if present - not required in most of the cases
    close_google_login_popup(driver, wait)

    # Accept cookies before taking screenshots
    accept_cookies(driver, wait)

    # Enable dark mode
    enable_dark_mode(driver, wait)

    script.titleSCFile = __takeScreenshot(filePrefix, driver, wait)
    for commentFrame in script.frames:
        # Check if the author of the comment is not [deleted]
        if commentFrame.author != "[deleted]":
            commentFrame.screenShotFile = __takeScreenshot(filePrefix, driver, wait, f"t1_{commentFrame.commentId}")
    driver.quit()


# def getPostScreenshots(filePrefix, script):
#     print("Taking screenshots...")
#     driver, wait = __setupDriver(script.url)

#     # Close the Google login popup if present - not required in most of the cases, commented for now
#     # close_google_login_popup(driver, wait)

#     # Accept cookies before taking screenshots
#     accept_cookies(driver, wait)
#     # accept_cookies(driver, wait)

#     # Enable dark mode
#     enable_dark_mode(driver, wait)

#     script.titleSCFile = __takeScreenshot(filePrefix, driver, wait)
#     for commentFrame in script.frames:
#         commentFrame.screenShotFile = __takeScreenshot(filePrefix, driver, wait, f"t1_{commentFrame.commentId}")
#     driver.quit()

def __takeScreenshot(filePrefix, driver, wait, handle="Post"):
    method = By.CLASS_NAME if (handle == "Post") else By.ID
    search = wait.until(EC.presence_of_element_located((method, handle)))
    driver.execute_script("window.focus();")

    fileName = f"{screenshotDir}/{filePrefix}-{handle}.png"
    fp = open(fileName, "wb")
    fp.write(search.screenshot_as_png)
    fp.close()
    return fileName

def __setupDriver(url: str):
    options = webdriver.FirefoxOptions()
    options.headless = False
    options.enable_mobile = False
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 10)

    driver.set_window_size(width=screenWidth, height=screenHeight)
    driver.get(url)

    return driver, wait