#!/usr/bin/env python3
# main.py: 해외주식 현재가 및 일별 시세를 조회하고, MACD와 일목균형표를 계산하여 출력하는 메인 스크립트
import os
import sys
import pandas as pd
from datetime import datetime, timedelta  # 과거 조회 기간 계산용
import time  # retry 대기를 위한 모듈
from zoneinfo import ZoneInfo  # 시간대 처리용

# kis_api 모듈을 사용할 수 있도록 src 디렉터리를 모듈 탐색 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from kis_api import kis_auth  # 인증 및 환경 설정 모듈
from kis_api.kis_ovrseastk import get_overseas_price_quot_price, get_overseas_price_quot_inquire_daily_chartprice, get_overseas_price_quot_inquire_time_itemchartprice  # 현재가, 일봉 및 인트라데이 조회 함수
from strategies.trading_conditions import compute_macd, compute_ichimoku, is_long_entry, is_short_entry  # MACD 및 일목균형표 계산 함수

def main():
    # main 함수: 고정 거래소 및 종목으로 지표 조회 흐름 실행
    # 거래소 코드와 심볼을 하드코딩 (필요 시 다른 값으로 변경)
    excd = "NAS"
    symb = "AAPL"

    # 인증 수행 (기본: 실전(prod) 환경)
    kis_auth.auth()

    # 현재 체결가(최근가) 조회
    df_current = get_overseas_price_quot_price(excd=excd, itm_no=symb)
    print(f"df_current: {df_current}")


if __name__ == "__main__":
    main()
