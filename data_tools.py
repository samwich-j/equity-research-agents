"""
Data fetching and analysis tools for the Equity Research Agent system.
Implements yfinance best practices with rate-limited sessions.
"""

import time
import yfinance as yf
from datetime import datetime, timedelta
from utils import get_llm
from langchain_core.messages import HumanMessage

# Import rate limiting components
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter


# Create a rate-limited session class
class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    """Session with caching and rate limiting to avoid Yahoo Finance blocks."""
    pass


# Create global session with strict rate limiting
# Max 2 requests per 5 seconds (Yahoo Finance recommended limit)
_session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND * 5)),
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)


def get_peers(ticker: str) -> list[str]:
    """
    Use LLM to generate a list of 3 competitor tickers for the given ticker.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        List of 3 competitor ticker symbols

    Example:
        >>> get_peers('AAPL')
        ['MSFT', 'GOOGL', 'META']
    """
    llm = get_llm()

    prompt = f"""You are a financial analyst. Given the stock ticker '{ticker}',
return ONLY a Python list of exactly 3 competitor ticker symbols.
Return ONLY the list, nothing else. Format: ['TICKER1', 'TICKER2', 'TICKER3']

Example for AAPL: ['MSFT', 'GOOGL', 'META']

Now provide 3 competitors for {ticker}:"""

    response = llm.invoke([HumanMessage(content=prompt)])

    # Parse the response - it should be a string representation of a list
    try:
        # Clean the response and evaluate as Python literal
        peers_str = response.content.strip()
        # Use eval safely since we expect a list format
        peers = eval(peers_str)

        # Validate we got a list of 3 strings
        if isinstance(peers, list) and len(peers) == 3:
            return [str(p).upper() for p in peers]
        else:
            # Fallback: try to extract tickers from response
            raise ValueError("Invalid peer format")
    except:
        # Fallback: return some generic large-cap tech stocks
        print(f"Warning: Could not parse peers for {ticker}, using fallback")
        return ['SPY', 'QQQ', 'DIA']  # Market ETFs as safe fallback


def fetch_market_data(ticker: str) -> dict:
    """
    Fetch key financial metrics for a ticker and its peers using yfinance.
    Uses generous delays between requests to avoid 429 errors.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Dictionary containing:
            - main_ticker: dict with price, market_cap, pe, peg, pb
            - peers: dict of peer_ticker -> metrics
            - peer_list: list of peer tickers

    Example:
        >>> data = fetch_market_data('AAPL')
        >>> data['main_ticker']['price']
        150.25
    """
    # Get peer tickers
    peers = get_peers(ticker)

    # Combine main ticker and peers
    all_tickers = [ticker] + peers

    print(f"Fetching data for {ticker} and peers: {', '.join(peers)}")
    print("Using conservative rate limiting (15 second delay between requests)...")

    # Fetch data with generous delays
    results = {}
    for idx, t in enumerate(all_tickers):
        print(f"  Fetching {t}...", end=" ", flush=True)
        try:
            # Let yfinance handle its own session (no custom session parameter)
            ticker_obj = yf.Ticker(t)
            info = ticker_obj.info
            results[t] = _parse_ticker_info(t, info)
            print("✓")

            # Add generous delay between requests (skip delay after last ticker)
            if idx < len(all_tickers) - 1:
                print(f"  Waiting 15 seconds before next request...", end=" ", flush=True)
                time.sleep(15)
                print("✓")
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"\n  ⚠️  Rate limited on {t}. Waiting 120 seconds...")
                time.sleep(120)
                # Retry once after waiting
                try:
                    ticker_obj = yf.Ticker(t)
                    info = ticker_obj.info
                    results[t] = _parse_ticker_info(t, info)
                    print("  ✓ Retry successful")
                except:
                    print(f"  ✗ Failed after retry")
                    results[t] = _get_empty_ticker_data(t)
            else:
                print(f"✗ Error: {e}")
                results[t] = _get_empty_ticker_data(t)

    # Organize results
    main_data = results.get(ticker, _get_empty_ticker_data(ticker))
    peer_data = {p: results.get(p, _get_empty_ticker_data(p)) for p in peers}

    return {
        'main_ticker': main_data,
        'peers': peer_data,
        'peer_list': peers
    }


