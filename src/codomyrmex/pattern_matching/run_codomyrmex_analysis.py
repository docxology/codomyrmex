import json
import os
import shutil
import sys
from typing import Callable, Optional  # Added Optional for type hinting embed_fn

from tqdm import tqdm  # Added tqdm

# Add project root to Python path to allow sibling module imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation

from dotenv import load_dotenv
from kit import (
    DocstringIndexer,
    OpenAIConfig,
    Repository,
)  # Summarizer is accessed via repo.get_summarizer()

# Attempt to import SentenceTransformer for explicit embedding function
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    # This print will be visible if the script is run and the import fails
    # The logger might not be initialized yet.
    print(
        "[CRITICAL SETUP ERROR] `sentence-transformers` package not found. DocstringIndexer will likely fail. Please install it: pip install sentence-transformers"
    )
    SentenceTransformer = (
        None  # Allow script to proceed but DocstringIndexer will fail if used
    )

# Attempt to import the new environment setup function
try:
    from codomyrmex.environment_setup.env_checker import (
        check_and_setup_env_vars,
    )
    from codomyrmex.environment_setup.env_checker import (
        ensure_dependencies_installed as ensure_core_deps_installed,
    )
except ImportError:
    # This initial print might be okay if logger isn't set up yet, or handle differently
    print(
        "[ERROR] Could not import from codomyrmex.environment_setup.env_checker. Please ensure the module exists and is in the Python path."
    )
    sys.exit(1)

# Import logging setup
try:
    from codomyrmex.logging_monitoring import get_logger, setup_logging
except ImportError:
    print(
        "[ERROR] Could not import from codomyrmex.logging_monitoring. Please ensure the module exists and is in the Python path."
    )
    sys.exit(1)

# --- Script Configuration ---

# !!! IMPORTANT: Update this path to the absolute path of your codomyrmex repository !!!
# REPO_ROOT_PATH = "/home/trim/Documents/GitHub/codomyrmex"
REPO_ROOT_PATH = PROJECT_ROOT  # Use the dynamically determined project root

# Output directory will be in the REPO_ROOT_PATH
BASE_OUTPUT_DIR_NAME = "output/codomyrmex_analysis"
BASE_OUTPUT_DIR = os.path.join(REPO_ROOT_PATH, BASE_OUTPUT_DIR_NAME)

MODULE_DIRS = [
    "ai_code_editing",
    "build_synthesis",
    "code_execution_sandbox",
    "data_visualization",
    "documentation",  # The module, not necessarily the docs site if it's separate
    "environment_setup",
    "git_operations",
    "logging_monitoring",
    "model_context_protocol",
    "pattern_matching",
    "static_analysis",
    "template/module_template",
]

# Dynamically generate module names for symbol search
# Takes the basename of each path in MODULE_DIRS
module_symbol_names = [
    os.path.basename(mod_dir.rstrip("/\\")) for mod_dir in MODULE_DIRS
]

# --- Analysis Parameters (all configured in-script) ---
ANALYSIS_CONFIG = {
    "text_search_queries": ["TODO", "FIXME", "NOTE", "HACK", "XXX", "MCP"],
    "files_to_summarize_count": 1,  # Max number of files to summarize per module/repo
    "max_summary_char_limit": 25000,  # Max characters for a file to be considered for summarization
    "docstring_search_query": "example function usage",
    "embedding_model": "all-MiniLM-L6-v2",  # For DocstringIndexer
    "symbols_to_find_usages": list(
        set(
            [
                "get_logger",
                "Repository",
                "main",
                "OpenAIConfig",
                "DocstringIndexer",
                "analyze_repository_path",
                "run_full_analysis",
                "setup_logging",
                "check_and_setup_env_vars",
                "ensure_core_deps_installed",
                "print_once",
                "summarize_file",
                "extract_symbols",
                "search_text",
                "chunk_file_by_lines",
                "chunk_file_by_symbols",  # Adding some kit methods
            ]
            + module_symbol_names
        )
    ),  # Example symbols
    "max_text_search_contexts_to_extract": 1,  # Max number of contexts to extract for text search results
    "max_files_for_chunking_examples": 1,  # Max number of files to generate chunking examples for
    # --- Flags to toggle analysis stages ---
    "run_repository_index": True,
    "run_dependency_analysis": True,
    "run_text_search": True,
    "run_code_summarization": True,
    "run_docstring_indexing": True,
    "run_symbol_extraction": True,
    "run_symbol_usage_analysis": True,
    "run_text_search_context_extraction": True,
    "run_chunking_examples": True,
}

# Initialize logger after imports and before it's used globally
# setup_logging() is called in run_full_analysis
logger = None  # Will be initialized in run_full_analysis
PRINTED_ONCE_KEYS = set()  # For print_once utility

# --- Global Embedding Function (for DocstringIndexer) ---
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
_embed_fn_instance: Optional[Callable[[str], list[float]]] = None


