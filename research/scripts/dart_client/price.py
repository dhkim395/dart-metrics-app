"""
종목 주가 데이터를 가져온다.
"""
from datetime import datetime, timedelta


def get_current_price(stock_code: str) -> dict:
    """
    종목코드(KRX 6자리)로 최근 종가를 가져온다.
    
    Args:
        stock_code: KRX 종목코드 (6자리, 예: "005930")
    
    Returns:
        dict: stock_code, date, close, volume
        실패 시 {"error": "..."}
    """
    try:
        import FinanceDataReader as fdr
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        df = fdr.DataReader(stock_code, start=start_date, end=end_date)
        
        if df.empty:
            return {"error": "주가 데이터 없음", "stock_code": stock_code}
        
        latest = df.iloc[-1]
        return {
            "stock_code": stock_code,
            "date": df.index[-1].strftime("%Y-%m-%d"),
            "close": int(latest["Close"]),
            "volume": int(latest.get("Volume", 0)),
        }
    except Exception as e:
        return {"error": str(e), "stock_code": stock_code}