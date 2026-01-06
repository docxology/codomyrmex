# Data Visualization - MCP Tool Specification

This document outlines the specification for tools within the Data Visualization module that are intended to be integrated with the Model Context Protocol (MCP).

## Initialization & Dependencies

- All tools require the `logging_monitoring` module for logging. Ensure `setup_logging()` is called at application startup.
- Use the `environment_setup` module to check/install dependencies and set up environment variables.

## Tool: `create_heatmap`

### 1. Tool Purpose and Description

Generates a heatmap from a 2D data array, with optional axis labels, color map, and annotations.

### 2. Invocation Name

`create_heatmap`

### 3. Input Schema (Parameters)

| Parameter Name   | Type        | Required | Description                                      | Example Value      |
| :-------------- | :---------- | :------- | :----------------------------------------------- | :----------------- |
| `data`          | array[array[float]] | Yes | 2D data array for the heatmap.                  | `[[1,2],[3,4]]`    |
| `x_labels`      | array[string] | No      | Labels for the x-axis.                           | `["A", "B"]`      |
| `y_labels`      | array[string] | No      | Labels for the y-axis.                           | `["Row1", "Row2"]`|
| `title`         | string      | No       | Title of the heatmap. Default: "Heatmap".        | `"My Heatmap"`     |
| `x_label`       | string      | No       | X-axis label. Default: "X-axis".                 | `"X"`             |
| `y_label`       | string      | No       | Y-axis label. Default: "Y-axis".                 | `"Y"`             |
| `cmap`          | string      | No       | Matplotlib colormap.                             | `"viridis"`        |
| `colorbar_label`| string      | No       | Label for the colorbar.                          | `"Intensity"`      |
| `output_path`   | string      | No       | File path to save the plot. If None, plot is not saved. The path should be absolute or relative to a pre-defined writable directory for the MCP agent. | `"./output/heatmap.png"`  |
| `show_plot`     | boolean     | No       | If True, attempts to display the plot (behavior might be backend-dependent for a server-side MCP tool and generally not recommended for automated agents). Default: `false`.    | `false`            |
| `annot`         | boolean     | No       | If True, annotates each cell. Default: `false`.  | `true`             |
| `fmt`           | string      | No       | Format string for annotations. Default: `".2f"`.| `".1f"`            |
| `figure_size`   | tuple[float,float] | No | Size of the figure (width, height) in inches. Default: `(10, 8)`. | `[8,6]` |

### 4. Output Schema (Return Value)

| Field Name    | Type   | Description                                                                 | Example Value     |
| :------------ | :----- | :-------------------------------------------------------------------------- | :---------------- |
| `output_path` | string | The absolute path where the plot was saved, if `output_path` was provided. Else null. | `"/mnt/shared/output/heatmap.png"` |
| `fig_details` | object | Information about the generated figure (e.g., if it was saved or an attempt to show was made).   | `{"status": "saved_to_path"}` |

### 5. Error Handling

- Errors are logged using `logging_monitoring`.
- If data is invalid or missing, a warning is logged and no plot is generated (returns null or error indication).
- Returns `{"error": "description"}` on failure.

### 6. Idempotency