def get_embedding_function(model_name: str = DEFAULT_EMBEDDING_MODEL):
    global _embed_fn_instance
    if _embed_fn_instance is not None:
        return _embed_fn_instance

    if SentenceTransformer is None:
        err_msg = f"[CRITICAL EMBEDDING ERROR] SentenceTransformer library not available. Cannot create embedding function for model '{model_name}'."
        if logger:  # Check if logger exists
            logger.error(err_msg)
        else:
            print(err_msg)
        return None

    try:
        st_model = SentenceTransformer(model_name)
        def _embed_fn_instance(text):
            return st_model.encode(text).tolist()
        if logger:  # Check if logger exists
            logger.info(
                f"Successfully initialized sentence-transformer model '{model_name}' for embeddings."
            )
        else:
            print(
                f"[INFO] Successfully initialized sentence-transformer model '{model_name}' for embeddings (logger not yet active)."
            )
        return _embed_fn_instance
    except Exception as e:
        err_msg = f"[CRITICAL EMBEDDING ERROR] Failed to initialize SentenceTransformer model '{model_name}': {e}"
        if logger:  # Check if logger exists
            logger.error(err_msg)
        else:
            print(err_msg)
        return None


# --- Helper Functions for Individual Analysis Stages ---


def _perform_repository_index(
    repo: Repository,
    full_output_path: str,
    relative_output_dir_name: str,
    config: dict,
    _logger,
):
    errors = []
    # _logger.info("Starting: Repository Index generation") # tqdm will show this
    if config.get("run_repository_index", True):
        try:
            repo.write_index(os.path.join(full_output_path, "repository_index.json"))
            _logger.info(f"Completed: Repository index for {relative_output_dir_name}")
        except Exception as e:
            err_msg = f"Failed: Repository index for {relative_output_dir_name}: {e}"
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(
            f"Skipped: Repository Index generation for {relative_output_dir_name} as per config."
        )
    return errors


def _perform_dependency_analysis(
    repo: Repository,
    full_output_path: str,
    relative_output_dir_name: str,
    config: dict,
    _logger,
):
    errors = []
    # _logger.info("Starting: Python Dependency Analysis")
    if config.get("run_dependency_analysis", True):
        try:
            py_files_exist = any(
                f_info.get("path", "").endswith(".py")
                for f_info in repo.get_file_tree()
            )
            if py_files_exist:
                analyzer = repo.get_dependency_analyzer("python")
                if analyzer:
                    analyzer.export_dependency_graph(
                        output_format="dot",
                        output_path=os.path.join(
                            full_output_path, "dependency_graph.dot"
                        ),
                    )

                    cycles = analyzer.find_cycles()
                    with open(
                        os.path.join(full_output_path, "dependency_cycles.txt"), "w"
                    ) as f:
                        if cycles:
                            f.write(f"Found {len(cycles)} circular dependencies:\n")
                            for cycle_list in cycles:  # cycles is a list of lists
                                f.write(
                                    f"  {' -> '.join(cycle_list)} -> {cycle_list[0]}\n"
                                )
                        else:
                            f.write("No circular dependencies found.\n")

                    analyzer.generate_llm_context(
                        output_format="markdown",
                        output_path=os.path.join(
                            full_output_path, "dependency_llm_context.md"
                        ),
                    )

                    if hasattr(
                        analyzer, "generate_dependency_report"
                    ):  # PythonDependencyAnalyzer specific
                        dep_report = analyzer.generate_dependency_report()
                        with open(
                            os.path.join(
                                full_output_path, "python_dependency_report.json"
                            ),
                            "w",
                        ) as f:
                            json.dump(dep_report, f, indent=2)
                    _logger.info(
                        f"Completed: Python dependency analysis for {relative_output_dir_name}"
                    )
                else:
                    _logger.warning(
                        f"Could not get Python dependency analyzer for {relative_output_dir_name}"
                    )
            else:
                _logger.info(
                    f"Skipped: Python dependency analysis for {relative_output_dir_name} (no .py files found)"
                )
        except Exception as e:
            err_msg = f"Failed: Python dependency analysis for {relative_output_dir_name}: {e}"
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(
            f"Skipped: Python Dependency Analysis for {relative_output_dir_name} as per config."
        )
    return errors


def _perform_text_search(
    repo: Repository,
    full_output_path: str,
    relative_output_dir_name: str,
    config: dict,
    _logger,
):
    errors = []
    text_search_results_data = {}
    # _logger.info("Starting: Text Search")
    if config.get("run_text_search", True):
        try:
            queries = config.get("text_search_queries", ["TODO", "FIXME"])
            for query in tqdm(
                queries,
                desc=f"Text Searching in {relative_output_dir_name}",
                unit="query",
                leave=False,
            ):
                results = repo.search_text(
                    query, file_pattern="*.*"
                )  # search all files
                text_search_results_data[query] = results
            with open(
                os.path.join(full_output_path, "text_search_results.json"), "w"
            ) as f:
                json.dump(text_search_results_data, f, indent=2)
            _logger.info(f"Completed: Text search for {relative_output_dir_name}")
        except Exception as e:
            err_msg = f"Failed: Text search for {relative_output_dir_name}: {e}"
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(
            f"Skipped: Text Search for {relative_output_dir_name} as per config."
        )
    return text_search_results_data, errors  # Return data for context extraction


