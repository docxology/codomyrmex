from codomyrmex.data_visualization.charts.pie_chart import PieChart

from .policy import PolicyEngine


def plot_policy_compliance(engine: PolicyEngine) -> str:
    """
    Renders a pie chart of policy compliance (pass vs fail).
    """
    labels = ["Pass", "Fail"]
    # Mock data for demonstration as we don't have historical logs in the basic engine yet
    data = [85, 15]

    chart = PieChart(
        title="Policy Compliance Rate",
        labels=labels,
        sizes=data
    )
    return chart.render()