- Idempotent: Yes (calling with the same arguments produces the same plot output file if `output_path` is specified).

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "create_heatmap",
  "arguments": {
    "data": [[10, 25, 30], [15, 5, 40]],
    "x_labels": ["X1", "X2", "X3"],
    "y_labels": ["Y_A", "Y_B"],
    "title": "Sample Heatmap via MCP",
    "output_path": "./output/mcp_heatmap.png"
  }
}
```

### 8. Security Considerations

- Logging is handled via `logging_monitoring` (ensure logs do not contain sensitive PII).
- Environment and dependencies are managed via `environment_setup`.
- File output is controlled by the user-supplied `output_path`. Ensure the path is validated and restricted to prevent unauthorized file access/overwrite in sensitive directories. The application running the MCP tool server should have appropriate file system permissions.

---

## Tool: `create_line_plot`

### 1. Tool Purpose and Description

Generates a line plot from X and Y data. Can plot multiple lines if Y data is a list of lists.

### 2. Invocation Name

`create_line_plot`

### 3. Input Schema (Parameters)

| Parameter Name | Type        | Required | Description                                      | Example Value      |
| :------------- | :---------- | :------- | :----------------------------------------------- | :----------------- |
| `x_data`       | array[float] | Yes      | Data for the x-axis.                             | `[1, 2, 3, 4]`     |
| `y_data`       | array[float] or array[array[float]] | Yes | Data for the y-axis. Can be a single list for one line, or list of lists for multiple lines. | `[10, 15, 13, 17]` or `[[10,15,13,17], [5,8,6,9]]` |
| `title`        | string      | No       | Title of the plot. Default: "Line Plot".         | `"Sales Over Time"`|
| `x_label`      | string      | No       | X-axis label. Default: "X-axis".                 | `"Month"`          |
| `y_label`      | string      | No       | Y-axis label. Default: "Y-axis".                 | `"Sales (Units)"`  |
| `output_path`  | string      | No       | File path to save the plot. If None, not saved. The path should be absolute or relative to a pre-defined writable directory.  | `"./output/line.png"`|
| `show_plot`    | boolean     | No       | If True, attempts to display the plot. Default: `false`. | `false`           |
| `line_labels`  | array[string] | No     | Labels for multiple lines (for legend). Auto-generated if not provided for multiple lines. | `["Product A", "Product B"]` |
| `markers`      | boolean     | No       | If True, adds markers to data points. Default: `false`. | `true`            |
| `figure_size`  | tuple[float,float] | No | Size of the figure (width, height) in inches. Default: `(10, 6)`. | `[12,7]`          |


### 4. Output Schema (Return Value)

| Field Name    | Type   | Description                                                                 | Example Value     |
| :------------ | :----- | :-------------------------------------------------------------------------- | :---------------- |
| `output_path` | string | The absolute path where the plot was saved, if `output_path` was provided. Else null. | `"/mnt/shared/output/line.png"` |
| `fig_details` | object | Information about the generated figure.                                     | `{"status": "saved_to_path"}` |

### 5. Error Handling

- Logs errors/warnings. Returns `{"error": "description"}` on critical failure (e.g., data mismatch).
- Handles empty data gracefully by logging and not plotting.

### 6. Idempotency

- Idempotent: Yes.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "create_line_plot",
  "arguments": {
    "x_data": [1, 2, 3, 4],
    "y_data": [[1, 4, 2, 5], [2, 3, 3, 4]],
    "title": "Performance Comparison",
    "x_label": "Quarter",
    "y_label": "Score",
    "line_labels": ["Metric 1", "Metric 2"],
    "output_path": "./output/mcp_line_plot.png",
    "markers": true
  }
}
```

### 8. Security Considerations

- Path validation for `output_path` is crucial. Restrict write access.

---

## Tool: `create_scatter_plot`

### 1. Tool Purpose and Description

Generates a scatter plot from X and Y data points.

### 2. Invocation Name

`create_scatter_plot`

### 3. Input Schema (Parameters)

| Parameter Name | Type        | Required | Description                                      | Example Value      |
| :------------- | :---------- | :------- | :----------------------------------------------- | :----------------- |
| `x_data`       | array[float] | Yes      | Data for the x-axis.                             | `[1, 2, 3, 4]`     |
| `y_data`       | array[float] | Yes      | Data for the y-axis.                             | `[10, 15, 13, 17]` |
| `title`        | string      | No       | Title of the plot. Default: "Scatter Plot".      | `"Correlation"`    |
| `x_label`      | string      | No       | X-axis label. Default: "X-axis".                 | `"Height"`         |
| `y_label`      | string      | No       | Y-axis label. Default: "Y-axis".                 | `"Weight"`         |
| `output_path`  | string      | No       | File path to save the plot. The path should be absolute or relative to a pre-defined writable directory.                      | `"./output/scatter.png"`|
| `show_plot`    | boolean     | No       | If True, attempts to display the plot. Default: `false`. | `false`           |
| `dot_size`     | integer     | No       | Size of the dots. Default: `20`.                 | `30`               |
| `dot_color`    | string      | No       | Color of the dots. Default: `"blue"`.          | `"red"`            |
| `alpha`        | float       | No       | Transparency of dots (0-1). Default: `0.7`.      | `0.5`              |
| `figure_size`  | tuple[float,float] | No | Size of the figure (width, height) in inches. Default: `(10, 6)`. | `[8,8]`            |

### 4. Output Schema (Return Value)

| Field Name    | Type   | Description                                  | Example Value     |
| :------------ | :----- | :------------------------------------------- | :---------------- |
| `output_path` | string | Absolute path where plot was saved, if applicable.    | `"/mnt/shared/output/scatter.png"` |
| `fig_details` | object | Info about the generated figure.             | `{"status": "saved_to_path"}` |