def _perform_code_summarization(
    repo: Repository,
    full_output_path: str,
    relative_output_dir_name: str,
    config: dict,
    llm_config: OpenAIConfig,
    _logger,
):
    errors = []
    # _logger.info("Starting: Code Summarization (Optional)")
    if config.get("run_code_summarization", True):
        summaries_output_dir = os.path.join(full_output_path, "code_summaries")
        os.makedirs(summaries_output_dir, exist_ok=True)
        max_char_limit = config.get("max_summary_char_limit", 25000)
        try:
            summarizer = repo.get_summarizer(config=llm_config)

            candidate_files_for_summary = [
                f_info.get("path")
                for f_info in repo.get_file_tree()
                if f_info.get("path")
                and not f_info.get("is_dir")
                and f_info.get("path", "").endswith((".py", ".md", ".txt"))
            ]

            COMMON_MD_FILENAMES_LOWER = {
                "security.md",
                "readme.md",
                "contributing.md",
                "license.md",
                "code_of_conduct.md",
            }

            def sort_key_summarize(file_path_str):
                base, ext = os.path.splitext(os.path.basename(file_path_str))
                base_lower = base.lower()
                ext_lower = ext.lower()

                ext_prio = {".py": 0, ".md": 1, ".txt": 2}.get(ext_lower, 3)
                is_init = base_lower == "__init__"

                is_module_specific_analysis = (
                    "full_repository_review" not in relative_output_dir_name
                )
                is_common_md = (
                    ext_lower == ".md" and base_lower in COMMON_MD_FILENAMES_LOWER
                )
                is_req_txt = ext_lower == ".txt" and base_lower == "requirements"

                score = 0
                if ext_prio == 0:  # .py
                    score = 0 + (1 if is_init else 0)
                elif ext_prio == 1:  # .md
                    score = 10 + (
                        1 if is_module_specific_analysis and is_common_md else 0
                    )
                elif ext_prio == 2:  # .txt
                    score = 20 + (
                        1 if is_module_specific_analysis and is_req_txt else 0
                    )
                else:
                    score = 30

                return (score, -len(base))

            candidate_files_for_summary.sort(key=sort_key_summarize)
            files_to_summarize_selected = candidate_files_for_summary[
                : config.get("files_to_summarize_count", 1)
            ]

            if files_to_summarize_selected:
                model_name = "default LLM"
                if hasattr(summarizer, "config") and hasattr(
                    summarizer.config, "model"
                ):
                    model_name = summarizer.config.model
                _logger.info(
                    f"Attempting to summarize {len(files_to_summarize_selected)} files for {relative_output_dir_name} using model '{model_name}' (char limit: {max_char_limit})..."
                )
                for file_path_in_repo in tqdm(
                    files_to_summarize_selected,
                    desc=f"Summarizing files in {relative_output_dir_name}",
                    unit="file",
                    leave=False,
                ):
                    try:
                        full_file_path = os.path.join(repo.repo_path, file_path_in_repo)
                        file_size = os.path.getsize(
                            full_file_path
                        )  # Check actual file size in bytes (approx chars)

                        if file_size > max_char_limit:
                            _logger.warning(
                                f"  Skipped summarizing {file_path_in_repo} ({file_size} chars) as it exceeds the configured limit of {max_char_limit} chars."
                            )
                            continue

                        summary_content = summarizer.summarize_file(
                            file_path_in_repo
                        )  # Path relative to repo root
                        summary_file_name = (
                            os.path.basename(file_path_in_repo).replace(".", "_")
                            + "_summary.txt"
                        )
                        with open(
                            os.path.join(summaries_output_dir, summary_file_name),
                            "w",
                            encoding="utf-8",
                        ) as f:
                            f.write(summary_content)
                        _logger.info(f"  Summarized: {file_path_in_repo}")
                    except FileNotFoundError:
                        _logger.warning(
                            f"  File not found for summarization: {file_path_in_repo}"
                        )
                    except Exception as e_summ:
                        err_msg_summ = (
                            f"  Failed to summarize {file_path_in_repo}: {e_summ}"
                        )
                        _logger.error(err_msg_summ)
                        errors.append(err_msg_summ)
            else:
                _logger.info(
                    f"No suitable files found for summarization in {relative_output_dir_name}."
                )
            _logger.info(
                f"Completed: Code Summarization attempt for {relative_output_dir_name}"
            )
        except Exception as e_summarizer_init:
            err_msg_init = f"Code summarization feature may be limited or skipped for {relative_output_dir_name}: {e_summarizer_init}. (Likely missing API key or Summarizer init failed)."
            print_once(
                "summarizer_init_failed_" + relative_output_dir_name,
                err_msg_init,
                level="warning",
                _logger=_logger,
            )
            errors.append(err_msg_init)
    else:
        _logger.info(
            f"Skipped: Code Summarization for {relative_output_dir_name} as per config."
        )
    return errors


