import os
import shutil
import json
import sys

# Add project root to Python path to allow sibling module imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
from kit import Repository, DocstringIndexer # Summarizer is accessed via repo.get_summarizer()
from kit.summaries import OpenAIConfig # Added import for OpenAIConfig
# Attempt to import the new environment setup function
try:
    from environment_setup.env_checker import check_and_setup_env_vars, ensure_dependencies_installed as ensure_core_deps_installed
except ImportError:
    # This initial print might be okay if logger isn't set up yet, or handle differently
    print("[ERROR] Could not import from environment_setup.env_checker. Please ensure the module exists and is in the Python path.")
    sys.exit(1)

# Import logging setup
try:
    from logging_monitoring import setup_logging, get_logger
except ImportError:
    print("[ERROR] Could not import from logging_monitoring. Please ensure the module exists and is in the Python path (PROJECT_ROOT/logging_monitoring).")
    sys.exit(1)

# --- Script Configuration ---

# !!! IMPORTANT: Update this path to the absolute path of your codomyrmex repository !!!
# REPO_ROOT_PATH = "/home/trim/Documents/GitHub/codomyrmex"
REPO_ROOT_PATH = PROJECT_ROOT # Use the dynamically determined project root

# Output directory will be in the REPO_ROOT_PATH
BASE_OUTPUT_DIR_NAME = "output/codomyrmex_analysis"
BASE_OUTPUT_DIR = os.path.join(REPO_ROOT_PATH, BASE_OUTPUT_DIR_NAME)

