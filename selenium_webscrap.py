from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import pyperclip
import json

# Use the link "the Chrome for Testing availability dashboard" on following page
# to get the correct "STABLE" Chrome-driver-version:
#  - https://chromedriver.chromium.org/home

URL_VEHICLE = "https://gta.fandom.com/wiki/Vehicles_in_GTA_Online"
CLASS_TABLE = "wikitable"
XPATH_TABLE = '//*[@id="mw-content-text"]/div[1]/table[2]'
XPATH_IMAGE = "aside/section[1]/figure[2]/a"
XPATH_PRICE = "aside/section[2]/div/div"
CLASS_STATS = "rssc-stats-container"
CLASS_INFOS = "rssc-info-container"
LIMIT = 150


def open_chrome(url: str, chrome_driver_path: str = "chromedriver.exe"):
    """Open an URL using the Chrome-driver.
    - Parameters:
        - url: A string representing the webpage-address to be opened.
        - chrome_driver_path-driver-path: An optional string representing the path of the Chrome-driver to use.
          By default the Chrome-driver within the same directory is used.
    - Returns:
        - A Chrome-driver with the specified URL opened.
    """
    service = webdriver.ChromeService(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options, service=service)
    driver.get(url)
    return driver


def get_element(driver, by_method, name: str, timeout: float = 5.0):
    """Find an web-element given a By strategy and locator (incl. wait page loading).
    - Parameters:
        - driver: A driver (e.g. a Chrome-driver).
        - by_method: A supported locator strategies.
          Arguments e.g.:
            - By.ID
            - By.CLASS_NAME
            - By.XPATH
        - name: A string representing the locator.
          Arguments e.g.:
            - "main-heading"
            - "important-reminder"
            - "/html/body/div[1]/div/img[1]"
        - timeout: An optional float representing the number of seconds before timing out (page loading).
    - Returns:
        - The WebElement once it is located.
    """
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by_method, name))
    )
    return driver.find_element(by_method, name)


def get_elements(driver, by_method, name: str):
    """Find web-elements given a By strategy and locator (incl. wait page loading).
    - Parameters:
        - driver: A driver (e.g. a Chrome-driver).
        - by_method: A supported locator strategies.
          Arguments e.g.:
            - By.ID
            - By.CLASS_NAME
            - By.XPATH
        - name: A string representing the locator.
          Arguments e.g.:
            - "main-heading"
            - "important-reminder"
            - "/html/body/div[1]/div/img[1]"
        - timeout: An optional float representing the number of seconds before timing out (page loading).
    - Returns:
        - A list of the WebElements once it is located.
    """
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((by_method, name)))
    return driver.find_elements(by_method, name)


def click_element(element: WebElement):
    """Click a given web-element (prints the exception when raised).
    - Parameters:
        - element: The web-element to click.
    """
    try:
        element.click()
    except Exception as e:
        print(e)