def _perform_docstring_indexing(
    repo: Repository,
    full_output_path: str,
    relative_output_dir_name: str,
    config: dict,
    llm_config: OpenAIConfig,
    _logger,
):
    errors = []
    # _logger.info("Starting: Docstring Indexing (Optional)")
    if config.get("run_docstring_indexing", True):
        docstring_output_dir = os.path.join(full_output_path, "docstring_index_data")
        # Persist dir for ChromaDB (DocstringIndexer's default backend)
        # Needs to be unique per analysis target to avoid collisions if multiple analyses run concurrently
        # or if the script is re-run for different modules.
        # A simple way is to use a subdirectory named after `relative_output_dir_name`
        # However, `relative_output_dir_name` can contain slashes (e.g., module_template_review/...),
        # so replace them for a valid directory name.
        sanitized_dir_name = relative_output_dir_name.replace("/", "_").replace(
            "\\", "_"
        )
        persist_dir_for_indexer = os.path.join(
            docstring_output_dir, sanitized_dir_name + "_chromadb"
        )
        os.makedirs(persist_dir_for_indexer, exist_ok=True)

        try:
            summarizer_for_indexer = repo.get_summarizer(config=llm_config)
            embedding_model_name = config.get(
                "embedding_model", DEFAULT_EMBEDDING_MODEL
            )

            # Get the embedding function
            current_embed_fn = get_embedding_function(embedding_model_name)
            if not current_embed_fn:
                err_msg = f"Skipping Docstring Indexing for {relative_output_dir_name}: Embedding function could not be initialized for model '{embedding_model_name}'. Check previous errors."
                _logger.error(err_msg)
                errors.append(err_msg)
                return errors  # Critical failure for this stage

            _logger.info(
                f"Initializing DocstringIndexer for {relative_output_dir_name} with embedding model '{embedding_model_name}' and persist_dir='{persist_dir_for_indexer}'."
            )

            # Pass the explicitly defined embed_fn and persist_dir
            indexer = DocstringIndexer(
                repo=repo,
                summarizer=summarizer_for_indexer,
                embed_fn=current_embed_fn,
                persist_dir=persist_dir_for_indexer,
            )

            model_name = "default LLM"
            if hasattr(summarizer_for_indexer, "config") and hasattr(
                summarizer_for_indexer.config, "model"
            ):
                model_name = summarizer_for_indexer.config.model

            _logger.info(
                f"Building docstring index for {relative_output_dir_name} using summarizer model '{model_name}'..."
            )

            # Build the index (symbol-level by default, can be configured via `level`)
            # Consider making `file_extensions` configurable as well.
            indexer.build(
                force=True, level="symbol", file_extensions=[".py", ".md"]
            )  # Force rebuild, symbol level for better granularity

            _logger.info(
                f"Completed: Docstring indexing for {relative_output_dir_name}"
            )

            # Example search (optional, for verification)
            search_query = config.get(
                "docstring_search_query", "example function usage"
            )
            search_results = indexer.get_searcher().search(search_query, top_k=3)
            with open(
                os.path.join(full_output_path, "docstring_search_example_results.json"),
                "w",
            ) as f:
                # Convert search results to a more JSON-serializable format if they contain non-standard objects
                # For now, assuming they are dicts of basic types or lists of such.
                try:
                    json.dump(search_results, f, indent=2)
                except TypeError as te:
                    _logger.warning(
                        f"Could not serialize docstring search results to JSON: {te}. Writing basic info."
                    )
                    json.dump([str(r) for r in search_results], f, indent=2)
            _logger.info(
                f"  Performed example docstring search for '{search_query}' for {relative_output_dir_name}"
            )

        except ImportError as ie_st:
            # This specific catch is for sentence-transformers not being installed.
            err_msg = f"Docstring indexing skipped for {relative_output_dir_name} due to missing 'sentence-transformers'. Error: {ie_st}. Please install the package."
            print_once(
                "docstring_indexer_import_error_" + relative_output_dir_name,
                err_msg,
                level="error",
                _logger=_logger,
            )
            errors.append(err_msg)
        except Exception as e_dsi:
            err_msg = (
                f"Failed: Docstring indexing for {relative_output_dir_name}: {e_dsi}"
            )
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(
            f"Skipped: Docstring Indexing for {relative_output_dir_name} as per config."
        )
    return errors


