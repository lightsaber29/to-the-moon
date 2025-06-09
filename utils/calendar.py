import urllib
import urllib.request
from urllib.error import HTTPError
from urllib.parse import urlencode

from bs4 import BeautifulSoup
import datetime
import arrow


class Good():
	def __init__(self):
		self.value = "+"
		self.name = "good"

	def __repr__(self):
		return "<Good(value='%s')>" % (self.value)


class Bad():
	def __init__(self):
		self.value = "-"
		self.name = "bad"

	def __repr__(self):
		return "<Bad(value='%s')>" % (self.value)


class Unknow():
	def __init__(self):
		self.value = "?"
		self.name = "unknow"

	def __repr__(self):
		return "<Unknow(value='%s')>" % (self.value)		


class Investing():
	def __init__(self, date_from=None, date_to=None):
		base_url = 'https://www.investing.com/economic-calendar/'
		params = {}
		if date_from and date_to:
			params['dateFrom'] = date_from
			params['dateTo'] = date_to
			self.uri = f"{base_url}?{urlencode(params)}"
		else:
			self.uri = base_url
		self.req = urllib.request.Request(self.uri)
		self.req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
		self.result = []

	def news(self):
		try:
			response = urllib.request.urlopen(self.req)
			html = response.read()
			soup = BeautifulSoup(html, "html.parser")

			table = soup.find('table', {"id": "economicCalendarData"})
			tbody = table.find('tbody')
			rows = tbody.find_all('tr', {"class": "js-event-item"})

			for row in rows:
				news = {
					'timestamp': None,
					'country': None,
					'impact': None,
					'url': None,
					'name': None,
					'bold': None,
					'fore': None,
					'prev': None,
					'signal': None,
					'type': None
				}

				_datetime = row.attrs['data-event-datetime']
				news['timestamp'] = arrow.get(_datetime, "YYYY/MM/DD HH:mm:ss").timestamp

				cols = row.find('td', {"class": "flagCur"})
				flag = cols.find('span')
				news['country'] = flag.get('title')

				impact = row.find('td', {"class": "sentiment"})
				bull = impact.find_all('i', {"class": "grayFullBullishIcon"})
				news['impact'] = len(bull)

				event = row.find('td', {"class": "event"})
				a = event.find('a')
				news['url'] = "{}{}".format(self.uri, a['href'])
				news['name'] = a.text.strip()

				# 이벤트 타입 판별
				if event.find('span', {"class": "smallGrayReport"}):
					news['type'] = "report"
				elif event.find('span', {"class": "audioIconNew"}):
					news['type'] = "speech"
				elif event.find('span', {"class": "smallGrayP"}):
					news['type'] = "release"
				elif event.find('span', {"class": "sandClock"}):
					news['type'] = "retrieving data"

				bold = row.find('td', {"class": "bold"})
				news['bold'] = bold.text.strip() if bold.text != '' else ''

				fore = row.find('td', {"class": "fore"})
				news['fore'] = fore.text.strip()

				prev = row.find('td', {"class": "prev"})
				news['prev'] = prev.text.strip()

				if "blackFont" in bold['class']:
					news['signal'] = Unknow()
				elif "redFont" in bold['class']:
					news['signal'] = Bad()
				elif "greenFont" in bold['class']:
					news['signal'] = Good()
				else:
					news['signal'] = Unknow()


				# 데이터 필터링
				# 국가: 미국
				if news['country'] != 'United States':
					continue

				# 영향도: 3 이상
				impact_value = int(news['impact']) if str(news['impact']).isdigit() else 0
				if impact_value < 3:
					continue

				self.result.append(news)

		except HTTPError as error:
			print("Oops... Get error HTTP {}".format(error.code))

		return self.result


if __name__ == "__main__":
	# 한 달치 데이터
	date_from = "2025-06-01"
	date_to = "2025-06-30"
	i = Investing(date_from=date_from, date_to=date_to)
	news_data = i.news()
	print(f'date_from: {date_from}, date_to: {date_to} 지표 데이터 개수: {len(news_data)}')
	# print(*news_data, sep='\n')

	# CSV로 저장
	import csv
	if news_data:
		keys = news_data[0].keys()
		with open('calendar_data.csv', 'w', newline='', encoding='utf-8') as f:
			writer = csv.DictWriter(f, fieldnames=keys)
			writer.writeheader()
			writer.writerows(news_data)