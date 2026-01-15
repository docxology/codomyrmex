# Data Visualization - Tutorial: Generating a Heatmap via MCP

This tutorial will guide you through generating a heatmap using the Data Visualization module's `create_heatmap` Model Context Protocol (MCP) tool.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Data Visualization module installed and its dependencies (`matplotlib`, `seaborn`, `numpy`) available in your Python environment. (See main [README.md](../../README.md) and `data_visualization/requirements.txt`).
- Your Codomyrmex project environment set up, with logging initialized (`logging_monitoring`) and capable of making MCP tool calls.
- An output directory (e.g., `./mcp_plots/`) created and writable by the application running the MCP server.
- Familiarity with JSON format for MCP requests.

## 2. Goal

By the end of this tutorial, you will be able to:

- Construct a valid JSON request to call the `create_heatmap` MCP tool.
- Understand the key input parameters for generating a heatmap, such as `data`, `x_labels`, `y_labels`, `title`, and `output_path`.
- Interpret the MCP response to confirm successful plot generation and locate the output file.

## 3. Steps

### Step 1: Prepare Your MCP Request

We will create a heatmap for a small 2D dataset representing, for example, monthly sales for different products.

**MCP Request (save as `heatmap_request.json` or similar):**
```json
{
  "tool_name": "create_heatmap",
  "arguments": {
    "data": [
      [10, 25, 30, 22],
      [15, 5, 40, 35],
      [20, 30, 10, 18]
    ],
    "x_labels": ["Jan", "Feb", "Mar", "Apr"],
    "y_labels": ["Product A", "Product B", "Product C"],
    "title": "Monthly Sales Heatmap (MCP)",
    "x_label": "Month",
    "y_label": "Product",
    "output_path": "./mcp_plots/sales_heatmap.png",
    "annot": true,
    "cmap": "YlGnBu",
    "colorbar_label": "Sales Units",
    "figure_size": [8, 5]
  }
}
```

**Explanation of Key Arguments:**
- `data`: A 2D array (list of lists) of numerical values.
- `x_labels`: Labels for the columns (X-axis).
- `y_labels`: Labels for the rows (Y-axis).
- `title`, `x_label`, `y_label`: Descriptive text for the plot.
- `output_path`: Crucial for saving the plot. Ensure the directory (`./mcp_plots/` in this case) exists and is writable by the server process.
- `annot`: If `true`, will write the data value in each cell.
- `cmap`: Specifies the Matplotlib colormap (e.g., "YlGnBu", "viridis", "coolwarm").
- `colorbar_label`: Label for the color intensity scale.
- `figure_size`: Optional, `[width, height]` in inches.

### Step 2: Invoke the `create_heatmap` MCP Tool

Use your Codomyrmex MCP client to send the request. The exact command will depend on your client implementation.

**Using a hypothetical MCP client command:**
```bash
# Ensure ./mcp_plots directory exists and is writable by the server
# mkdir -p ./mcp_plots 

codomyrmex_mcp_client send_request --file heatmap_request.json
```

### Step 3: Examine the MCP Response

The MCP tool should return a JSON response indicating success or failure.

**Example Expected JSON Response (Success):**
```json
{
  "output_path": "./mcp_plots/sales_heatmap.png",
  "fig_details": {
    "status": "saved"
    // Other details might be included here in future versions
  }
}
```

If an error occurred (e.g., invalid `output_path`, incorrect data format), the response would look different, typically including an `"error"` field. For example:
```json
{
  "error": "Invalid output_path: Directory ./mcp_plots/does_not_exist/ does not exist or is not writable.",
  "output_path": null,
  "fig_details": {
      "status": "error"
  }
}
```

### Step 4: Verify the Output File

- If the MCP response indicates success:
    - Navigate to the directory specified in `output_path` (e.g., `./mcp_plots/`).
    - You should find the image file `sales_heatmap.png`.
    - Open the image to view your heatmap.

## 4. Important Considerations for MCP Usage

- **`output_path` Security**: The process executing the MCP tool (the server-side application) needs write access to the `output_path`. It is critical that the server validates and restricts where files can be written to prevent security vulnerabilities like directory traversal or overwriting system files. Plots should ideally be saved to a designated, non-critical output directory.
- **Error Handling**: Always check the MCP response for an `"error"` field or a non-successful status in `fig_details` to determine if the plot generation succeeded.
- **Data Validation**: While the tool will attempt to generate a plot, providing correctly structured data as per the `MCP_TOOL_SPECIFICATION.md` is essential for meaningful output.
- **Resource Usage**: Generating heatmaps from very large datasets can be resource-intensive. Be mindful of this if allowing arbitrary data sizes via MCP calls.

For a complete list of parameters and details for the `create_heatmap` MCP tool and others, always refer to the [Data Visualization MCP Tool Specification](../../MCP_TOOL_SPECIFICATION.md).

## 5. Next Steps

- Experiment with different colormaps (`cmap` parameter).
- Try generating heatmaps with larger or different datasets.
- Explore other MCP plotting tools provided by the `data_visualization` module, such as `create_line_plot` or `create_bar_chart`, by consulting the `MCP_TOOL_SPECIFICATION.md`. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../README.md)
- **Home**: [Root README](../../README.md)