def scroll_to_element(element: WebElement):
    """Scroll to a given web-element (prints the exception when raised).
    - Parameters:
        - element: The web-element to scroll to.
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView();", element)
    except Exception as e:
        print(e)


def write_json(file_path: str, data):
    """Write the data to a JSON file using the standard library 'json': https://docs.python.org/3/library/json.html
    - Parameters:
        - file_path: A string representing the destination file path.
        - data: A dictionary or a list containing the data to be written to the JSON file.
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def read_json(file_path: str):
    """Read the data from a JSON file using the standard library 'json': https://docs.python.org/3/library/json.html
    - Parameters:
        - file_path: A string representing the file path.
    - Returns:
        - A dictionary or a list containing the data of the JSON file.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def set_to_clipboard(text: str):
    """Set a given text to the clipboard (CTRL+C) using the library 'pyperclip': https://pypi.org/project/pyperclip/
    - Parameters:
        - text: A string representing the text to be set to the clipboard.
    """
    pyperclip.copy(text)
    print("Clipboard set:\n", text)


def get_from_clipboard():
    """Get the content of the clipboard (CTRL+V) using the library 'pyperclip': https://pypi.org/project/pyperclip/
    - Returns:
        - A string containing the content of the clipboard.
    """
    text = pyperclip.paste()
    print("Clipboard get:\n", text)
    return text


if __name__ == "__main__":
    # Open Chrome with URL
    driver = open_chrome(URL_VEHICLE)

    # Get vehicle links
    vehicle_table = get_element(driver, By.XPATH, XPATH_TABLE)
    # scroll_to_element(vehicle_table)
    links = {}
    for row in vehicle_table.find_elements(By.CSS_SELECTOR, "tr"):
        for cell in row.find_elements(By.CSS_SELECTOR, "td"):
            for list in cell.find_elements(By.CSS_SELECTOR, "ul"):
                for item in list.find_elements(By.CSS_SELECTOR, "li"):
                    try:
                        link = item.find_element(By.CSS_SELECTOR, "a")
                    except:
                        print("ERROR: Link element within list-item not found!")
                    else:
                        links[link.get_attribute("innerText")] = link.get_attribute(
                            "href"
                        )

    # Write links to JSON
    write_json("gta_links.json", links)

    # # Read links from JSON
    # links = read_json("gta_links.json")

    # Get data from vehicle links
    data = {}
    cnt = 0
    for name, url in links.items():
        cnt += 1
        # Create record
        record = {}
        # Open page
        driver.get(url)
        # Set link
        record["link"] = url
        # Set image
        container = driver.find_element(By.CLASS_NAME, "nohero")
        element = container.find_element(By.XPATH, XPATH_IMAGE)
        url = element.get_attribute("href")
        record["image"] = url[: url.lower().index(".png") + 4]
        # Set vehicle class
        for el in container.find_elements(By.TAG_NAME, "div"):
            if el.get_attribute("data-source") == "class":
                value = el.get_attribute("innerText")
                break
        record["CLASS"] = value.split("\n")[1].split("(")[0]
        # Set price
        element = container.find_elements(By.XPATH, XPATH_PRICE)
        if len(element) > 0:
            element = element[0]
            price = element.get_attribute("innerText")
            if "$" in price:
                price = price.replace(",", "").replace("\n", " ").replace("(", " ")
                idx = price.index("$")
                record["PRICE"] = int(price[idx:].split(" ")[0].replace("$", ""))
        # Set stats
        container = driver.find_elements(By.CLASS_NAME, CLASS_STATS)
        if len(container) > 0:
            container = container[0]
            for idx in range(4):
                title = container.find_element(
                    By.CLASS_NAME, CLASS_STATS.replace("container", f"name{idx + 1}")
                )
                stats = container.find_element(
                    By.CLASS_NAME, CLASS_STATS.replace("container", f"data{idx + 1}")
                )
                element = stats.find_elements(By.XPATH, "div[1]/div[1]")
                if len(element) > 0:
                    element = element[0]
                    record[title.get_attribute("innerText")] = element.size["width"]
        # Set info
        container = driver.find_elements(By.CLASS_NAME, CLASS_INFOS)
        if len(container) > 0:
            container = container[0]
            for idx in range(7):
                title = container.find_element(
                    By.CLASS_NAME, CLASS_INFOS.replace("container", f"name{idx + 1}")
                )
                element = container.find_element(
                    By.CLASS_NAME, CLASS_INFOS.replace("container", f"data{idx + 1}")
                )
                value = element.get_attribute("innerText")
                if value == "":
                    element = element.find_element(By.XPATH, "img[1]")
                    value = False
                    if "Check" in element.get_attribute("data-image-name"):
                        value = True
                elif value.isnumeric():
                    value = int(value)
                record[title.get_attribute("innerText")] = value
        # Add record to data
        data[name] = record
        if cnt > LIMIT:
            break

    # Write vehicle data to JSON
    write_json("gta_vehicles.json", data)

    # # Read vehicle data from JSON
    # data = read_json("gta_vehicles.json")

    # Create tabular data
    table = []
    for vehicle, values in data.items():
        record = {"Vehicle": vehicle}
        for key, value in values.items():
            record[key] = value
        table.append(record)

    # Write tabular data to JSON
    write_json("Vehicles_Table.json", table)
