import time
from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
# from robocorp.browser import WaitForSelectorState

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    download_csv_file()
    orders = get_orders()
    for order_number in orders:
        close_annoying_modal()
        fill_the_form(order_number)
    archive_receipts()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    page=browser.page()
    page.locator('button', has_text='Yep').click()

def download_csv_file():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def fill_the_form(order):
    page = browser.page()
    page.locator('#head').select_option(order['Head'])
    page.locator(f'#id-body-{order["Body"]}').click()
    page.get_by_placeholder('Enter the part number for the legs').fill(order['Legs'])
    page.locator('#address').fill(order['Address'])
    page.locator('#preview').click()
    page.locator('#order').click()
    time.sleep(5)

    image= screenshot_robot(order['Order number'])
    reciept_path=store_receipt_as_pdf(order['Order number'])
    
    embed_screenshot_to_receipt(image, reciept_path)
    page.click('id=order-another')

def get_orders():
    """Reads the orders from the CSV file"""
    tables = Tables()
    orders = tables.read_table_from_csv("orders.csv", header=True)
    return orders

def store_receipt_as_pdf(order):
    """Stores the order receipt as a PDF file"""
    reciept_path = f'./output/reciepts/order_{order}_reciept.pdf'
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt, reciept_path)
    return reciept_path

def screenshot_robot(order):
    """Takes a screenshot of the ordered robot"""
    screenshot_path = f'./output/reciepts/order_{order}_img.png'
    page = browser.page()
    page.locator('#robot-preview-image').screenshot(path=screenshot_path)
    
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):    
    """Embeds the screenshot to the PDF receipt"""
    pdf = PDF()
    
    pdf.add_files_to_pdf(files=[screenshot], target_document='output/reciepts/receipt_results.pdf', append=True)

def archive_receipts():
    """Creates a ZIP archive of the receipts and images"""
    archive = Archive()
    archive.archive_folder_with_zip(folder='./output/reciepts', archive_name='./output/reciepts/reciepts.zip')