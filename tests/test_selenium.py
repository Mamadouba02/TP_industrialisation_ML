import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.e2e
@pytest.mark.skipif(os.getenv('RUN_E2E') != '1', reason='RUN_E2E=1 and a running API/Chrome required')
def test_application():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(os.getenv('API_URL', 'http://localhost:8000') + '/docs')
        WebDriverWait(driver, 60).until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '/predict'))
        assert 'Churn Prediction API' in driver.title
        assert '/predict' in driver.find_element(By.TAG_NAME, 'body').text
    finally:
        driver.quit()