def _perform_symbol_extraction(
    repo: Repository,
    full_output_path: str,
    relative_output_dir_name: str,
    config: dict,
    _logger,
):
    errors = []
    all_symbols_data = []
    # _logger.info("Starting: Extract All Symbols (Python files)")
    if config.get("run_symbol_extraction", True):
        try:
            # Assuming repo.extract_symbols() gives all symbols from python files
            # If it needs specific file types, that should be handled here or in the kit.
            all_symbols_data = (
                repo.extract_symbols()
            )  # This could be slow for large repos

            output_file = os.path.join(full_output_path, "all_python_symbols.json")
            with open(output_file, "w") as f:
                json.dump(all_symbols_data, f, indent=2)

            if all_symbols_data:
                _logger.info(
                    f"Completed: Extracted and wrote {len(all_symbols_data)} Python symbols for {relative_output_dir_name}"
                )
            else:
                _logger.info(
                    f"No Python symbols extracted for {relative_output_dir_name}"
                )
        except Exception as e:
            err_msg = (
                f"Failed: Python symbol extraction for {relative_output_dir_name}: {e}"
            )
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(
            f"Skipped: Python Symbol Extraction for {relative_output_dir_name} as per config."
        )
    return all_symbols_data, errors  # Return symbols for usage analysis


def _perform_symbol_usage_analysis(
    repo: Repository,
    all_symbols_data: list,
    full_output_path: str,
    relative_output_dir_name: str,
    config: dict,
    _logger,
):
    errors = []
    # _logger.info("Starting: Find Symbol Usages")
    if config.get("run_symbol_usage_analysis", True):
        symbols_output_dir = os.path.join(full_output_path, "symbol_usages")
        os.makedirs(symbols_output_dir, exist_ok=True)

        symbols_to_check = config.get("symbols_to_find_usages", [])

        if not symbols_to_check:
            _logger.info(
                f"No symbols configured for usage analysis in {relative_output_dir_name}."
            )
        else:
            _logger.info(
                f"Analyzing usages for {len(symbols_to_check)} configured symbols in {relative_output_dir_name}..."
            )
            for symbol_name in tqdm(
                symbols_to_check,
                desc=f"Finding symbol usages in {relative_output_dir_name}",
                unit="symbol",
                leave=False,
            ):
                try:
                    usages = repo.find_symbol_usages(symbol_name)
                    usage_file_name = f"{symbol_name.replace('.', '_').replace('/', '_')}_usages.json"  # Sanitize name
                    with open(
                        os.path.join(symbols_output_dir, usage_file_name), "w"
                    ) as f:
                        json.dump(usages, f, indent=2)
                    # _logger.info(f"  Completed: Found and wrote usages for symbol '{symbol_name}' to {os.path.join(symbols_output_dir, usage_file_name)}")
                except Exception as e_usage:
                    err_msg = f"  Failed to find usages for symbol '{symbol_name}' in {relative_output_dir_name}: {e_usage}"
                    _logger.error(err_msg)
                    errors.append(err_msg)
            _logger.info(
                f"Completed: Symbol usage search for {relative_output_dir_name}"
            )
    else:
        _logger.info(
            f"Skipped: Symbol Usage Analysis for {relative_output_dir_name} as per config."
        )
    return errors


def _perform_text_search_context_extraction(
    repo: Repository,
    text_search_results_data: dict,
    full_output_path: str,
    relative_output_dir_name: str,
    config: dict,
    _logger,
):
    errors = []
    # _logger.info("Starting: Extract Context for Text Search Results")
    if config.get("run_text_search_context_extraction", True):
        if not text_search_results_data:
            _logger.info(
                f"Skipped: No text search results to extract context from for {relative_output_dir_name}."
            )
        else:
            try:
                contexts_output_dir = os.path.join(
                    full_output_path, "text_search_contexts"
                )
                os.makedirs(contexts_output_dir, exist_ok=True)

                max_contexts = config.get("max_text_search_contexts_to_extract", 1)
                extracted_count = 0

                # Using tqdm for iterating over queries
                for query, results in tqdm(
                    text_search_results_data.items(),
                    desc=f"Extracting contexts in {relative_output_dir_name}",
                    unit="query",
                    leave=False,
                ):
                    if not results:
                        continue
                    query_contexts = []
                    # Potentially use tqdm here if results list can be very long
                    for _res_idx, res in enumerate(results):
                        if extracted_count >= max_contexts:
                            break
                        try:
                            file_path = res.get("file_path", "Unknown_file")
                            line_number = res.get("line_number", "Unknown_line")
                            # Placeholder for actual context extraction. This might need a repo method.
                            # For now, just log that context extraction would happen here.
                            # context_snippet = f"Context for {file_path} line {line_number} (TODO: implement actual context extraction via repo.get_context_for_match)"

                            # Attempt to use get_context_for_match if available (hypothetical)
                            context_snippet = f"Context for {file_path} line {line_number} not extracted (method unavailable)."
                            if hasattr(repo, "get_context_for_match"):
                                try:
                                    # Assuming get_context_for_match returns a string or serializable object
                                    context_snippet_data = repo.get_context_for_match(
                                        res["file_path"],
                                        res["line_number"],
                                        window_size=5,
                                    )
                                    context_snippet = (
                                        json.dumps(context_snippet_data)
                                        if not isinstance(context_snippet_data, str)
                                        else context_snippet_data
                                    )
                                except Exception as e_get_ctx:
                                    _logger.warning(
                                        f"Could not get context snippet for {file_path} line {line_number}: {e_get_ctx}"
                                    )

                            context = {
                                "match_info": res,
                                "context_snippet": context_snippet,
                            }
                            query_contexts.append(context)
                            extracted_count += 1
                        except Exception as e_ctx:
                            _logger.warning(
                                f"Could not extract context for {res.get('file_path', 'N/A')} line {res.get('line_number', 'N/A')}: {e_ctx}"
                            )

                    if query_contexts:
                        with open(
                            os.path.join(contexts_output_dir, f"{query}_contexts.json"),
                            "w",
                        ) as f:
                            json.dump(query_contexts, f, indent=2)
                _logger.info(
                    f"Completed: Extracted context for up to {max_contexts} text search results for {relative_output_dir_name}."
                )

            except Exception as e:
                err_msg = f"Failed: Text search context extraction for {relative_output_dir_name}: {e}"
                _logger.error(err_msg)
                errors.append(err_msg)
    else:
        _logger.info(
            f"Skipped: Text Search Context Extraction for {relative_output_dir_name} as per config."
        )
    return errors