### 5. Error Handling

- Logs errors/warnings. Returns `{"error": "description"}` on failure.
- Handles empty or mismatched data.

### 6. Idempotency

- Idempotent: Yes.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "create_scatter_plot",
  "arguments": {
    "x_data": [1, 2, 2.5, 3, 4.2],
    "y_data": [5, 7, 6, 8, 7.5],
    "title": "Height vs Weight",
    "output_path": "./output/mcp_scatter.png",
    "dot_color": "green"
  }
}
```

### 8. Security Considerations

- Path validation for `output_path`.

---

## Tool: `create_bar_chart`

### 1. Tool Purpose and Description

Generates a bar chart from categories and their corresponding values. Can be vertical or horizontal.

### 2. Invocation Name

`create_bar_chart`

### 3. Input Schema (Parameters)

| Parameter Name | Type        | Required | Description                                      | Example Value      |
| :------------- | :---------- | :------- | :----------------------------------------------- | :----------------- |
| `categories`   | array[string] | Yes      | List of strings for category labels.             | `["A", "B", "C"]`  |
| `values`       | array[float] | Yes      | List of numerical values for each category.      | `[10, 20, 15]`     |
| `title`        | string      | No       | Title of the chart. Default: "Bar Chart".        | `"Category Sales"` |
| `x_label`      | string      | No       | X-axis label. Default: "Categories".             | `"Product Type"`   |
| `y_label`      | string      | No       | Y-axis label. Default: "Values".                 | `"Units Sold"`     |
| `output_path`  | string      | No       | File path to save the chart. The path should be absolute or relative to a pre-defined writable directory.                     | `"./output/bar.png"`|
| `show_plot`    | boolean     | No       | If True, attempts to display the chart. Default: `false`. | `false`           |
| `horizontal`   | boolean     | No       | If True, creates a horizontal bar chart. Default: `false`. | `true`           |
| `bar_color`    | string      | No       | Color of the bars. Default: Matplotlib default.  | `"skyblue"`      |
| `figure_size`  | tuple[float,float] | No | Size of the figure (width, height) in inches. Default: `(10, 6)`. | `[8,5]`            |

### 4. Output Schema (Return Value)

| Field Name    | Type   | Description                                  | Example Value     |
| :------------ | :----- | :------------------------------------------- | :---------------- |
| `output_path` | string | Absolute path where plot was saved, if applicable.    | `"/mnt/shared/output/bar.png"` |
| `fig_details` | object | Info about the generated figure.             | `{"status": "saved_to_path"}` |

### 5. Error Handling

- Logs errors/warnings. Returns `{"error": "description"}` on failure.
- Handles empty or mismatched data (categories vs. values).

### 6. Idempotency

- Idempotent: Yes.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "create_bar_chart",
  "arguments": {
    "categories": ["Q1", "Q2", "Q3", "Q4"],
    "values": [150, 200, 180, 220],
    "title": "Quarterly Revenue",
    "x_label": "Quarter",
    "y_label": "Revenue (USD)",
    "output_path": "./output/mcp_bar_chart.png",
    "horizontal": false
  }
}
```

### 8. Security Considerations

- Path validation for `output_path` is crucial. Restrict write access.

---

## Tool: `create_histogram`

### 1. Tool Purpose and Description

Generates a histogram to display the distribution of a single numerical dataset.

### 2. Invocation Name

`create_histogram`

### 3. Input Schema (Parameters)

| Parameter Name | Type        | Required | Description                                      | Example Value      |
| :------------- | :---------- | :------- | :----------------------------------------------- | :----------------- |
| `data`         | array[float]| Yes      | 1D array of numerical data.                      | `[1,2,2,3,3,3,4,4,5]`|
| `bins`         | integer or string or array[float] | No | Number of bins, or a string strategy (e.g., "auto"), or array of bin edges. Default: `10`. | `15` or `"auto"`|
| `title`        | string      | No       | Title of the histogram. Default: "Histogram".    | `"Data Distribution"`|
| `x_label`      | string      | No       | X-axis label. Default: "Value".                  | `"Measurement"`    |
| `y_label`      | string      | No       | Y-axis label. Default: "Frequency".              | `"Count"`          |
| `output_path`  | string      | No       | File path to save the histogram. The path should be absolute or relative to a pre-defined writable directory. | `"./output/histogram.png"`|
| `show_plot`    | boolean     | No       | If True, attempts to display the histogram. Default: `false`. | `false`           |
| `hist_color`   | string      | No       | Color of the histogram bars. Default: Matplotlib default. | `"cornflowerblue"` |
| `edge_color`   | string      | No       | Color of bar edges. Default: `"black"`.          | `"gray"`           |
| `density`      | boolean     | No       | If True, normalize to form a probability density. Default: `false`. | `true`            |
| `figure_size`  | tuple[float,float] | No | Size of the figure (width, height) in inches. Default: `(10, 6)`. | `[8,5]`            |

