#!/bin/bash
# 🐜 Codomyrmex Data Visualization Demo
# 
# This script demonstrates Codomyrmex's data visualization capabilities by:
# 1. Creating various types of charts and plots
# 2. Showing different visualization formats and options
# 3. Demonstrating integration with data analysis workflows
#
# Prerequisites: None (all dependencies handled automatically)
# Duration: ~3 minutes
# Output: Generated plots in examples/output/data-visualization/

set -e  # Exit on any error

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/examples/output/data-visualization"
DEMO_START_TIME=$(date +%s)

# Parse command line arguments
INTERACTIVE=true
for arg in "$@"; do
    case $arg in
        --non-interactive)
            INTERACTIVE=false
            ;;
        --help)
            echo "Usage: $0 [--non-interactive] [--help]"
            echo "  --non-interactive  Run without user prompts"
            echo "  --help            Show this help message"
            exit 0
            ;;
    esac
done

# Helper functions
log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "\n${BLUE}🔹 $1${NC}"
}

pause_for_user() {
    echo -e "${YELLOW}💡 $1${NC}"
    if [ "$INTERACTIVE" = true ]; then
        read -p "Press Enter to continue..."
    else
        echo -e "${CYAN}[Non-interactive mode: Continuing automatically...]${NC}"
        sleep 1
    fi
}

show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🐜 CODOMYRMEX DATA VISUALIZATION DEMO 🐜                    ║
║   Demonstrating Charts, Plots, and Data Analysis              ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

check_environment() {
    log_step "Environment Setup & Validation"
    
    # Check if we're in the right location
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]] || [[ ! -d "$PROJECT_ROOT/src/codomyrmex" ]]; then
        log_error "Not in Codomyrmex project root. Please run from examples/basic/"
        exit 1
    fi
    
    # Check Python environment
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.10+"
        exit 1
    fi
    
    # Activate virtual environment if available
    if [[ -f "$PROJECT_ROOT/.venv/bin/activate" ]]; then
        log_info "Activating virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
    
    # Test Codomyrmex import
    log_info "Checking Codomyrmex installation..."
    if ! python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT/src'); from codomyrmex.data_visualization import create_line_plot" 2>/dev/null; then
        log_error "Codomyrmex data visualization module not available. Please run: pip install -e ."
        exit 1
    fi
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    log_success "Environment ready!"
}

generate_sample_data() {
    log_step "Generating Sample Data"
    
    log_info "Creating sample datasets for demonstration..."
    
    # Create Python script to generate sample data
    cat > "$OUTPUT_DIR/generate_data.py" << 'EOF'
import numpy as np
import json
import sys
import os

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def generate_datasets():
    """Generate various sample datasets for visualization demos"""
    
    # Time series data
    time_points = np.linspace(0, 10, 100)
    sin_wave = np.sin(time_points)
    cos_wave = np.cos(time_points)
    noisy_data = sin_wave + np.random.normal(0, 0.1, len(sin_wave))
    
    # Sales data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    sales_2023 = [12000, 15000, 18000, 22000, 28000, 32000,
                  35000, 38000, 31000, 28000, 25000, 40000]
    sales_2024 = [15000, 18000, 21000, 26000, 31000, 36000,
                  39000, 42000, 38000, 35000, 32000, 45000]
    
    # Survey data
    satisfaction_scores = np.random.normal(7.5, 1.5, 500)
    satisfaction_scores = np.clip(satisfaction_scores, 1, 10)
    
    # Performance metrics
    languages = ['Python', 'JavaScript', 'Java', 'C++', 'Go', 'Rust']
    performance = [85, 78, 72, 95, 88, 92]
    
    # Scatter plot data - relationship between study hours and test scores
    study_hours = np.random.uniform(0, 10, 50)
    test_scores = 60 + 3 * study_hours + np.random.normal(0, 5, 50)
    test_scores = np.clip(test_scores, 0, 100)
    
    return {
        'time_series': {
            'time_points': time_points.tolist(),
            'sin_wave': sin_wave.tolist(),
            'cos_wave': cos_wave.tolist(),
            'noisy_data': noisy_data.tolist()
        },
        'sales': {
            'months': months,
            'sales_2023': sales_2023,
            'sales_2024': sales_2024
        },
        'satisfaction': satisfaction_scores.tolist(),
        'performance': {
            'languages': languages,
            'scores': performance
        },
        'scatter': {
            'study_hours': study_hours.tolist(),
            'test_scores': test_scores.tolist()
        }
    }