def _get_chunking_example_output_path(
    full_output_path: str, file_path_in_repo: str, type: str = "lines"
):
    chunking_output_dir = os.path.join(full_output_path, "file_chunking_examples")
    os.makedirs(chunking_output_dir, exist_ok=True)
    base_name = os.path.basename(file_path_in_repo).replace(".", "_")
    return os.path.join(chunking_output_dir, f"{base_name}_chunks_by_{type}.json")


def _perform_chunking_examples(
    repo: Repository,
    full_output_path: str,
    relative_output_dir_name: str,
    config: dict,
    _logger,
):
    errors = []
    # _logger.info("Starting: Generate File Chunking Examples")
    if config.get("run_chunking_examples", True):
        chunking_output_dir = os.path.join(full_output_path, "file_chunking_examples")
        os.makedirs(chunking_output_dir, exist_ok=True)
        try:
            candidate_files = [
                f_info.get("path")
                for f_info in repo.get_file_tree()
                if f_info.get("path")
                and not f_info.get("is_dir")
                and f_info.get("path", "").endswith((".py", ".md", ".txt"))
            ]
            candidate_files.sort(key=lambda x: (0 if x.endswith(".py") else 1, x))

            files_for_examples = candidate_files[
                : config.get("max_files_for_chunking_examples", 1)
            ]

            if files_for_examples:
                _logger.info(
                    f"Generating chunking examples for {len(files_for_examples)} files in {relative_output_dir_name}..."
                )
                for file_path_in_repo in tqdm(
                    files_for_examples,
                    desc=f"Generating chunk examples in {relative_output_dir_name}",
                    unit="file",
                    leave=False,
                ):
                    _logger.info(f"  Processing chunks for {file_path_in_repo}")
                    try:
                        line_chunks = repo.chunk_file_by_lines(
                            file_path_in_repo, max_lines=50
                        )
                        symbol_chunks = []
                        if file_path_in_repo.endswith(".py"):
                            try:
                                symbol_chunks = repo.chunk_file_by_symbols(
                                    file_path_in_repo
                                )
                            except Exception as e_sym_chunk:
                                _logger.warning(
                                    f"    Could not generate symbol chunks for {file_path_in_repo}: {e_sym_chunk}"
                                )

                        example_data = {
                            "file_path": file_path_in_repo,
                            "line_chunks_example_first_3": (
                                line_chunks[:3]
                                if line_chunks
                                else "No line chunks generated or file empty."
                            ),
                            "symbol_chunks_example_first_3": (
                                symbol_chunks[:3]
                                if symbol_chunks
                                else "No symbol chunks generated or not a Python file."
                            ),
                        }
                        chunk_file_name = (
                            os.path.basename(file_path_in_repo).replace(".", "_")
                            + "_chunking_example.json"
                        )
                        with open(
                            os.path.join(chunking_output_dir, chunk_file_name),
                            "w",
                            encoding="utf-8",
                        ) as f:
                            json.dump(
                                example_data,
                                f,
                                indent=2,
                                default=lambda o: "<not serializable>",
                            )
                    except FileNotFoundError:
                        _logger.warning(
                            f"  File not found for chunking example: {file_path_in_repo}"
                        )
                    except Exception as e_chunk_file:
                        err_msg_chunk = f"    Failed to generate chunking example for {file_path_in_repo}: {e_chunk_file}"
                        _logger.error(err_msg_chunk)
                        errors.append(err_msg_chunk)
                _logger.info(
                    f"Completed: Generated chunking examples for {len(files_for_examples)} files."
                )
            else:
                _logger.info(
                    f"No suitable files found for generating chunking examples in {relative_output_dir_name}."
                )

        except Exception as e:
            err_msg = f"Failed: File chunking example generation for {relative_output_dir_name}: {e}"
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(
            f"Skipped: File Chunking Examples for {relative_output_dir_name} as per config."
        )
    return errors


