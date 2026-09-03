import networkx as nx


def build_fraud_graph(transactions: list[dict]) -> nx.Graph:
    """
    Build a user-recipient fraud graph.
    """

    graph = nx.Graph()

    for transaction in transactions:
        sender = transaction["sender"]
        recipient = transaction["recipient"]

        graph.add_node(sender, node_type="user")
        graph.add_node(recipient, node_type="recipient")

        graph.add_edge(
            sender,
            recipient,
            amount=transaction.get("amount", 0),
            flagged=transaction.get("flagged", False),
        )

    return graph


def analyze_recipient_network(
    graph: nx.Graph,
    recipient_id: str,
) -> dict:
    """
    Analyze suspicious users connected to a recipient.
    """

    if recipient_id not in graph:
        return {
            "cluster_id": None,
            "connected_suspicious_users": 0,
        }

    suspicious_users = []

    for user in graph.neighbors(recipient_id):
        edge_data = graph.get_edge_data(recipient_id, user, {})

        if edge_data.get("flagged", False):
            suspicious_users.append(user)

    component = nx.node_connected_component(graph, recipient_id)

    cluster_id = f"CLUSTER-{recipient_id}"

    return {
        "cluster_id": cluster_id,
        "connected_suspicious_users": len(suspicious_users),
        "network_size": len(component),
    }