if __name__ == '__main__':
    datasets = generate_datasets()
    with open('sample_data.json', 'w') as f:
        json.dump(datasets, f, indent=2)
    print("Sample datasets generated successfully!")
EOF

    # Generate the data
    cd "$OUTPUT_DIR"
    python3 generate_data.py
    log_success "Sample data generated!"
}

demo_line_plots() {
    log_step "Creating Line Plots"
    
    pause_for_user "We'll create line plots showing time series data (sine/cosine waves)"
    
    # Create line plot demonstration
    cat > "$OUTPUT_DIR/line_plot_demo.py" << 'EOF'
import json
import sys
import os

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.data_visualization import create_line_plot

# Load sample data
with open('sample_data.json', 'r') as f:
    data = json.load(f)

time_series = data['time_series']

print("📊 Creating line plots...")

# 1. Simple sine wave
create_line_plot(
    x_data=time_series['time_points'],
    y_data=time_series['sin_wave'],
    title="Sine Wave Demonstration",
    x_label="Time (seconds)",
    y_label="Amplitude",
    output_path="sine_wave.png",
    show_plot=False,
    markers=False
)
print("✅ Created sine_wave.png")

# 2. Multiple lines on same plot
create_line_plot(
    x_data=time_series['time_points'],
    y_data=[time_series['sin_wave'], time_series['cos_wave'], time_series['noisy_data']],
    title="Trigonometric Functions Comparison",
    x_label="Time (seconds)", 
    y_label="Amplitude",
    line_labels=["sin(x)", "cos(x)", "sin(x) + noise"],
    output_path="trig_comparison.png",
    show_plot=False,
    markers=True,
    figure_size=(12, 6)
)
print("✅ Created trig_comparison.png")

# 3. Sales trend analysis
sales = data['sales']
create_line_plot(
    x_data=list(range(len(sales['months']))),
    y_data=[sales['sales_2023'], sales['sales_2024']],
    title="Monthly Sales Comparison (2023 vs 2024)",
    x_label="Month",
    y_label="Sales ($)",
    line_labels=["2023", "2024"],
    output_path="sales_trend.png",
    show_plot=False,
    markers=True,
    figure_size=(10, 6)
)
print("✅ Created sales_trend.png")

print("🎉 Line plot demonstrations completed!")
EOF

    cd "$OUTPUT_DIR"
    python3 line_plot_demo.py
    
    log_success "Line plots created!"
    log_info "Generated files: sine_wave.png, trig_comparison.png, sales_trend.png"
}

demo_bar_charts() {
    log_step "Creating Bar Charts"
    
    pause_for_user "We'll create bar charts showing categorical data and comparisons"
    
    cat > "$OUTPUT_DIR/bar_chart_demo.py" << 'EOF'
import json
import sys
import os

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.data_visualization import create_bar_chart

# Load sample data
with open('sample_data.json', 'r') as f:
    data = json.load(f)

print("📊 Creating bar charts...")

# 1. Programming language performance
performance = data['performance']
create_bar_chart(
    categories=performance['languages'],
    values=performance['scores'],
    title="Programming Language Performance Comparison",
    x_label="Programming Language",
    y_label="Performance Score",
    output_path="language_performance.png",
    show_plot=False,
    bar_color="skyblue"
)
print("✅ Created language_performance.png")

# 2. Horizontal bar chart
create_bar_chart(
    categories=performance['languages'],
    values=performance['scores'],
    title="Programming Language Performance (Horizontal)",
    x_label="Performance Score",
    y_label="Programming Language", 
    output_path="language_performance_horizontal.png",
    show_plot=False,
    horizontal=True,
    bar_color="lightgreen"
)
print("✅ Created language_performance_horizontal.png")

# 3. Monthly sales bar chart
sales = data['sales']
create_bar_chart(
    categories=sales['months'],
    values=sales['sales_2024'],
    title="2024 Monthly Sales Performance",
    x_label="Month",
    y_label="Sales ($)",
    output_path="monthly_sales_2024.png",
    show_plot=False,
    bar_color="orange"
)
print("✅ Created monthly_sales_2024.png")

print("🎉 Bar chart demonstrations completed!")
EOF

    cd "$OUTPUT_DIR"
    python3 bar_chart_demo.py
    
    log_success "Bar charts created!"
    log_info "Generated files: language_performance.png, language_performance_horizontal.png, monthly_sales_2024.png"
}

