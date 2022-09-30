"""도스쉘에서 다음과 같이 입력하면 자동으로 패키지 다운, 설치가 됩니다.
   시간이 소요되니 커서가 뜰 때까지 기다려 주세요.
   pip install beautifulsoup4
   pip install matplotlib
"""

#내장 모듈
from curses.ascii import isdigit
from urllib.request import *
import sys
import time
import json

#외부 모듈
from bs4 import *
import matplotlib.pyplot as p

def parsePlayerData ( year, playerType ) :
	"""네이버 KBO 자료실에서 해당 연도의 입력받은 타입에 대한 
	   입력: year: 정보를 가져올 연도, playerType: 투수 (1), 타자 (2)
	   출력: 선수들 정보를 담은 list
	"""

	playerList = []
	dataName = ['이름', '평균자책', '이닝수', '승률', '탈삼진', '피안타', '볼넷']

	# Web 요청시 필요한 데이터 정리
	type = 'pitcher'
	order = 'era'
	if (playerType == 2):
		type = 'batter'
		order = 'hra'
		dataName = ['타율', '타수', '안타', '홈런', '득점', '장타율']
	# https://sports.news.naver.com/kbaseball/record/index?category=kbo&year=2022&type=pitcher&playerOrder=era
	# https://sports.news.naver.com/kbaseball/record/index?category=kbo&year=2022&type=batter&playerOrder=hra

	req = Request ('https://sports.news.naver.com/kbaseball/record/index?category=kbo&year=' + str(year) + '&type=' + type + '&playerOrder=' + order)
	req.add_header('User-Agent', 'Mozilla/5.0') #정상적인 웹 크롤러라고 헤더에 표시
	wp = urlopen(req)
	soup = BeautifulSoup(wp, 'html.parser', from_encoding="euc-kr") # parsing

	table = soup.find_all('script')

	playerRecord = str(table[13].get_text()) # 13번째 Script Tag 안에 선수 정보가 들어있음
	playerDataStartIndex = playerRecord.index('[{') # JSON Data 시작 Index 찾기
	playerDataEndIndex = playerRecord.index('}],') + 2 # JSON Data 끝나는 지점 찾기
	playerData = playerRecord[playerDataStartIndex:playerDataEndIndex] # JSON으로 저장된 선수 정보 읽어오기
	playerJSON = json.loads(playerData) # JSON Parsing

	for player in playerJSON:
		if (playerType == 1):
			# 투수
			# 이름 name, 평균자책 era, 이닝수 inn, 승률 winp, 탈삼진 kk, 피안타 hit, 볼넷 bb 혹은 r
			playerList.append([player['name'] + ' (' + player['team'] + ')', float(player['era']) ,int(player['inn'][:3]), float(player['winp']), player['kk'], player['hit'], player['bb']])
		else:
			# 타자
			# 이름 name, 타율 hra, 타수 ab, 안타 hit, 홈런 hr, 득점 run, 장타율 slg
			playerList.append([player['name'] + ' (' + player['team'] + ')', float(player['hra']) , player['ab'], player['hit'], player['hr'], player['run'], float(player['slg'])])

	return playerList, dataName

def getDrawPlayerIndex(playerList) :
	""" 그래프를 그릴 선수의 index를 계산해주는 함수
		입력: 없음
		출력: 그래프를 그릴 선수들의 index list
	"""
	print('===== 표시 가능한 선수 목록 =====')
	for i in range(len(playerList)):
		print(str(i + 1) + ': ' + playerList[i][0], end = ' ')
		if (i % 5 == 4):
			print('')
	print('\n선수 정보 표시 방법을 선택하세요')

	graphMode = input("1: 상위 5인 표시 / 2: 두 선수 비교 / 3: 특정 선수 표시 : ")

	if (graphMode.isdigit() == False):
		print("잘못된 입력입니다. 프로그램을 종료합니다.")
		sys.exit()

	graphMode = int(graphMode)

	drawPlayerIndex = []

	if (graphMode == 1):
		drawPlayerIndex = [0, 1, 2, 3, 4]
	elif (graphMode == 2):
		playerIndexStr = input('비교할 두 선수의 번호를 입력하세요 (ex: 1 15) : ')
		index1, index2 = playerIndexStr.split(' ')
		if (index1.isdigit() == False or index2.isdigit() == False):
			print("잘못된 입력입니다. 프로그램을 종료합니다.")
			sys.exit()
		drawPlayerIndex = [index1 - 1, index2 - 1]
	elif (graphMode == 3):
		playerIndexStr = input('정보를 보고 싶은 선수의 번호를 입력하세요 : ')
		if (playerIndexStr.isdigit() == False or (int(playerIndexStr) < 1 or int(playerIndexStr) > 20)):
			print("잘못된 입력입니다. 프로그램을 종료합니다.")
			sys.exit()
		playerIndex = int(playerIndexStr)
		drawPlayerIndex = [playerIndex - 1]
	else:
		print("잘못된 입력입니다. 프로그램을 종료합니다.")
		sys.exit()
	
	return drawPlayerIndex

def getYearAndPlayerType ():
	"""연도 정보 및 타자 / 투수 선택 여부를 입력받아주는 함수
	   입력: 없음
	   출력: year(연도 정보), playerType(0: 투수, 1: 타자)
	"""

	#회사 선택
	year = input ('선수 정보를 볼 연도를 고르세요 (2012 ~ 2022) : ')
	if (year.isdigit() == False):
		print("잘못된 입력입니다. 프로그램을 종료합니다.")
		sys.exit()

	year = int(year)

	if (year < 2012 or year > 2022):
		print("잘못된 입력입니다. 프로그램을 종료합니다.")
		sys.exit()

	#추출할 종가의 날 수를 입력받는다.
	playerType = input ('정보를 볼 선수 분야를 선택하세요 (1: 투수, 2: 타자) : ')

	if (playerType.isdigit() == False):
		print("잘못된 입력입니다. 프로그램을 종료합니다.")
		sys.exit()

	playerType = int(playerType)

	if (playerType < 0 or playerType > 2) :
		print("잘못된 입력입니다. 프로그램을 종료합니다.")
		sys.exit()

	return year, playerType


"""***메인 프로그램: 주식 종가 추출 및 그리기***"""

year, playerType = getYearAndPlayerType() # 회사 선택

playerList, dataName = parsePlayerData(year, playerType) # 종가 추출

drawPlayerIndex = getDrawPlayerIndex(playerList)
print(playerList)
print(dataName)
print(drawPlayerIndex)
# drawGraph(pList) # 그리기

""" ***The End of Main*** """

