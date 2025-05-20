import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/codomyrmex/',
    component: ComponentCreator('/codomyrmex/', '06e'),
    routes: [
      {
        path: '/codomyrmex/',
        component: ComponentCreator('/codomyrmex/', '4c4'),
        routes: [
          {
            path: '/codomyrmex/',
            component: ComponentCreator('/codomyrmex/', '1c4'),
            routes: [
              {
                path: '/codomyrmex/category/modules',
                component: ComponentCreator('/codomyrmex/category/modules', 'fb0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/development/environment-setup',
                component: ComponentCreator('/codomyrmex/development/environment-setup', 'b8b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/intro',
                component: ComponentCreator('/codomyrmex/intro', '4a2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/', '3a1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/ai-code-editing-api-specification',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/ai-code-editing-api-specification', '00f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/ai-code-editing-changelog',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/ai-code-editing-changelog', '9a3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/ai-code-editing-mcp-tool-specification',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/ai-code-editing-mcp-tool-specification', 'c1a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/ai-code-editing-security',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/ai-code-editing-security', '345'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/ai-code-editing-usage-examples',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/ai-code-editing-usage-examples', 'afc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/docs/',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/docs/', 'ed1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/docs/ai-code-editing-technical-overview',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/docs/ai-code-editing-technical-overview', '873'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/docs/tutorials/', '1af'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/ai_code_editing/docs/tutorials/ai-code-editing-example-tutorial',
                component: ComponentCreator('/codomyrmex/modules/ai_code_editing/docs/tutorials/ai-code-editing-example-tutorial', '110'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/', 'e16'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/build-synthesis-api-specification',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/build-synthesis-api-specification', '0b1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/build-synthesis-changelog',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/build-synthesis-changelog', '666'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/build-synthesis-mcp-tool-specification',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/build-synthesis-mcp-tool-specification', 'f9f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/build-synthesis-security',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/build-synthesis-security', '60e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/build-synthesis-usage-examples',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/build-synthesis-usage-examples', '092'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/docs/',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/docs/', 'd93'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/docs/build-synthesis-technical-overview',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/docs/build-synthesis-technical-overview', 'd2d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/docs/tutorials/', '77a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/build_synthesis/docs/tutorials/build-synthesis-example-tutorial',
                component: ComponentCreator('/codomyrmex/modules/build_synthesis/docs/tutorials/build-synthesis-example-tutorial', 'f06'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/', '44b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/code-execution-sandbox-api-specification',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/code-execution-sandbox-api-specification', '0ef'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/code-execution-sandbox-changelog',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/code-execution-sandbox-changelog', 'b0c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/code-execution-sandbox-mcp-tool-specification',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/code-execution-sandbox-mcp-tool-specification', '663'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/code-execution-sandbox-security',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/code-execution-sandbox-security', 'ecf'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/docs/',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/docs/', '90e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/docs/technical_overview', 'dc8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/docs/tutorials/', 'e06'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/docs/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/docs/tutorials/example_tutorial', '3be'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/code_execution_sandbox/USAGE_EXAMPLES',
                component: ComponentCreator('/codomyrmex/modules/code_execution_sandbox/USAGE_EXAMPLES', 'bc7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization',
                component: ComponentCreator('/codomyrmex/modules/data_visualization', '228'),
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
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/', '1a0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/technical_overview', '623'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/tutorials/', 'f42'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/data_visualization/docs/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/modules/data_visualization/docs/tutorials/example_tutorial', 'f10'),
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
                path: '/codomyrmex/modules/documentation',
                component: ComponentCreator('/codomyrmex/modules/documentation', '50a'),
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
                component: ComponentCreator('/codomyrmex/modules/documentation/docs/', '6f5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/documentation/docs/technical_overview', '004'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/documentation/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/documentation/docs/tutorials/', '7ac'),
                exact: true,
                sidebar: "tutorialSidebar"
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
                component: ComponentCreator('/codomyrmex/modules/environment_setup', '273'),
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
                component: ComponentCreator('/codomyrmex/modules/environment_setup/docs/', '278'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment_setup/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/docs/technical_overview', '8d0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/environment_setup/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/environment_setup/docs/tutorials/', '32b'),
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
                path: '/codomyrmex/modules/git_operations',
                component: ComponentCreator('/codomyrmex/modules/git_operations', '44a'),
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
                component: ComponentCreator('/codomyrmex/modules/git_operations/docs/', 'f60'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/git_operations/docs/technical_overview', '5af'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/git_operations/docs/tutorials/', '845'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/git_operations/docs/tutorials/example_tutorial',
                component: ComponentCreator('/codomyrmex/modules/git_operations/docs/tutorials/example_tutorial', '1e0'),
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
                path: '/codomyrmex/modules/logging_monitoring',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring', 'e30'),
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
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/docs/', 'b94'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging_monitoring/docs/technical_overview',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/docs/technical_overview', '2b3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/logging_monitoring/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/logging_monitoring/docs/tutorials/', 'fc1'),
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
                path: '/codomyrmex/modules/model_context_protocol/',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/', '0df'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/docs/',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/docs/', '4bf'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/docs/model-context-protocol-technical-overview',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/docs/model-context-protocol-technical-overview', 'd9e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/docs/tutorials/', '944'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/docs/tutorials/model-context-protocol-example-tutorial',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/docs/tutorials/model-context-protocol-example-tutorial', 'ef5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/model-context-protocol-api-specification',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/model-context-protocol-api-specification', 'e0e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/model-context-protocol-changelog',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/model-context-protocol-changelog', '7d6'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/model-context-protocol-mcp-tool-specification',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/model-context-protocol-mcp-tool-specification', 'bff'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/model-context-protocol-security',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/model-context-protocol-security', '844'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/model_context_protocol/model-context-protocol-usage-examples',
                component: ComponentCreator('/codomyrmex/modules/model_context_protocol/model-context-protocol-usage-examples', '46f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching', '925'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/docs/pattern-matching-module-docs-index',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/docs/pattern-matching-module-docs-index', '7e0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/docs/pattern-matching-technical-overview',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/docs/pattern-matching-technical-overview', 'c68'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/docs/tutorials/pattern-matching-example-tutorial',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/docs/tutorials/pattern-matching-example-tutorial', '820'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/pattern_matching/docs/tutorials/pattern-matching-tutorials-index',
                component: ComponentCreator('/codomyrmex/modules/pattern_matching/docs/tutorials/pattern-matching-tutorials-index', '238'),
                exact: true,
                sidebar: "tutorialSidebar"
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
                path: '/codomyrmex/modules/static_analysis/',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/', 'aec'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/docs/',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/docs/', '656'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/docs/static-analysis-technical-overview',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/docs/static-analysis-technical-overview', 'd4a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/docs/tutorials/',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/docs/tutorials/', '08e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/docs/tutorials/static-analysis-example-tutorial',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/docs/tutorials/static-analysis-example-tutorial', 'a06'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/docs/tutorials/static-analysis-pylint-example-tutorial',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/docs/tutorials/static-analysis-pylint-example-tutorial', '1ab'),
                exact: true
              },
              {
                path: '/codomyrmex/modules/static_analysis/static-analysis-api-specification',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/static-analysis-api-specification', '000'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/static-analysis-changelog',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/static-analysis-changelog', '250'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/static-analysis-mcp-tool-specification',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/static-analysis-mcp-tool-specification', 'edc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/static-analysis-security',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/static-analysis-security', 'c13'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/codomyrmex/modules/static_analysis/static-analysis-usage-examples',
                component: ComponentCreator('/codomyrmex/modules/static_analysis/static-analysis-usage-examples', '806'),
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
                path: '/codomyrmex/project/license',
                component: ComponentCreator('/codomyrmex/project/license', '7d2'),
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
