"""
Simple test script to validate yfinance connectivity and data fetching.
Run this BEFORE running the full system to ensure data access works.
"""

import yfinance as yf


def test_basic_fetch():
    """Test basic ticker data fetching."""
    print("Testing yfinance basic fetch...")

    try:
        # Test with a well-known ticker
        ticker = 'AAPL'
        stock = yf.Ticker(ticker)
        info = stock.info

        # Check if we got data
        price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        market_cap = info.get('marketCap', 0)

        print(f"✓ Successfully fetched data for {ticker}")
        print(f"  Price: ${price}")
        print(f"  Market Cap: ${market_cap:,}")

        # Check key metrics
        pe = info.get('trailingPE') or info.get('forwardPE')
        peg = info.get('pegRatio')
        pb = info.get('priceToBook')

        print(f"  P/E Ratio: {pe}")
        print(f"  PEG Ratio: {peg}")
        print(f"  P/B Ratio: {pb}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_multiple_tickers():
    """Test fetching data for multiple tickers."""
    print("\nTesting multiple ticker fetch...")

    tickers = ['AAPL', 'MSFT', 'GOOGL']

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            print(f"✓ {ticker}: ${price}")
        except Exception as e:
            print(f"✗ {ticker}: Error - {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("YFINANCE CONNECTIVITY TEST")
    print("=" * 60)
    print()

    success = test_basic_fetch()

    if success:
        test_multiple_tickers()
        print("\n" + "=" * 60)
        print("✓ All tests passed! yfinance is working correctly.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ Tests failed. Please check your internet connection")
        print("  and ensure yfinance is properly installed.")
        print("=" * 60)