def _parse_ticker_info(ticker: str, info: dict) -> dict:
    """
    Parse yfinance info dict into our standard format.

    Args:
        ticker: Stock ticker symbol
        info: yfinance info dictionary

    Returns:
        Dictionary with price, market_cap, pe, peg, pb
    """
    # Get current price
    price = info.get('currentPrice') or info.get('regularMarketPrice', 0)

    # Get key metrics (handle None values)
    market_cap = info.get('marketCap', 0)
    pe_ratio = info.get('trailingPE') or info.get('forwardPE')
    peg_ratio = info.get('pegRatio')
    pb_ratio = info.get('priceToBook')

    return {
        'ticker': ticker,
        'price': round(price, 2) if price else 0,
        'market_cap': market_cap,
        'pe': round(pe_ratio, 2) if pe_ratio else None,
        'peg': round(peg_ratio, 2) if peg_ratio else None,
        'pb': round(pb_ratio, 2) if pb_ratio else None
    }


def _get_empty_ticker_data(ticker: str) -> dict:
    """Return empty ticker data structure for error cases."""
    return {
        'ticker': ticker,
        'price': 0,
        'market_cap': 0,
        'pe': None,
        'peg': None,
        'pb': None,
        'error': 'Data unavailable'
    }


def calculate_peer_comparison(ticker: str, market_data: dict) -> str:
    """
    Calculate how the main ticker compares to peer group averages.

    Args:
        ticker: Main stock ticker symbol
        market_data: Output from fetch_market_data()

    Returns:
        Formatted string summary of peer comparison analysis
    """
    main = market_data['main_ticker']
    peers = market_data['peers']
    peer_list = market_data['peer_list']

    # Calculate peer averages (excluding None values)
    pe_values = [p['pe'] for p in peers.values() if p['pe'] is not None]
    peg_values = [p['peg'] for p in peers.values() if p['peg'] is not None]
    pb_values = [p['pb'] for p in peers.values() if p['pb'] is not None]

    avg_pe = sum(pe_values) / len(pe_values) if pe_values else None
    avg_peg = sum(peg_values) / len(peg_values) if peg_values else None
    avg_pb = sum(pb_values) / len(pb_values) if pb_values else None

    # Build comparison summary
    summary_lines = [
        f"=" * 60,
        f"PEER COMPARISON ANALYSIS FOR {ticker}",
        f"=" * 60,
        f"",
        f"Main Ticker: {ticker}",
        f"Price: ${main['price']}",
        f"Market Cap: ${main['market_cap']:,}",
        f"",
        f"Peer Group: {', '.join(peer_list)}",
        f"",
        f"--- VALUATION METRICS ---",
        f""
    ]

    # P/E Comparison
    if main['pe'] and avg_pe:
        pe_diff = ((main['pe'] - avg_pe) / avg_pe) * 100
        summary_lines.append(f"P/E Ratio:")
        summary_lines.append(f"  {ticker}: {main['pe']}")
        summary_lines.append(f"  Peer Avg: {avg_pe:.2f}")
        summary_lines.append(f"  Difference: {pe_diff:+.1f}% {'(PREMIUM)' if pe_diff > 0 else '(DISCOUNT)'}")
        summary_lines.append(f"")
    else:
        summary_lines.append(f"P/E Ratio: Data not available")
        summary_lines.append(f"")

    # PEG Comparison
    if main['peg'] and avg_peg:
        peg_diff = ((main['peg'] - avg_peg) / avg_peg) * 100
        summary_lines.append(f"PEG Ratio:")
        summary_lines.append(f"  {ticker}: {main['peg']}")
        summary_lines.append(f"  Peer Avg: {avg_peg:.2f}")
        summary_lines.append(f"  Difference: {peg_diff:+.1f}% {'(PREMIUM)' if peg_diff > 0 else '(DISCOUNT)'}")
        summary_lines.append(f"")
    else:
        summary_lines.append(f"PEG Ratio: Data not available")
        summary_lines.append(f"")

    # P/B Comparison
    if main['pb'] and avg_pb:
        pb_diff = ((main['pb'] - avg_pb) / avg_pb) * 100
        summary_lines.append(f"Price-to-Book Ratio:")
        summary_lines.append(f"  {ticker}: {main['pb']}")
        summary_lines.append(f"  Peer Avg: {avg_pb:.2f}")
        summary_lines.append(f"  Difference: {pb_diff:+.1f}% {'(PREMIUM)' if pb_diff > 0 else '(DISCOUNT)'}")
        summary_lines.append(f"")
    else:
        summary_lines.append(f"Price-to-Book Ratio: Data not available")
        summary_lines.append(f"")

    summary_lines.append(f"=" * 60)

    return "\n".join(summary_lines)
