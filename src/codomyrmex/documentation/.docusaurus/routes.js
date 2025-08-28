import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/codomyrmex/',
    component: ComponentCreator('/codomyrmex/', '53b'),
    routes: [
      {
        path: '/codomyrmex/',
        component: ComponentCreator('/codomyrmex/', '8ed'),
        routes: [
          {
            path: '/codomyrmex/',
            component: ComponentCreator('/codomyrmex/', 'f13'),
            routes: [
              {
                path: '/codomyrmex/development-guides',
                component: ComponentCreator('/codomyrmex/development-guides', 'a10'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/development/documentation-pipeline',
                component: ComponentCreator('/codomyrmex/development/documentation-pipeline', 'd49'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/development/DocumentationMaintenance',
                component: ComponentCreator('/codomyrmex/development/DocumentationMaintenance', '023'),
                exact: true
              },
              {
                path: '/codomyrmex/development/environment-setup',
                component: ComponentCreator('/codomyrmex/development/environment-setup', 'b8b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/development/testing-strategy',
                component: ComponentCreator('/codomyrmex/development/testing-strategy', 'd33'),
                exact: true
              },
              {
                path: '/codomyrmex/modules',
                component: ComponentCreator('/codomyrmex/modules', 'c63'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/', '4b6'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/', 'eab'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/api_specification',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/api_specification', '98b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/changelog',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/changelog', 'abc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/docs/',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/docs/', '234'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/docs/technical_overview', 'dfd'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/docs/tutorials/generate_code_snippet_tutorial',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/docs/tutorials/generate_code_snippet_tutorial', 'dec'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/docs/tutorials/refactor_code_snippet_tutorial',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/docs/tutorials/refactor_code_snippet_tutorial', '0fa'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/mcp_tool_specification', '472'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/security',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/security', 'fe2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/usage_examples', '3ed'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai-code-editing/tutorials',
                component: ComponentCreator('/codomyrmex/modules/ai-code-editing/tutorials', '91a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/', 'e02'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/build_synthesis/',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/', '065'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/api_specification',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/api_specification', 'eff'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/changelog',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/changelog', 'a0b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/docs/',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/docs/', '999'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/build_synthesis/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/docs/technical_overview', '593'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/docs/tutorials/synthesize_code_component_tutorial',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/docs/tutorials/synthesize_code_component_tutorial', 'caa'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/docs/tutorials/trigger_build_tutorial',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/docs/tutorials/trigger_build_tutorial', 'c0b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/mcp_tool_specification', '993'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/security',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/security', 'f98'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/usage_examples', '36f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build-synthesis/tutorials',
                component: ComponentCreator('/codomyrmex/modules/build-synthesis/tutorials', '3cb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/', 'e93'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/', '00a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/api_specification',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/api_specification', '9fb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/changelog',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/changelog', 'db3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/docs/',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/docs/', '947'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/docs/technical_overview', 'dc8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/docs/tutorials/execute_code_tutorial',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/docs/tutorials/execute_code_tutorial', '84a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/mcp_tool_specification', '52f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/security',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/security', '79a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/usage_examples', '34b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code-execution-sandbox/tutorials',
                component: ComponentCreator('/codomyrmex/modules/code-execution-sandbox/tutorials', '6a9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization',
                component: ComponentCreator('/codomyrmex/modules/data_visualization', 'cba'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/data_visualization/',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/', '160'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/api_specification',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/api_specification', '59c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/changelog',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/changelog', '895'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/', 'cc6'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/technical_overview', '623'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/tutorials/generating_a_bar_chart_tutorial',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/tutorials/generating_a_bar_chart_tutorial', 'bc6'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/tutorials/generating_a_histogram_tutorial',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/tutorials/generating_a_histogram_tutorial', '7eb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/tutorials/generating_a_line_plot_tutorial',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/tutorials/generating_a_line_plot_tutorial', 'cd4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/tutorials/generating_a_pie_chart_tutorial',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/tutorials/generating_a_pie_chart_tutorial', 'd59'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/tutorials/generating_a_scatter_plot_tutorial',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/tutorials/generating_a_scatter_plot_tutorial', 'eec'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/tutorials/mcp_heatmap_tutorial',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/tutorials/mcp_heatmap_tutorial', '9e2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/mcp_tool_specification', '848'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/security',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/security', '5cb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/usage_examples', '021'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data-visualization/tutorials',
                component: ComponentCreator('/codomyrmex/modules/data-visualization/tutorials', 'eaf'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation',
                component: ComponentCreator('/codomyrmex/modules/documentation', '50a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation-meta/tutorials',
                component: ComponentCreator('/codomyrmex/modules/documentation-meta/tutorials', '93d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation/api_specification',
                component: ComponentCreator('/codomyrmex/modules/documentation/api_specification', 'efc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation/changelog',
                component: ComponentCreator('/codomyrmex/modules/documentation/changelog', '929'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation/docs/',
                component: ComponentCreator('/codomyrmex/modules/documentation/docs/', 'd6b'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/documentation/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/documentation/docs/technical_overview', '004'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/documentation/docs/tutorials/', '914'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/documentation/docs/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/modules/documentation/docs/tutorials/example_tutorial', '7ca'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/documentation/mcp_tool_specification', '17d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation/security',
                component: ComponentCreator('/codomyrmex/modules/documentation/security', 'a05'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/documentation/usage_examples', '303'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment_setup',
                component: ComponentCreator('/codomyrmex/modules/environment_setup', '5ec'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/environment_setup/',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/', '89e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment_setup/api_specification',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/api_specification', '047'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment_setup/changelog',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/changelog', '9ef'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment_setup/docs/',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/docs/', '9e2'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/environment_setup/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/docs/technical_overview', '8d0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment_setup/docs/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/docs/tutorials/example_tutorial', 'b69'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment_setup/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/mcp_tool_specification', '09c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment_setup/security',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/security', '1d7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment_setup/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/usage_examples', '23c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment-setup/tutorials',
                component: ComponentCreator('/codomyrmex/modules/environment-setup/tutorials', '5dd'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations',
                component: ComponentCreator('/codomyrmex/modules/git_operations', '2d8'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/git_operations/',
                component: ComponentCreator('/codomyrmex/modules/git_operations/', 'e96'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations/api_specification',
                component: ComponentCreator('/codomyrmex/modules/git_operations/api_specification', '441'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations/changelog',
                component: ComponentCreator('/codomyrmex/modules/git_operations/changelog', '469'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations/docs/',
                component: ComponentCreator('/codomyrmex/modules/git_operations/docs/', '08b'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/git_operations/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/git_operations/docs/technical_overview', '5af'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations/docs/tutorials/creating_feature_branch_tutorial',
                component: ComponentCreator('/codomyrmex/modules/git_operations/docs/tutorials/creating_feature_branch_tutorial', '1be'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/git_operations/mcp_tool_specification', '2f5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations/security',
                component: ComponentCreator('/codomyrmex/modules/git_operations/security', '618'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/git_operations/usage_examples', '653'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git-operations/tutorials',
                component: ComponentCreator('/codomyrmex/modules/git-operations/tutorials', 'c9d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging_monitoring',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring', '0b5'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/logging_monitoring',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring', 'd7a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging_monitoring/api_specification',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/api_specification', '8fb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging_monitoring/changelog',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/changelog', 'e28'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging_monitoring/docs/',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/docs/', 'bb2'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/logging_monitoring/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/docs/technical_overview', '2b3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging_monitoring/docs/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/docs/tutorials/example_tutorial', '888'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging_monitoring/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/mcp_tool_specification', 'ddb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging_monitoring/security',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/security', '2f1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging_monitoring/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/usage_examples', 'c53'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging-monitoring/tutorials',
                component: ComponentCreator('/codomyrmex/modules/logging-monitoring/tutorials', '099'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/', '528'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/', '12a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/api_specification',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/api_specification', '814'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/changelog',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/changelog', 'b7f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/docs/',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/docs/', '5b3'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/docs/technical_overview', '579'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/docs/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/docs/tutorials/example_tutorial', '66c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/docs/tutorials/implementing_an_mcp_tool',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/docs/tutorials/implementing_an_mcp_tool', '237'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/mcp_tool_specification', '68b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/security',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/security', '76d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/usage_examples', 'c3a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model-context-protocol/tutorials',
                component: ComponentCreator('/codomyrmex/modules/model-context-protocol/tutorials', '880'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/module_template/',
                component: ComponentCreator('/codomyrmex/modules/module_template/', '8f2'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/module_template/api_specification',
                component: ComponentCreator('/codomyrmex/modules/module_template/api_specification', '212'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/module_template/changelog',
                component: ComponentCreator('/codomyrmex/modules/module_template/changelog', 'a40'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/module_template/docs/',
                component: ComponentCreator('/codomyrmex/modules/module_template/docs/', '52a'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/module_template/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/module_template/docs/technical_overview', 'b36'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/module_template/docs/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/modules/module_template/docs/tutorials/example_tutorial', '83f'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/module_template/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/module_template/mcp_tool_specification', '979'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/module_template/security',
                component: ComponentCreator('/codomyrmex/modules/module_template/security', '29a'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/module_template/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/module_template/usage_examples', '9db'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/pattern_matching',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching', '310'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/pattern_matching/',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/', 'e05'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/api_specification',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/api_specification', '741'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/pattern_matching/changelog',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/changelog', '6b2'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/pattern_matching/docs/',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/docs/', '377'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/pattern_matching/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/docs/technical_overview', '779'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/docs/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/docs/tutorials/example_tutorial', 'a2e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/mcp_tool_specification', '2e5'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/pattern_matching/pattern-matching-api-specification',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/pattern-matching-api-specification', '02b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/pattern-matching-changelog',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/pattern-matching-changelog', 'ace'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/pattern-matching-mcp-tool-specification',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/pattern-matching-mcp-tool-specification', '564'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/pattern-matching-security',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/pattern-matching-security', '29b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/pattern-matching-tasks',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/pattern-matching-tasks', '338'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/pattern_matching/pattern-matching-usage-examples',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/pattern-matching-usage-examples', '359'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/security',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/security', 'ba5'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/pattern_matching/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/usage_examples', '6b2'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/pattern-matching/tutorials',
                component: ComponentCreator('/codomyrmex/modules/pattern-matching/tutorials', 'd1b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/', '060'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/', '75f'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/static_analysis/api_specification',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/api_specification', '70a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/changelog',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/changelog', '56c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/docs/',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/docs/', '4bf'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/static_analysis/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/docs/technical_overview', '80e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/docs/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/docs/tutorials/example_tutorial', '55b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/mcp_tool_specification',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/mcp_tool_specification', '601'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/security',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/security', '4b3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/usage_examples',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/usage_examples', '41c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static-analysis/tutorials',
                component: ComponentCreator('/codomyrmex/modules/static-analysis/tutorials', 'aff'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/project-overview',
                component: ComponentCreator('/codomyrmex/project-overview', 'df7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/project/architecture',
                component: ComponentCreator('/codomyrmex/project/architecture', '18d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/project/code-of-conduct',
                component: ComponentCreator('/codomyrmex/project/code-of-conduct', '2a5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/project/contributing',
                component: ComponentCreator('/codomyrmex/project/contributing', 'f03'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/project/CONTRIBUTING_TO_DOCUMENTATION',
                component: ComponentCreator('/codomyrmex/project/CONTRIBUTING_TO_DOCUMENTATION', '4e7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/project/ERROR_HANDLING_LOGGING',
                component: ComponentCreator('/codomyrmex/project/ERROR_HANDLING_LOGGING', 'd7f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/project/license',
                component: ComponentCreator('/codomyrmex/project/license', '7d2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/project/TESTING_STRATEGY',
                component: ComponentCreator('/codomyrmex/project/TESTING_STRATEGY', 'b7d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/technical_overview',
                component: ComponentCreator('/codomyrmex/technical_overview', 'a9b'),
                exact: true
              },
              {
                path: '/codomyrmex/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/tutorials/example_tutorial', 'f9d'),
                exact: true
              },
              {
                path: '/codomyrmex/',
                component: ComponentCreator('/codomyrmex/', '038'),
                exact: true
              },
              {
                path: '/codomyrmex/',
                component: ComponentCreator('/codomyrmex/', '43e'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
