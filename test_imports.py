"""
Test script to validate all imports and basic functionality.
This tests the code structure WITHOUT making LLM API calls.
"""


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        import config
        print("✓ config.py imported successfully")
        print(f"  LLM_MODEL: {config.LLM_MODEL}")

        import utils
        print("✓ utils.py imported successfully")

        import data_tools
        print("✓ data_tools.py imported successfully")

        import agents
        print("✓ agents.py imported successfully")
        print(f"  AgentState defined: {agents.AgentState is not None}")

        import main
        print("✓ main.py imported successfully")

        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_fetch():
    """Test data fetching without LLM calls."""
    print("\nTesting data fetching (without LLM peer generation)...")

    try:
        from data_tools import _fetch_ticker_data
        import yfinance as yf

        # Test fetching a single ticker
        data = _fetch_ticker_data('AAPL')
        print(f"✓ Fetched data for AAPL:")
        print(f"  Price: ${data['price']}")
        print(f"  P/E: {data['pe']}")
        print(f"  PEG: {data['peg']}")
        print(f"  P/B: {data['pb']}")

        return True
    except Exception as e:
        print(f"✗ Data fetch error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_peer_comparison_calculation():
    """Test peer comparison calculation logic."""
    print("\nTesting peer comparison calculation...")

    try:
        from data_tools import calculate_peer_comparison

        # Create mock market data
        mock_data = {
            'main_ticker': {
                'ticker': 'AAPL',
                'price': 150.0,
                'market_cap': 2500000000000,
                'pe': 30.0,
                'peg': 2.5,
                'pb': 40.0
            },
            'peers': {
                'MSFT': {
                    'ticker': 'MSFT',
                    'price': 350.0,
                    'market_cap': 2600000000000,
                    'pe': 35.0,
                    'peg': 2.8,
                    'pb': 12.0
                },
                'GOOGL': {
                    'ticker': 'GOOGL',
                    'price': 140.0,
                    'market_cap': 1800000000000,
                    'pe': 25.0,
                    'peg': 1.8,
                    'pb': 5.0
                },
                'META': {
                    'ticker': 'META',
                    'price': 320.0,
                    'market_cap': 900000000000,
                    'pe': 28.0,
                    'peg': 2.0,
                    'pb': 6.0
                }
            },
            'peer_list': ['MSFT', 'GOOGL', 'META']
        }

        result = calculate_peer_comparison('AAPL', mock_data)
        print("✓ Peer comparison calculated successfully")
        print("\nSample output:")
        print(result[:300] + "...")

        return True
    except Exception as e:
        print(f"✗ Peer comparison error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_structure():
    """Test that the graph can be created (without executing)."""
    print("\nTesting graph structure...")

    try:
        from main import create_graph

        graph = create_graph()
        print("✓ Graph created successfully")
        print("  Nodes: research, fundamentalist, quant, strategist")
        print("  Architecture: Parallel execution (research → fundamentalist & quant → strategist)")

        return True
    except Exception as e:
        print(f"✗ Graph creation error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("CODE VALIDATION TEST SUITE")
    print("=" * 70)
    print()

    all_passed = True

    all_passed &= test_imports()
    all_passed &= test_data_fetch()
    all_passed &= test_peer_comparison_calculation()
    all_passed &= test_graph_structure()

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("\nThe code is ready to run.")
        print("Next step: Configure LLM (OpenAI API key or Ollama setup)")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease review the errors above.")
    print("=" * 70)