MODULE_DIRS = [
    "ai_code_editing",
    "build_synthesis",
    "code_execution_sandbox",
    "data_visualization",
    "documentation", # The module, not necessarily the docs site if it's separate
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
module_symbol_names = [os.path.basename(mod_dir.rstrip('/\\')) for mod_dir in MODULE_DIRS]

# --- Analysis Parameters (all configured in-script) ---
ANALYSIS_CONFIG = {
    "text_search_queries": ["TODO", "FIXME", "NOTE", "HACK", "XXX", "MCP"],
    "files_to_summarize_count": 1,  # Max number of files to summarize per module/repo
    "max_summary_char_limit": 25000, # Max characters for a file to be considered for summarization
    "docstring_search_query": "example function usage",
    "embedding_model": 'all-MiniLM-L6-v2', # For DocstringIndexer
    "symbols_to_find_usages": list(set(
        ["get_logger", "Repository", "main", "OpenAIConfig", "DocstringIndexer",
         "analyze_repository_path", "run_full_analysis", "setup_logging",
         "check_and_setup_env_vars", "ensure_core_deps_installed", "print_once",
         "summarize_file", "extract_symbols", "search_text", "chunk_file_by_lines", "chunk_file_by_symbols" # Adding some kit methods
         ] + module_symbol_names
    )), # Example symbols
    "max_text_search_contexts_to_extract": 1, # Max number of contexts to extract for text search results
    "max_files_for_chunking_examples": 1, # Max number of files to generate chunking examples for
    
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
logger = None # Will be initialized in run_full_analysis
PRINTED_ONCE_KEYS = set() # For print_once utility

# --- Helper Functions for Individual Analysis Stages ---

def _perform_repository_index(repo: Repository, full_output_path: str, relative_output_dir_name: str, config: dict, _logger):
    errors = []
    _logger.info("Starting: Repository Index generation")
    if config.get("run_repository_index", True):
        try:
            repo.write_index(os.path.join(full_output_path, "repository_index.json"))
            _logger.info(f"Completed: Repository index for {relative_output_dir_name}")
        except Exception as e:
            err_msg = f"Failed: Repository index for {relative_output_dir_name}: {e}"
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(f"Skipped: Repository Index generation for {relative_output_dir_name} as per config.")
    return errors

def _perform_dependency_analysis(repo: Repository, full_output_path: str, relative_output_dir_name: str, config: dict, _logger):
    errors = []
    _logger.info("Starting: Python Dependency Analysis")
    if config.get("run_dependency_analysis", True):
        try:
            py_files_exist = any(f_info.get('path', '').endswith(".py") for f_info in repo.get_file_tree())
            if py_files_exist:
                analyzer = repo.get_dependency_analyzer('python')
                if analyzer:
                    analyzer.export_dependency_graph(output_format="dot", output_path=os.path.join(full_output_path, "dependency_graph.dot"))
                    
                    cycles = analyzer.find_cycles()
                    with open(os.path.join(full_output_path, "dependency_cycles.txt"), "w") as f:
                        if cycles:
                            f.write(f"Found {len(cycles)} circular dependencies:\\n")
                            for cycle_list in cycles: # cycles is a list of lists
                                f.write(f"  {' -> '.join(cycle_list)} -> {cycle_list[0]}\\n")
                        else:
                            f.write("No circular dependencies found.\\n")
                    
                    analyzer.generate_llm_context(output_format="markdown", output_path=os.path.join(full_output_path, "dependency_llm_context.md"))
                    
                    if hasattr(analyzer, "generate_dependency_report"): # PythonDependencyAnalyzer specific
                         dep_report = analyzer.generate_dependency_report()
                         with open(os.path.join(full_output_path, "python_dependency_report.json"), "w") as f:
                             json.dump(dep_report, f, indent=2)
                    _logger.info(f"Completed: Python dependency analysis for {relative_output_dir_name}")
                else:
                    _logger.warning(f"Could not get Python dependency analyzer for {relative_output_dir_name}")
            else:
                _logger.info(f"Skipped: Python dependency analysis for {relative_output_dir_name} (no .py files found)")
        except Exception as e:
            err_msg = f"Failed: Python dependency analysis for {relative_output_dir_name}: {e}"
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(f"Skipped: Python Dependency Analysis for {relative_output_dir_name} as per config.")
    return errors

def _perform_text_search(repo: Repository, full_output_path: str, relative_output_dir_name: str, config: dict, _logger):
    errors = []
    text_search_results_data = {}
    _logger.info("Starting: Text Search")
    if config.get("run_text_search", True):
        try:
            for query in config.get("text_search_queries", ["TODO", "FIXME"]):
                results = repo.search_text(query, file_pattern="*.*") # search all files
                text_search_results_data[query] = results
            with open(os.path.join(full_output_path, "text_search_results.json"), "w") as f:
                json.dump(text_search_results_data, f, indent=2)
            _logger.info(f"Completed: Text search for {relative_output_dir_name}")
        except Exception as e:
            err_msg = f"Failed: Text search for {relative_output_dir_name}: {e}"
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(f"Skipped: Text Search for {relative_output_dir_name} as per config.")
    return text_search_results_data, errors # Return data for context extraction

def _perform_code_summarization(repo: Repository, full_output_path: str, relative_output_dir_name: str, config: dict, llm_config: OpenAIConfig, _logger):
    errors = []
    _logger.info("Starting: Code Summarization (Optional)")
    if config.get("run_code_summarization", True):
        summaries_output_dir = os.path.join(full_output_path, "code_summaries")
        os.makedirs(summaries_output_dir, exist_ok=True)
        max_char_limit = config.get("max_summary_char_limit", 25000)
        try:
            summarizer = repo.get_summarizer(config=llm_config)
            
            candidate_files_for_summary = [
                f_info.get('path') for f_info in repo.get_file_tree() 
                if f_info.get('path') and not f_info.get('is_dir') and \
                   f_info.get('path', '').endswith((".py", ".md", ".txt"))
            ]

            COMMON_MD_FILENAMES_LOWER = {"security.md", "readme.md", "contributing.md", "license.md", "code_of_conduct.md"}

            def sort_key_summarize(file_path_str):
                base, ext = os.path.splitext(os.path.basename(file_path_str))
                base_lower = base.lower()
                ext_lower = ext.lower()
                
                ext_prio = {".py": 0, ".md": 1, ".txt": 2}.get(ext_lower, 3)
                is_init = base_lower == "__init__"
                
                is_module_specific_analysis = "full_repository_review" not in relative_output_dir_name
                is_common_md = ext_lower == ".md" and base_lower in COMMON_MD_FILENAMES_LOWER
                is_req_txt = ext_lower == ".txt" and base_lower == "requirements"

                score = 0
                if ext_prio == 0: # .py
                    score = 0 + (1 if is_init else 0) 
                elif ext_prio == 1: # .md
                    score = 10 + (1 if is_module_specific_analysis and is_common_md else 0)
                elif ext_prio == 2: # .txt
                    score = 20 + (1 if is_module_specific_analysis and is_req_txt else 0) 
                else:
                    score = 30
                
                return (score, -len(base)) 

            candidate_files_for_summary.sort(key=sort_key_summarize)
            files_to_summarize_selected = candidate_files_for_summary[:config.get("files_to_summarize_count", 1)]

            if files_to_summarize_selected:
                model_name = 'default LLM'
                if hasattr(summarizer, 'config') and hasattr(summarizer.config, 'model'):
                    model_name = summarizer.config.model
                _logger.info(f"Attempting to summarize {len(files_to_summarize_selected)} files for {relative_output_dir_name} using model '{model_name}' (char limit: {max_char_limit})...")
                for file_path_in_repo in files_to_summarize_selected:
                    try:
                        full_file_path = os.path.join(repo.repo_path, file_path_in_repo)
                        file_size = os.path.getsize(full_file_path) # Check actual file size in bytes (approx chars)

                        if file_size > max_char_limit:
                            _logger.warning(f"  Skipped summarizing {file_path_in_repo} ({file_size} chars) as it exceeds the configured limit of {max_char_limit} chars.")
                            continue

                        summary_content = summarizer.summarize_file(file_path_in_repo) # Path relative to repo root
                        summary_file_name = os.path.basename(file_path_in_repo).replace(".", "_") + "_summary.txt"
                        with open(os.path.join(summaries_output_dir, summary_file_name), "w", encoding='utf-8') as f:
                            f.write(summary_content)
                        _logger.info(f"  Summarized: {file_path_in_repo}")
                    except FileNotFoundError:
                        _logger.warning(f"  File not found for summarization: {file_path_in_repo}")
                    except Exception as e_summ:
                        err_msg_summ = f"  Failed to summarize {file_path_in_repo}: {e_summ}"
                        _logger.error(err_msg_summ)
                        errors.append(err_msg_summ)
            else:
                _logger.info(f"No suitable files found for summarization in {relative_output_dir_name}.")
            _logger.info(f"Completed: Code Summarization attempt for {relative_output_dir_name}")
        except Exception as e_summarizer_init:
            err_msg_init = f"Code summarization feature may be limited or skipped for {relative_output_dir_name}: {e_summarizer_init}. (Likely missing API key or Summarizer init failed)."
            print_once("summarizer_init_failed_" + relative_output_dir_name, err_msg_init, level="warning", _logger=_logger)
            errors.append(err_msg_init)
    else:
        _logger.info(f"Skipped: Code Summarization for {relative_output_dir_name} as per config.")
    return errors

def _perform_docstring_indexing(repo: Repository, full_output_path: str, relative_output_dir_name: str, config: dict, llm_config: OpenAIConfig, _logger):
    errors = []
    _logger.info("Starting: Docstring Indexing and Search (Optional)")
    if config.get("run_docstring_indexing", True):
        docstring_index_persist_dir = os.path.join(full_output_path, "docstring_index_data")
        try:
            from sentence_transformers import SentenceTransformer # Dynamically import to check availability
            
            embed_model_name = config.get("embedding_model", 'all-MiniLM-L6-v2')
            embed_model = None
            device_used = "auto (default)"

            try:
                _logger.info(f"Attempting to load SentenceTransformer model '{embed_model_name}' with auto device selection.")
                embed_model = SentenceTransformer(embed_model_name) # Default device selection
                embed_model.encode("test sentence") # Test to catch device issues early
                device_used = str(embed_model.device) # Actual device
                _logger.info(f"Successfully loaded SentenceTransformer model on device: {device_used}")
            except Exception as e_model_load:
                print_once(f"st_model_load_failed_{embed_model_name}", f"Failed to load SentenceTransformer model '{embed_model_name}': {e_model_load}. Docstring indexing will be impacted.", level="warning", _logger=_logger)
                errors.append(f"Failed to load SentenceTransformer model for {relative_output_dir_name}: {e_model_load}")
                embed_model = None

            if embed_model: # Proceed only if model loaded successfully
                _logger.info(f"Building docstring index for {relative_output_dir_name} using '{embed_model_name}' (this may take time)...")
                os.makedirs(docstring_index_persist_dir, exist_ok=True)
                
                try:
                    summarizer = repo.get_summarizer(config=llm_config)
                except Exception as e_summ_init:
                    _logger.error(f"Failed to initialize Summarizer for DocstringIndexer in {relative_output_dir_name}: {e_summ_init}")
                    errors.append(f"Summarizer init failed for DocstringIndexer in {relative_output_dir_name}: {e_summ_init}")
                    return errors # Stop if summarizer cannot be initialized

                indexer = DocstringIndexer(
                    repo=repo,
                    summarizer=summarizer,
                    embed_fn=embed_model.encode, # Use the encode method of the loaded model
                    persist_dir=docstring_index_persist_dir
                )
                indexer.build(force=True) # Build the index using DocstringIndexer

                actual_searcher = indexer.get_searcher() # Get the SummarySearcher instance

                search_query = config.get("docstring_search_query", "example function")
                docstring_search_results_data = actual_searcher.search(search_query, top_k=3) # Perform search using SummarySearcher
                
                with open(os.path.join(full_output_path, "docstring_search_results.json"), "w") as f:
                    json.dump(docstring_search_results_data, f, indent=2)
                _logger.info(f"Completed: Docstring index and search for {relative_output_dir_name}.")
            else:
                _logger.warning(f"Skipping docstring indexing for {relative_output_dir_name} as embedding model '{embed_model_name}' could not be loaded.")

        except ImportError:
            err_msg_import = "Docstring indexing feature requires 'sentence-transformers'. Install with 'pip install sentence-transformers'."
            print_once("sentence_transformers_missing_docstring", err_msg_import, level="warning", _logger=_logger)
            _logger.warning(f"Docstring indexing skipped for {relative_output_dir_name}: 'sentence-transformers' not found.")
            errors.append(f"Docstring indexing skipped for {relative_output_dir_name}: sentence-transformers not found.")
        except Exception as e_doc_index:
            err_msg_doc = f"Docstring indexing feature may be limited or skipped for {relative_output_dir_name}: {e_doc_index}. (Likely missing API key, model issue, or setup problem)."
            print_once("docstring_indexer_failed_" + relative_output_dir_name, err_msg_doc, level="warning", _logger=_logger)
            errors.append(err_msg_doc)
    else:
        _logger.info(f"Skipped: Docstring Indexing and Search for {relative_output_dir_name} as per config.")
    return errors

def _perform_symbol_extraction(repo: Repository, full_output_path: str, relative_output_dir_name: str, config: dict, _logger):
    errors = []
    all_symbols_data = []
    _logger.info("Starting: Extract All Symbols (Python files)")
    if config.get("run_symbol_extraction", True):
        try:
            # Assuming repo.extract_symbols() gives all symbols from python files
            # If it needs specific file types, that should be handled here or in the kit.
            all_symbols_data = repo.extract_symbols()
            
            output_file = os.path.join(full_output_path, "all_python_symbols.json")
            with open(output_file, "w") as f:
                json.dump(all_symbols_data, f, indent=2)
            
            if all_symbols_data:
                _logger.info(f"Completed: Extracted and wrote all Python symbols for {relative_output_dir_name}")
            else:
                _logger.info(f"No Python symbols extracted for {relative_output_dir_name}")
        except Exception as e:
            err_msg = f"Failed: Python symbol extraction for {relative_output_dir_name}: {e}"
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(f"Skipped: Python Symbol Extraction for {relative_output_dir_name} as per config.")
    return all_symbols_data, errors # Return symbols for usage analysis

def _perform_symbol_usage_analysis(repo: Repository, all_symbols_data: list, full_output_path: str, relative_output_dir_name: str, config: dict, _logger):
    errors = []
    _logger.info("Starting: Find Symbol Usages")
    if config.get("run_symbol_usage_analysis", True):
        symbols_output_dir = os.path.join(full_output_path, "symbol_usages")
        os.makedirs(symbols_output_dir, exist_ok=True)
        
        symbols_to_check = config.get("symbols_to_find_usages", [])
        
        # Optionally, add all extracted top-level symbols from the current module if desired
        # extracted_local_symbols = [sym['name'] for sym in all_symbols_data if sym.get('file_path') and not os.path.dirname(sym['file_path'])] # very basic
        # symbols_to_check = list(set(symbols_to_check + extracted_local_symbols))

        if not symbols_to_check:
            _logger.info(f"No symbols configured or extracted for usage analysis in {relative_output_dir_name}.")
        else:
            _logger.info(f"Analyzing usages for {len(symbols_to_check)} configured symbols in {relative_output_dir_name}...")
            for symbol_name in symbols_to_check:
                try:
                    usages = repo.find_symbol_usages(symbol_name) 
                    usage_file_name = f"{symbol_name.replace('.', '_').replace('/', '_')}_usages.json" # Sanitize name
                    with open(os.path.join(symbols_output_dir, usage_file_name), "w") as f:
                        json.dump(usages, f, indent=2)
                    _logger.info(f"  Completed: Found and wrote usages for symbol '{symbol_name}' to {os.path.join(symbols_output_dir, usage_file_name)}")
                except Exception as e_usage:
                    err_msg = f"  Failed to find usages for symbol '{symbol_name}' in {relative_output_dir_name}: {e_usage}"
                    _logger.error(err_msg)
                    errors.append(err_msg)
        _logger.info(f"Completed: Symbol usage search for {relative_output_dir_name}")
    else:
        _logger.info(f"Skipped: Symbol Usage Analysis for {relative_output_dir_name} as per config.")
    return errors

def _perform_text_search_context_extraction(repo: Repository, text_search_results_data: dict, full_output_path: str, relative_output_dir_name: str, config: dict, _logger):
    errors = []
    _logger.info("Starting: Extract Context for Text Search Results")
    if config.get("run_text_search_context_extraction", True):
        if not text_search_results_data:
            _logger.info(f"Skipped: No text search results to extract context from for {relative_output_dir_name}.")
        else:
            try:
                contexts_output_dir = os.path.join(full_output_path, "text_search_contexts")
                os.makedirs(contexts_output_dir, exist_ok=True)
                
                max_contexts = config.get("max_text_search_contexts_to_extract", 1)
                extracted_count = 0

                for query, results in text_search_results_data.items():
                    if not results: continue
                    query_contexts = []
                    for res in results:
                        if extracted_count >= max_contexts: break
                        try:
                            # Assuming kit.Repository has a method to get context.
                            # This is a placeholder for actual kit functionality.
                            # context = repo.get_context_for_match(res['file_path'], res['line_number'], window_size=5) 
                            # For now, we just save the match itself as a pseudo-context
                            file_path = res.get('file_path', 'Unknown_file')
                            line_number = res.get('line_number', 'Unknown_line')
                            context = {"match_info": res, "context_snippet": f"Context for {file_path} line {line_number} (TODO: implement actual context extraction)"}
                            query_contexts.append(context)
                            extracted_count +=1
                        except Exception as e_ctx:
                            _logger.warning(f"Could not extract context for {res.get('file_path', 'N/A')} line {res.get('line_number', 'N/A')}: {e_ctx}")
                    
                    if query_contexts:
                        with open(os.path.join(contexts_output_dir, f"{query}_contexts.json"), "w") as f:
                            json.dump(query_contexts, f, indent=2)
                _logger.info(f"Completed: Extracted context for up to {max_contexts} text search results for {relative_output_dir_name}.")

            except Exception as e:
                err_msg = f"Failed: Text search context extraction for {relative_output_dir_name}: {e}"
                _logger.error(err_msg)
                errors.append(err_msg)
    else:
         _logger.info(f"Skipped: Text Search Context Extraction for {relative_output_dir_name} as per config.")
    return errors

def _perform_chunking_examples(repo: Repository, full_output_path: str, relative_output_dir_name: str, config: dict, _logger):
    errors = []
    _logger.info("Starting: Generate File Chunking Examples")
    if config.get("run_chunking_examples", True):
        chunking_output_dir = os.path.join(full_output_path, "file_chunking_examples")
        os.makedirs(chunking_output_dir, exist_ok=True)
        try:
            # Select files for chunking examples (similar to summarization selection)
            candidate_files = [
                f_info.get('path') for f_info in repo.get_file_tree()
                if f_info.get('path') and not f_info.get('is_dir') and f_info.get('path', '').endswith((".py", ".md", ".txt"))
            ]
            # Simple sort: prefer .py, then by name
            candidate_files.sort(key=lambda x: (0 if x.endswith('.py') else 1, x)) 
            
            files_for_examples = candidate_files[:config.get("max_files_for_chunking_examples", 1)]

            if files_for_examples:
                _logger.info(f"Generating chunking examples for {len(files_for_examples)} files in {relative_output_dir_name}...")
                for file_path_in_repo in files_for_examples:
                    _logger.info(f"  Processing chunks for {file_path_in_repo}")
                    try:
                        # Example: Chunk by lines (customize as needed)
                        line_chunks = repo.chunk_file_by_lines(file_path_in_repo, max_lines=50) # Path relative to repo root
                        # Example: Chunk by symbols (if applicable, e.g. for Python)
                        symbol_chunks = []
                        if file_path_in_repo.endswith('.py'):
                            try:
                                symbol_chunks = repo.chunk_file_by_symbols(file_path_in_repo)
                            except Exception as e_sym_chunk:
                                _logger.warning(f"    Could not generate symbol chunks for {file_path_in_repo}: {e_sym_chunk}")

                        example_data = {
                            "file_path": file_path_in_repo,
                            "line_chunks_example_first_3": line_chunks[:3] if line_chunks else "No line chunks generated or file empty.",
                            "symbol_chunks_example_first_3": symbol_chunks[:3] if symbol_chunks else "No symbol chunks generated or not a Python file."
                        }
                        chunk_file_name = os.path.basename(file_path_in_repo).replace(".", "_") + "_chunking_example.json"
                        with open(os.path.join(chunking_output_dir, chunk_file_name), "w", encoding='utf-8') as f:
                            json.dump(example_data, f, indent=2, default=lambda o: '<not serializable>') # Handle non-serializable if any
                    except FileNotFoundError:
                        _logger.warning(f"  File not found for chunking example: {file_path_in_repo}")
                    except Exception as e_chunk_file:
                        err_msg_chunk =f"    Failed to generate chunking example for {file_path_in_repo}: {e_chunk_file}"
                        _logger.error(err_msg_chunk)
                        errors.append(err_msg_chunk)
                _logger.info(f"Completed: Generated chunking examples for {len(files_for_examples)} files.")
            else:
                _logger.info(f"No suitable files found for generating chunking examples in {relative_output_dir_name}.")

        except Exception as e:
            err_msg = f"Failed: File chunking example generation for {relative_output_dir_name}: {e}"
            _logger.error(err_msg)
            errors.append(err_msg)
    else:
        _logger.info(f"Skipped: File Chunking Examples for {relative_output_dir_name} as per config.")
    return errors


# --- Main Analysis Orchestration Function ---
def analyze_repository_path(path_to_analyze: str, relative_output_dir_name: str, config: dict):
    """
    Runs a suite of kit analyses on the given repository path and saves results.
    Returns a list of error messages encountered.
    """
    global logger # Ensure we use the globally initialized logger
    if not logger:
        # Fallback if called directly without run_full_analysis setting up the logger
        # This isn't ideal, but a safeguard.
        print("[WARN] Logger not initialized in analyze_repository_path. Using basic print.")
        _logger_instance = print 
    else:
        _logger_instance = logger # Use the initialized logger

    all_errors_for_path = []

    full_output_path = os.path.join(BASE_OUTPUT_DIR, relative_output_dir_name)
    os.makedirs(full_output_path, exist_ok=True)
    
    _logger_instance.info(f"----- Starting Analysis for: {path_to_analyze} -----")
    _logger_instance.info(f"Outputting to: {full_output_path}")

    try:
        repo = Repository(path_to_analyze)
        # Determine LLM config once, pass to relevant functions
        llm_model_name = config.get("llm_model_for_summaries", "gpt-4o-mini") # Make configurable if needed elsewhere
        llm_config = OpenAIConfig(model=llm_model_name)

        # 1. Repository Index
        all_errors_for_path.extend(_perform_repository_index(repo, full_output_path, relative_output_dir_name, config, _logger_instance))

        # 2. Dependency Analysis
        all_errors_for_path.extend(_perform_dependency_analysis(repo, full_output_path, relative_output_dir_name, config, _logger_instance))

        # 3. Text Search
        text_search_results, text_search_errors = _perform_text_search(repo, full_output_path, relative_output_dir_name, config, _logger_instance)
        all_errors_for_path.extend(text_search_errors)

        # 4. Code Summarization
        all_errors_for_path.extend(_perform_code_summarization(repo, full_output_path, relative_output_dir_name, config, llm_config, _logger_instance))

        # 5. Docstring Indexing and Search
        all_errors_for_path.extend(_perform_docstring_indexing(repo, full_output_path, relative_output_dir_name, config, llm_config, _logger_instance))
        
        # 6. Extract All Symbols
        all_symbols, symbol_extraction_errors = _perform_symbol_extraction(repo, full_output_path, relative_output_dir_name, config, _logger_instance)
        all_errors_for_path.extend(symbol_extraction_errors)
        
        # 7. Find Symbol Usages
        all_errors_for_path.extend(_perform_symbol_usage_analysis(repo, all_symbols, full_output_path, relative_output_dir_name, config, _logger_instance))
        
        # 8. Extract Context for Text Search Results
        all_errors_for_path.extend(_perform_text_search_context_extraction(repo, text_search_results, full_output_path, relative_output_dir_name, config, _logger_instance))

        # 9. Generate File Chunking Examples
        all_errors_for_path.extend(_perform_chunking_examples(repo, full_output_path, relative_output_dir_name, config, _logger_instance))

    except Exception as e_repo_init:
        err_msg = f"FATAL: Could not initialize Repository for path {path_to_analyze}: {e_repo_init}"
        _logger_instance.error(err_msg)
        all_errors_for_path.append(err_msg)
        # If repo init fails, most other steps are pointless for this path
    
    _logger_instance.info(f"----- Finished analysis for: {path_to_analyze} -----")
    return all_errors_for_path


# --- Main Script Execution ---
def run_full_analysis():
    """
    Main function to orchestrate the analysis of all configured modules and the full repository.
    """
    global logger, PRINTED_ONCE_KEYS
    setup_logging()  # Configure the logging system
    logger = get_logger(__name__)  # Get a logger instance for this script/module
    PRINTED_ONCE_KEYS.clear() # Reset for each full run

    overall_errors = [] # Collect all errors from all analysis runs

    logger.info("--- Starting Codomyrmex Review Script ---")

    # Initial Environment & Dependency Checks
    try:
        logger.info("Running initial environment and dependency checks...")
        # check_and_setup_env_vars() # Assuming .env is loaded or not strictly needed for this script post-load_dotenv
        ensure_core_deps_installed() # Removed logger=logger argument
        logger.info("Environment and dependency checks completed.")
    except Exception as e_env_check:
        logger.error(f"Environment check failed: {e_env_check}. Attempting to continue but some features might be affected.")
        overall_errors.append(f"Environment check failed: {e_env_check}")


    # Clean up old output directory
    if os.path.exists(BASE_OUTPUT_DIR):
        logger.info(f"Removing existing output directory: {BASE_OUTPUT_DIR}")
        try:
            shutil.rmtree(BASE_OUTPUT_DIR)
        except OSError as e:
            logger.error(f"Error removing directory {BASE_OUTPUT_DIR}: {e}. Please check permissions or remove manually.")
            overall_errors.append(f"Error removing directory {BASE_OUTPUT_DIR}: {e}")
            # Decide if script should exit; for now, it will try to continue.
            # sys.exit(1) 
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
    logger.info(f"Created base output directory: {BASE_OUTPUT_DIR}")

    # Analyze each module
    for module_dir_name in MODULE_DIRS:
        module_path = os.path.join(REPO_ROOT_PATH, module_dir_name)
        if not os.path.isdir(module_path):
            logger.warning(f"Module directory not found: {module_path}. Skipping.")
            overall_errors.append(f"Module directory not found: {module_path}")
            continue
        
        # Use module name for output subdirectory (e.g., "ai_code_editing_review")
        output_dir_name_for_module = os.path.basename(module_dir_name).replace('.', '_') + "_review"
        module_errors = analyze_repository_path(module_path, output_dir_name_for_module, ANALYSIS_CONFIG)
        overall_errors.extend(module_errors)

    # Analyze the full repository
    logger.info("----- Starting Analysis for: Full Repository -----")
    full_repo_errors = analyze_repository_path(REPO_ROOT_PATH, "full_repository_review", ANALYSIS_CONFIG)
    overall_errors.extend(full_repo_errors)
    logger.info("----- Finished Analysis for: Full Repository -----")
    
    logger.info("--- Codomyrmex Review Complete ---")
    logger.info(f"All outputs are in: {BASE_OUTPUT_DIR}")

    if overall_errors:
        logger.error("--- Summary of Errors Encountered During Analysis ---")
        for i, err in enumerate(overall_errors):
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
    global PRINTED_ONCE_KEYS, logger # Corrected global declaration
    
    current_logger = _logger if _logger else logger # Use the global logger if _logger is None
    if not current_logger: # Fallback if logger somehow isn't set
        print(f"[PRINT_ONCE FALLBACK - {level.upper()}]: ({key}) {message}")
        return

    if key not in PRINTED_ONCE_KEYS:
        if level == "info":
            current_logger.info(f"({key}) {message}")
        elif level == "warning":
            current_logger.warning(f"({key}) {message}")
        elif level == "error":
            current_logger.error(f"({key}) {message}")
        else: # default to info
            current_logger.info(f"({key}) {message}")
        PRINTED_ONCE_KEYS.add(key)


if __name__ == "__main__":
    load_dotenv() # Load .env file variables into environment
    run_full_analysis() 