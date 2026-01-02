"""
Main orchestration file for the Equity Research Agent system.
Implements the parallel multi-agent architecture using LangGraph.
"""

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from agents import (
    AgentState,
    FUNDAMENTALIST_PROMPT,
    QUANT_PROMPT,
    STRATEGIST_PROMPT
)
from data_tools import fetch_market_data, calculate_peer_comparison
from utils import get_llm


# ============================================================================
# NODE DEFINITIONS
# ============================================================================

def research_node(state: AgentState) -> AgentState:
    """
    Fetch market data and perform peer comparison analysis.

    Args:
        state: Current agent state

    Returns:
        Updated state with market_data populated
    """
    ticker = state['ticker']
    print(f"\n[Research Node] Fetching data for {ticker}...")

    # Fetch market data
    market_data_dict = fetch_market_data(ticker)

    # Calculate peer comparison
    comparison = calculate_peer_comparison(ticker, market_data_dict)

    # Return only the updated field
    print(f"[Research Node] Data fetched successfully")

    return {'market_data': comparison}


def fundamentalist_node(state: AgentState) -> AgentState:
    """
    Run fundamental analysis using the fundamentalist agent.

    Args:
        state: Current agent state

    Returns:
        Updated state with fundamentalist_analysis populated
    """
    print(f"\n[Fundamentalist Agent] Analyzing {state['ticker']}...")

    llm = get_llm()

    # Construct the prompt
    prompt = f"""{FUNDAMENTALIST_PROMPT}

Here is the market data for {state['ticker']}:

{state['market_data']}

Provide your fundamental analysis:"""

    # Invoke LLM
    response = llm.invoke([HumanMessage(content=prompt)])

    # Return only the updated field
    print(f"[Fundamentalist Agent] Analysis complete")

    return {'fundamentalist_analysis': response.content}


def quant_node(state: AgentState) -> AgentState:
    """
    Run quantitative analysis using the quant agent.

    Args:
        state: Current agent state

    Returns:
        Updated state with quant_analysis populated
    """
    print(f"\n[Quant Agent] Analyzing {state['ticker']}...")

    llm = get_llm()

    # Construct the prompt
    prompt = f"""{QUANT_PROMPT}

Here is the peer comparison data for {state['ticker']}:

{state['market_data']}

Provide your quantitative analysis:"""

    # Invoke LLM
    response = llm.invoke([HumanMessage(content=prompt)])

    # Return only the updated field
    print(f"[Quant Agent] Analysis complete")

    return {'quant_analysis': response.content}


def strategist_node(state: AgentState) -> AgentState:
    """
    Synthesize analyses and produce final investment recommendation.

    Args:
        state: Current agent state

    Returns:
        Updated state with final_report populated
    """
    print(f"\n[Strategist Agent] Synthesizing final report for {state['ticker']}...")

    llm = get_llm()

    # Construct the prompt
    prompt = f"""{STRATEGIST_PROMPT}

You are analyzing: {state['ticker']}

=== FUNDAMENTAL ANALYST'S REPORT ===
{state['fundamentalist_analysis']}

=== QUANTITATIVE ANALYST'S REPORT ===
{state['quant_analysis']}

=== YOUR TASK ===
Synthesize the above analyses into a final investment memo with a clear BUY/SELL/HOLD recommendation.
"""

    # Invoke LLM
    response = llm.invoke([HumanMessage(content=prompt)])

    # Return only the updated field
    print(f"[Strategist Agent] Final report complete")

    return {'final_report': response.content}


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def create_graph():
    """
    Create the LangGraph workflow with parallel agent execution.

    Returns:
        Compiled graph ready for execution
    """
    # Initialize graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("fundamentalist", fundamentalist_node)
    workflow.add_node("quant", quant_node)
    workflow.add_node("strategist", strategist_node)

    # Define edges
    # Start -> research_node
    workflow.set_entry_point("research")

    # research_node -> PARALLEL fan-out to fundamentalist AND quant
    workflow.add_edge("research", "fundamentalist")
    workflow.add_edge("research", "quant")

    # Both fundamentalist and quant -> strategist (fan-in)
    workflow.add_edge("fundamentalist", "strategist")
    workflow.add_edge("quant", "strategist")

    # strategist -> END
    workflow.add_edge("strategist", END)

    # Compile and return
    return workflow.compile()


# ============================================================================
# CLI RUNNER
# ============================================================================

def run_analysis():
    """
    Interactive CLI for running stock analyses.
    Loops continuously until user exits.
    """
    print("=" * 70)
    print("🔬 ALGORITHMIC EQUITY RESEARCH AGENT")
    print("=" * 70)
    print("\nMulti-Agent Analysis System")
    print("- Fundamentalist: Value-focused conservative analysis")
    print("- Quant: Data-driven peer comparison")
    print("- Strategist: Synthesized investment recommendation")
    print("\n" + "=" * 70)

    # Create the graph once
    graph = create_graph()

    while True:
        print("\n" + "-" * 70)
        ticker = input("\nEnter stock ticker (or 'quit' to exit): ").strip().upper()

        if ticker in ['QUIT', 'EXIT', 'Q']:
            print("\n👋 Goodbye!")
            break

        if not ticker:
            print("⚠️  Please enter a valid ticker symbol")
            continue

        try:
            # Initialize state
            initial_state = {
                'ticker': ticker,
                'market_data': '',
                'fundamentalist_analysis': '',
                'quant_analysis': '',
                'final_report': ''
            }

            # Run the graph
            print(f"\n🚀 Starting analysis for {ticker}...")
            print("=" * 70)

            final_state = graph.invoke(initial_state)

            # Display final report
            print("\n" + "=" * 70)
            print("📊 FINAL INVESTMENT MEMO")
            print("=" * 70)
            print(f"\n{final_state['final_report']}")
            print("\n" + "=" * 70)

        except KeyboardInterrupt:
            print("\n\n⚠️  Analysis interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            print("Please try again with a different ticker")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    run_analysis()