### 4. Output Schema (Return Value)

| Field Name    | Type   | Description                                  | Example Value     |
| :------------ | :----- | :------------------------------------------- | :---------------- |
| `output_path` | string | Absolute path where plot was saved, if applicable.    | `"/mnt/shared/output/histogram.png"` |
| `fig_details` | object | Info about the generated figure.             | `{"status": "saved_to_path"}` |

### 5. Error Handling

- Logs errors/warnings. Returns `{"error": "description"}` on failure.
- Handles empty data.

### 6. Idempotency

- Idempotent: Yes.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "create_histogram",
  "arguments": {
    "data": [10, 12, 12, 13, 15, 15, 15, 18, 20, 22],
    "bins": 5,
    "title": "Value Distribution",
    "output_path": "./output/mcp_histogram.png",
    "hist_color": "green"
  }
}
```

### 8. Security Considerations

- Path validation for `output_path` is crucial. Restrict write access.

---

## Tool: `create_pie_chart`

### 1. Tool Purpose and Description

Generates a pie chart to show proportions of different categories.

### 2. Invocation Name

`create_pie_chart`

### 3. Input Schema (Parameters)

| Parameter Name | Type        | Required | Description                                      | Example Value      |
| :------------- | :---------- | :------- | :----------------------------------------------- | :----------------- |
| `labels`       | array[string] | Yes      | List of labels for each slice.                   | `["A", "B", "C"]`  |
| `sizes`        | array[float] | Yes      | List of numerical values for slice sizes.        | `[40, 30, 30]`     |
| `title`        | string      | No       | Title of the chart. Default: "Pie Chart".        | `"Market Share"`   |
| `output_path`  | string      | No       | File path to save the chart. The path should be absolute or relative to a pre-defined writable directory. | `"./output/pie.png"`|
| `show_plot`    | boolean     | No       | If True, attempts to display the chart. Default: `false`. | `false`           |
| `autopct`      | string      | No       | Format string for slice values (e.g., "%1.1f%%"). Default: `"%1.1f%%"`. | `"%1.0f%%"`        |
| `startangle`   | float       | No       | Rotates start of pie chart (degrees). Default: `90`.| `0`                |
| `explode`      | array[float] | No      | List of offsets for each slice (e.g., [0, 0.1, 0]). | `[0, 0.1, 0]`      |
| `colors`       | array[string] | No      | List of colors for slices. Default: Matplotlib defaults. | `["gold", "lightcoral", "lightskyblue"]` |
| `figure_size`  | tuple[float,float] | No | Size of the figure (width, height) in inches. Default: `(8, 8)`. | `[7,7]`            |

### 4. Output Schema (Return Value)

| Field Name    | Type   | Description                                  | Example Value     |
| :------------ | :----- | :------------------------------------------- | :---------------- |
| `output_path` | string | Absolute path where plot was saved, if applicable.    | `"/mnt/shared/output/pie_chart.png"` |
| `fig_details` | object | Info about the generated figure.             | `{"status": "saved_to_path"}` |

### 5. Error Handling

- Logs errors/warnings. Returns `{"error": "description"}` on failure.
- Handles empty or mismatched data (labels vs. sizes).

### 6. Idempotency

- Idempotent: Yes.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "create_pie_chart",
  "arguments": {
    "labels": ["Product X", "Product Y", "Product Z"],
    "sizes": [250, 450, 300],
    "title": "Sales Distribution by Product",
    "output_path": "./output/mcp_pie_chart.png",
    "explode": [0, 0.05, 0],
    "startangle": 45
  }
}
```

### 8. Security Considerations

- Path validation for `output_path` is crucial. Restrict write access.
- Ensure `labels` and other string inputs are handled safely if they come from untrusted sources, though typical plotting libraries are robust against injection via labels.

---
<!-- End of tool specifications for Data Visualization --> 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