# --- Main Analysis Orchestration Function ---
def analyze_repository_path(
    path_to_analyze: str,
    relative_output_dir_name: str,
    config: dict,
    module_pbar_desc: str,
):
    """
    Runs a suite of kit analyses on the given repository path and saves results.
    Returns a list of error messages encountered.
    """
    global logger
    if not logger:
        print(
            "[WARN] Logger not initialized in analyze_repository_path. Using basic print for initial messages."
        )

        # A simple fallback logger for when the main logger isn't ready
        class DummyLogger:
            def info(self, msg):
                print(f"[INFO] {msg}")

            def warning(self, msg):
                print(f"[WARNING] {msg}")

            def error(self, msg):
                print(f"[ERROR] {msg}")

        _logger_instance = DummyLogger()
    else:
        _logger_instance = logger

    all_errors_for_path = []

    full_output_path = os.path.join(BASE_OUTPUT_DIR, relative_output_dir_name)
    os.makedirs(full_output_path, exist_ok=True)

    _logger_instance.info(
        f"----- Starting Analysis for: {path_to_analyze} ({relative_output_dir_name}) -----"
    )
    # _logger_instance.info(f"Outputting to: {full_output_path}") # Redundant with tqdm desc

    try:
        repo = Repository(path_to_analyze)
        llm_model_name = config.get("llm_model_for_summaries", "gpt-4o-mini")
        llm_config = OpenAIConfig(model=llm_model_name)

        # Define analysis stages for tqdm
        analysis_stages = []
        if config.get("run_repository_index", True):
            analysis_stages.append(
                (
                    "Repo Index",
                    lambda: _perform_repository_index(
                        repo,
                        full_output_path,
                        relative_output_dir_name,
                        config,
                        _logger_instance,
                    ),
                )
            )
        if config.get("run_dependency_analysis", True):
            analysis_stages.append(
                (
                    "Deps Analysis",
                    lambda: _perform_dependency_analysis(
                        repo,
                        full_output_path,
                        relative_output_dir_name,
                        config,
                        _logger_instance,
                    ),
                )
            )

        # Text search returns data, so handle it slightly differently
        text_search_results = {}
        if config.get("run_text_search", True):

            def text_search_stage():
                nonlocal text_search_results  # To modify the outer scope variable
                results, errors = _perform_text_search(
                    repo,
                    full_output_path,
                    relative_output_dir_name,
                    config,
                    _logger_instance,
                )
                text_search_results = results
                return errors

            analysis_stages.append(("Text Search", text_search_stage))

        if config.get("run_code_summarization", True):
            analysis_stages.append(
                (
                    "Summarization",
                    lambda: _perform_code_summarization(
                        repo,
                        full_output_path,
                        relative_output_dir_name,
                        config,
                        llm_config,
                        _logger_instance,
                    ),
                )
            )
        if config.get("run_docstring_indexing", True):
            analysis_stages.append(
                (
                    "Docstring Index",
                    lambda: _perform_docstring_indexing(
                        repo,
                        full_output_path,
                        relative_output_dir_name,
                        config,
                        llm_config,
                        _logger_instance,
                    ),
                )
            )

        # Symbol extraction returns data
        all_symbols = []
        if config.get("run_symbol_extraction", True):

            def symbol_extraction_stage():
                nonlocal all_symbols
                symbols, errors = _perform_symbol_extraction(
                    repo,
                    full_output_path,
                    relative_output_dir_name,
                    config,
                    _logger_instance,
                )
                all_symbols = symbols
                return errors

            analysis_stages.append(("Symbol Extract", symbol_extraction_stage))

        if config.get("run_symbol_usage_analysis", True):
            analysis_stages.append(
                (
                    "Symbol Usages",
                    lambda: _perform_symbol_usage_analysis(
                        repo,
                        all_symbols,
                        full_output_path,
                        relative_output_dir_name,
                        config,
                        _logger_instance,
                    ),
                )
            )
        if config.get("run_text_search_context_extraction", True):
            analysis_stages.append(
                (
                    "Text Contexts",
                    lambda: _perform_text_search_context_extraction(
                        repo,
                        text_search_results,
                        full_output_path,
                        relative_output_dir_name,
                        config,
                        _logger_instance,
                    ),
                )
            )
        if config.get("run_chunking_examples", True):
            analysis_stages.append(
                (
                    "Chunk Examples",
                    lambda: _perform_chunking_examples(
                        repo,
                        full_output_path,
                        relative_output_dir_name,
                        config,
                        _logger_instance,
                    ),
                )
            )

        # Iterate through stages with tqdm
        for stage_name, stage_func in tqdm(
            analysis_stages,
            desc=f"Analyzing {module_pbar_desc}",
            unit="stage",
            leave=False,
        ):
            errors = stage_func()
            if errors:  # errors is expected to be a list
                all_errors_for_path.extend(errors)
                _logger_instance.error(
                    f"Errors encountered during '{stage_name}' for {relative_output_dir_name}: {errors}"
                )

    except Exception as e_repo_init:
        err_msg = f"FATAL: Could not initialize Repository for path {path_to_analyze}: {e_repo_init}"
        _logger_instance.error(err_msg)
        all_errors_for_path.append(err_msg)

    _logger_instance.info(
        f"----- Finished analysis for: {path_to_analyze} ({relative_output_dir_name}) -----"
    )
    return all_errors_for_path


