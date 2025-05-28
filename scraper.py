from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def extract_text(driver, label):
    try:
        elem = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//label[contains(text(), '{label}')]/following-sibling::*[1]"
            ))
        )
        return elem.text.strip()
    except:
        return "N/A"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)
driver.get("https://rera.odisha.gov.in/projects/project-list")

time.sleep(5)

projects = []

for i in range(6):
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'View Details')]")))
        view_buttons = driver.find_elements(By.XPATH, "//a[contains(text(),'View Details')]")

        if i >= len(view_buttons):
            print(f"❌ Less than {i+1} projects available.")
            break

        print(f"🔍 Scraping project {i+1}")
        driver.execute_script("arguments[0].scrollIntoView(true);", view_buttons[i])
        driver.execute_script("arguments[0].click();", view_buttons[i])
        time.sleep(3)

        # Extract from Overview tab
        rera_no = extract_text(driver, "RERA Regd. No.")
        project_name = extract_text(driver, "Project Name")

        # Switch to Promoter Details tab
        promoter_tab = driver.find_element(By.XPATH, "//a[contains(text(),'Promoter Details')]")
        driver.execute_script("arguments[0].click();", promoter_tab)
        time.sleep(2)

        promoter_name = extract_text(driver, "Company Name")
        promoter_address = extract_text(driver, "Registered Office Address")
        gst_no = extract_text(driver, "GST No")

        projects.append({
            "RERA Regd. No": rera_no,
            "Project Name": project_name,
            "Promoter Name": promoter_name,
            "Promoter Address": promoter_address,
            "GST No": gst_no
        })

        print(f"✅ Scraped: {project_name}")
        driver.back()
        time.sleep(3)

    except Exception as e:
        print(f"❌ Error scraping project {i+1}: {e}")
        driver.back()
        time.sleep(3)

driver.quit()

with open("project_details.json", "w", encoding="utf-8") as f:
    json.dump(projects, f, indent=2, ensure_ascii=False)

print("✅ Saved project details to project_details.json")
