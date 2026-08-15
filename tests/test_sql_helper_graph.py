from sql_helper_graph import SQLState, app, route_after_decision


def test_sql_graph_has_required_nodes():
    graph_nodes = list(app.get_graph().nodes.keys())

    assert "identify_tables" in graph_nodes
    assert "generate_sql_query" in graph_nodes
    assert "check_sql_risks" in graph_nodes
    assert "simple_sql_response" in graph_nodes
    assert "advanced_sql_response" in graph_nodes


def test_decision_routes_simple_and_advanced():
    simple_state = SQLState(is_advanced_query=False)
    advanced_state = SQLState(is_advanced_query=True)

    assert route_after_decision(simple_state) == "simple"
    assert route_after_decision(advanced_state) == "advanced"