# --- Main Script Execution ---
def run_full_analysis():
    """
    Main function to orchestrate the analysis of all configured modules and the full repository.
    """
    global logger, PRINTED_ONCE_KEYS
    setup_logging()
    logger = get_logger(__name__)
    PRINTED_ONCE_KEYS.clear()

    overall_errors = []

    logger.info("--- Starting Codomyrmex Review Script ---")

    try:
        logger.info("Running initial environment and dependency checks...")
        ensure_core_deps_installed()
        logger.info("Environment and dependency checks completed.")
    except Exception as e_env_check:
        logger.error(
            f"Environment check failed: {e_env_check}. Attempting to continue but some features might be affected."
        )
        overall_errors.append(f"Environment check failed: {e_env_check}")

    if os.path.exists(BASE_OUTPUT_DIR):
        logger.info(f"Removing existing output directory: {BASE_OUTPUT_DIR}")
        try:
            shutil.rmtree(BASE_OUTPUT_DIR)
        except OSError as e:
            logger.error(
                f"Error removing directory {BASE_OUTPUT_DIR}: {e}. Please check permissions or remove manually."
            )
            overall_errors.append(f"Error removing directory {BASE_OUTPUT_DIR}: {e}")
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
    logger.info(f"Created base output directory: {BASE_OUTPUT_DIR}")

    # Analyze each module with a main progress bar
    logger.info(f"Analyzing {len(MODULE_DIRS)} modules...")
    for module_dir_name in tqdm(
        MODULE_DIRS, desc="Overall Module Progress", unit="module"
    ):
        module_path = os.path.join(REPO_ROOT_PATH, module_dir_name)
        if not os.path.isdir(module_path):
            logger.warning(f"Module directory not found: {module_path}. Skipping.")
            overall_errors.append(f"Module directory not found: {module_path}")
            continue

        output_dir_name_for_module = (
            os.path.basename(module_dir_name).replace(".", "_") + "_review"
        )
        # Pass a clean description for the inner pbar
        module_pbar_description = os.path.basename(module_dir_name)
        module_errors = analyze_repository_path(
            module_path,
            output_dir_name_for_module,
            ANALYSIS_CONFIG,
            module_pbar_description,
        )
        overall_errors.extend(module_errors)

    # Analyze the full repository
    logger.info("----- Starting Analysis for: Full Repository -----")
    full_repo_errors = analyze_repository_path(
        REPO_ROOT_PATH, "full_repository_review", ANALYSIS_CONFIG, "Full Repository"
    )
    overall_errors.extend(full_repo_errors)
    logger.info("----- Finished Analysis for: Full Repository -----")

    logger.info("--- Codomyrmex Review Complete ---")
    logger.info(f"All outputs are in: {BASE_OUTPUT_DIR}")

    if overall_errors:
        logger.error("--- Summary of Errors Encountered During Analysis ---")
        # Use tqdm for error summary if it's long, or just print
        for i, err in enumerate(
            tqdm(overall_errors, desc="Summarizing Errors", unit="error", leave=False)
            if len(overall_errors) > 10
            else overall_errors
        ):
            logger.error(f"  Error {i+1}: {err}")
        logger.error("--- End of Error Summary ---")
    else:
        logger.info("No errors reported during the analysis run.")

    logger.info("Review script finished.")


def print_once(key, message, level="info", _logger=None):
    """
    Prints a message only once per script run, based on the key.
    Uses the global logger if _logger is not provided.
    """
    global PRINTED_ONCE_KEYS, logger

    current_logger = _logger if _logger else logger

    if key not in PRINTED_ONCE_KEYS:
        if not current_logger:
            try:
                tqdm.write(
                    f"[PRINT_ONCE FALLBACK - {level.upper()}]: ({key}) {message}"
                )
            except Exception:
                print(f"[PRINT_ONCE FALLBACK - {level.upper()}]: ({key}) {message}")
        else:
            log_method = getattr(current_logger, level, None)
            if not callable(log_method):
                # Fallback to info if the specified level is not a valid method
                log_method = getattr(current_logger, "info", None)

            if callable(log_method):
                log_method(f"({key}) {message}")
            else:
                # Absolute fallback if no logging method is found (should be rare)
                try:
                    tqdm.write(
                        f"[PRINT_ONCE UNEXPECTED FALLBACK - {level.upper()}]: ({key}) {message}"
                    )
                except Exception:
                    print(
                        f"[PRINT_ONCE UNEXPECTED FALLBACK - {level.upper()}]: ({key}) {message}"
                    )
        PRINTED_ONCE_KEYS.add(key)


if __name__ == "__main__":
    load_dotenv()
    run_full_analysis()
else:
    # When imported as a module, just set up the logger without running analysis
    setup_logging()
