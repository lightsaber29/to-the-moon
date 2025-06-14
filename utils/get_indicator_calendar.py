from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 1. 크롬 옵션 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36")

# 2. 크롬 드라이버 서비스 생성
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 3. 페이지 접속
url = "https://globalmonitor.einfomax.co.kr/ht_usa.html#/2/1"
driver.get(url)

# 4. 테이블이 로딩될 때까지 최대 15초 기다리기
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
)

# 5. HTML 파싱
soup = BeautifulSoup(driver.page_source, "html.parser")

# 제목 행 추출
header_row = soup.select_one("table thead tr")
headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
print(headers)

# 본문 행 추출
rows = soup.select("table tbody tr")
for row in rows:
    cols = []
    tds = row.find_all("td")
    for idx, td in enumerate(tds):
        if idx == 6:  # 중요도 열 (★)
            stars = td.select("img[alt='별']")
            cols.append(str(len(stars)))  # 숫자만 (예: '2')
        else:
            cols.append(td.get_text(strip=True))
    print(cols)

driver.quit()