demo_scatter_plots() {
    log_step "Creating Scatter Plots"
    
    pause_for_user "We'll create scatter plots showing relationships between variables"
    
    cat > "$OUTPUT_DIR/scatter_plot_demo.py" << 'EOF'
import json
import sys
import os

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.data_visualization import create_scatter_plot

# Load sample data
with open('sample_data.json', 'r') as f:
    data = json.load(f)

print("📊 Creating scatter plots...")

# 1. Study hours vs test scores relationship
scatter = data['scatter']
create_scatter_plot(
    x_data=scatter['study_hours'],
    y_data=scatter['test_scores'],
    title="Study Hours vs Test Scores Correlation",
    x_label="Study Hours per Week",
    y_label="Test Score (%)",
    output_path="study_correlation.png",
    show_plot=False,
    dot_size=50,
    dot_color="blue",
    alpha=0.7
)
print("✅ Created study_correlation.png")

# 2. Different styling
create_scatter_plot(
    x_data=scatter['study_hours'],
    y_data=scatter['test_scores'],
    title="Study Hours vs Test Scores (Styled)",
    x_label="Study Hours per Week",
    y_label="Test Score (%)",
    output_path="study_correlation_styled.png",
    show_plot=False,
    dot_size=30,
    dot_color="red",
    alpha=0.6
)
print("✅ Created study_correlation_styled.png")

print("🎉 Scatter plot demonstrations completed!")
EOF

    cd "$OUTPUT_DIR"
    python3 scatter_plot_demo.py
    
    log_success "Scatter plots created!"
    log_info "Generated files: study_correlation.png, study_correlation_styled.png"
}

demo_histograms() {
    log_step "Creating Histograms"
    
    pause_for_user "We'll create histograms showing data distributions"
    
    cat > "$OUTPUT_DIR/histogram_demo.py" << 'EOF'
import json
import sys
import os

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.data_visualization import create_histogram

# Load sample data
with open('sample_data.json', 'r') as f:
    data = json.load(f)

print("📊 Creating histograms...")

# Satisfaction scores distribution
satisfaction = data['satisfaction']
create_histogram(
    data=satisfaction,
    bins=20,
    title="Customer Satisfaction Score Distribution",
    x_label="Satisfaction Score (1-10)",
    y_label="Number of Responses",
    output_path="satisfaction_distribution.png",
    show_plot=False,
    hist_color="lightblue",
    edge_color="navy"
)
print("✅ Created satisfaction_distribution.png")

# Different binning
create_histogram(
    data=satisfaction,
    bins=10,
    title="Customer Satisfaction Score Distribution (10 bins)",
    x_label="Satisfaction Score (1-10)",
    y_label="Number of Responses",
    output_path="satisfaction_distribution_10bins.png",
    show_plot=False,
    hist_color="lightgreen",
    edge_color="darkgreen"
)
print("✅ Created satisfaction_distribution_10bins.png")

print("🎉 Histogram demonstrations completed!")
EOF

    cd "$OUTPUT_DIR"
    python3 histogram_demo.py
    
    log_success "Histograms created!"
    log_info "Generated files: satisfaction_distribution.png, satisfaction_distribution_10bins.png"
}

