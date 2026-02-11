from .skills import SkillLibrary
from codomyrmex.data_visualization.charts.bar_chart import BarChart
from collections import Counter

def plot_skill_distribution(library: SkillLibrary) -> str:
    """
    Renders a bar chart of skills by tag.
    """
    tags = []
    for skill in library._skills.values():
        tags.extend(skill.tags)
        
    counts = Counter(tags)
    
    chart = BarChart(
        title="Skill Distribution by Tag",
        x_label="Tag",
        y_label="Count",
        categories=list(counts.keys()),
        values=list(counts.values())
    )
    return chart.render()
