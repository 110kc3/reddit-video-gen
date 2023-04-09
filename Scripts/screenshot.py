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

def __add_opacity(driver, element, opacity=0.2, color='255, 255, 255'):
    script = f"""
    var overlay = document.createElement('div');
    overlay.style.position = 'absolute';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba({color}, {opacity})';
    arguments[0].appendChild(overlay);
    """
    driver.execute_script(script, element)


def __takeScreenshot(filePrefix, driver, wait, handle="Post"):
    method = By.CLASS_NAME if (handle == "Post") else By.ID
    search = wait.until(EC.presence_of_element_located((method, handle)))
    driver.execute_script("window.focus();")

    # Add opacity to the element before taking the screenshot - this has some color issues, commented for now
    # __add_opacity(driver, search, opacity=0.8)
  
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