demo_pie_charts() {
    log_step "Creating Pie Charts"
    
    pause_for_user "We'll create pie charts showing proportional data"
    
    cat > "$OUTPUT_DIR/pie_chart_demo.py" << 'EOF'
import json
import sys
import os

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.data_visualization import create_pie_chart

print("📊 Creating pie charts...")

# Technology stack usage
technologies = ["Python", "JavaScript", "Java", "C++", "Go", "Other"]
usage_percentage = [35, 25, 20, 10, 5, 5]

create_pie_chart(
    labels=technologies,
    sizes=usage_percentage,
    title="Technology Stack Usage Distribution",
    output_path="technology_distribution.png",
    show_plot=False,
    autopct='%1.1f%%',
    startangle=90
)
print("✅ Created technology_distribution.png")

# Market share with exploded slice
market_share = ["Product A", "Product B", "Product C", "Product D"]
shares = [40, 30, 20, 10]
explode = [0.1, 0, 0, 0]  # Explode first slice

create_pie_chart(
    labels=market_share,
    sizes=shares,
    title="Market Share Analysis",
    output_path="market_share.png",
    show_plot=False,
    autopct='%1.1f%%',
    startangle=45,
    explode=explode
)
print("✅ Created market_share.png")

print("🎉 Pie chart demonstrations completed!")
EOF

    cd "$OUTPUT_DIR"
    python3 pie_chart_demo.py
    
    log_success "Pie charts created!"
    log_info "Generated files: technology_distribution.png, market_share.png"
}

show_results() {
    log_step "Demonstration Results"
    
    log_info "All visualizations have been created! Here's what was generated:"
    
    echo -e "${WHITE}📁 Output Directory: $OUTPUT_DIR${NC}"
    echo ""
    
    # Count and list generated files
    cd "$OUTPUT_DIR"
    plot_files=(*.png)
    if [ ${#plot_files[@]} -gt 0 ] && [ "${plot_files[0]}" != "*.png" ]; then
        echo -e "${GREEN}🎨 Generated Visualizations (${#plot_files[@]} files):${NC}"
        for file in "${plot_files[@]}"; do
            if [[ -f "$file" ]]; then
                size=$(du -h "$file" | cut -f1)
                echo -e "   📈 ${file} (${size})"
            fi
        done
    else
        log_warning "No plot files found. Something may have gone wrong."
        return 1
    fi
    
    echo ""
    log_info "You can view these files using:"
    echo -e "${CYAN}   # Open the directory in your file browser${NC}"
    echo -e "${CYAN}   open '$OUTPUT_DIR'  # macOS${NC}"
    echo -e "${CYAN}   xdg-open '$OUTPUT_DIR'  # Linux${NC}"
    echo -e "${CYAN}   explorer '$OUTPUT_DIR'  # Windows${NC}"
    
    echo ""
    echo -e "${CYAN}   # Or view individual files${NC}"
    echo -e "${CYAN}   open '$OUTPUT_DIR/trig_comparison.png'${NC}"
    
    return 0
}

demo_integration_example() {
    log_step "Integration Example: Data Analysis + Visualization"
    
    pause_for_user "Let's see how data visualization integrates with other Codomyrmex modules"
    
    cat > "$OUTPUT_DIR/integration_demo.py" << 'EOF'
import json
import sys
import os
import numpy as np

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.data_visualization import create_line_plot, create_bar_chart
from codomyrmex.logging_monitoring import get_logger

# Initialize logging
logger = get_logger(__name__)

print("🔗 Demonstrating integration with other Codomyrmex modules...")

# Load data
with open('sample_data.json', 'r') as f:
    data = json.load(f)

# Simulate data analysis (would normally use pattern_matching or static_analysis modules)
logger.info("Analyzing performance data across programming languages")

performance = data['performance']
languages = performance['languages']  
scores = performance['scores']

# Analysis: calculate statistics
mean_score = np.mean(scores)
max_score = max(scores)
min_score = min(scores)
best_language = languages[scores.index(max_score)]

logger.info(f"Analysis complete: Best performer is {best_language} with score {max_score}")

# Create analysis summary visualization
analysis_results = {
    'metrics': ['Mean', 'Maximum', 'Minimum'],
    'values': [mean_score, max_score, min_score]
}

create_bar_chart(
    categories=analysis_results['metrics'],
    values=analysis_results['values'],
    title="Performance Analysis Summary",
    x_label="Metric",
    y_label="Score",
    output_path="analysis_summary.png",
    show_plot=False,
    bar_color="purple"
)

logger.info("Created analysis summary visualization")

# Create detailed comparison with annotations
create_line_plot(
    x_data=list(range(len(languages))),
    y_data=scores,
    title=f"Language Performance Analysis (Best: {best_language})",
    x_label="Language Index",
    y_label="Performance Score",
    output_path="detailed_analysis.png",
    show_plot=False,
    markers=True,
    figure_size=(10, 6)
)

logger.info("Integration demonstration completed successfully")
print("✅ Created analysis_summary.png")
print("✅ Created detailed_analysis.png")
print("🎉 Integration example completed!")
EOF

    cd "$OUTPUT_DIR"
    python3 integration_demo.py
    
    log_success "Integration example completed!"
    log_info "This shows how visualization works with logging and data analysis workflows"
}

show_summary() {
    log_step "Demo Summary & Next Steps"
    
    # Calculate demo duration
    demo_end_time=$(date +%s)
    demo_duration=$((demo_end_time - demo_start_time))
    
    echo -e "${GREEN}🎉 Data Visualization Demo Complete!${NC}"
    echo ""
    echo -e "${WHITE}📊 What You've Learned:${NC}"
    echo "   ✅ Created line plots for time series data"
    echo "   ✅ Built bar charts for categorical comparisons"  
    echo "   ✅ Made scatter plots showing correlations"
    echo "   ✅ Generated histograms for distribution analysis"
    echo "   ✅ Designed pie charts for proportional data"
    echo "   ✅ Saw integration with other Codomyrmex modules"
    
    echo ""
    echo -e "${WHITE}📁 Generated Files:${NC}"
    cd "$OUTPUT_DIR"
    ls -la *.png 2>/dev/null | wc -l | xargs echo "   📈 Total plots created:"
    
    echo ""
    echo -e "${WHITE}⏱️  Demo Statistics:${NC}"
    echo "   🕒 Duration: ${demo_duration} seconds"
    echo "   🎯 Modules demonstrated: data_visualization, logging_monitoring"
    echo "   📦 Output location: $OUTPUT_DIR"
    
    echo ""
    echo -e "${YELLOW}🚀 Next Steps:${NC}"
    echo "   1. Explore the generated visualizations"
    echo "   2. Try modifying the demo scripts with your own data"
    echo "   3. Run other examples: cd ../integration"
    echo "   4. Check out the documentation: docs/modules/data_visualization/"
    echo "   5. Try the AI-enhanced analysis example: ../integration/ai-enhanced-analysis.sh"
    
    echo ""
    echo -e "${CYAN}💡 Pro Tips:${NC}"
    echo "   • Use different color schemes and styling options"
    echo "   • Combine multiple plot types for comprehensive analysis"
    echo "   • Integrate with static analysis for code metrics visualization"
    echo "   • Export to different formats (SVG, PDF) for presentations"
    
    echo ""
    echo -e "${GREEN}✨ Happy visualizing with Codomyrmex! ✨${NC}"
}

cleanup_option() {
    echo ""
    if [ "$INTERACTIVE" = true ]; then
        read -p "🧹 Would you like to clean up the generated files? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cleaning up generated files..."
            rm -f "$OUTPUT_DIR"/*.png
            rm -f "$OUTPUT_DIR"/*.py
            rm -f "$OUTPUT_DIR"/*.json
            log_success "Cleanup completed!"
        else
            log_info "Files preserved for your exploration"
        fi
    else
        log_info "Non-interactive mode: Files preserved for your exploration"
        log_info "Generated files located in: $OUTPUT_DIR"
    fi
}

# Error handling
handle_error() {
    log_error "Demo encountered an error on line $1"
    log_info "You can find partial results in: $OUTPUT_DIR"
    log_info "Check the logs above for details"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Main execution
main() {
    show_header
    
    log_info "This demo will showcase Codomyrmex's data visualization capabilities"
    log_info "We'll create various plots and charts using sample data"
    log_info "Duration: ~3 minutes | Output: examples/output/data-visualization/"
    
    pause_for_user "Ready to start the data visualization demo?"
    
    check_environment
    generate_sample_data
    demo_line_plots
    demo_bar_charts
    demo_scatter_plots
    demo_histograms
    demo_pie_charts
    demo_integration_example
    
    if show_results; then
        show_summary
        cleanup_option
    else
        log_error "Demo completed with some issues. Check the output directory for partial results."
        exit 1
    fi
}

# Run the demo
main "$@"
