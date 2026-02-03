#!/usr/bin/env python3
"""
Streaming Demo Script

Demonstrates streaming response handlers for real-time LLM output processing.
Shows patterns for handling chunked responses efficiently.

Features:
    - Streaming response simulation
    - Token-by-token processing
    - Progress indicators
    - Buffer management
"""

import sys
import time
from pathlib import Path
from typing import Iterator, Callable, Optional
from dataclasses import dataclass

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_warning


@dataclass
class StreamChunk:
    """A chunk from a streaming response."""
    content: str
    is_final: bool = False
    token_count: int = 0


class StreamBuffer:
    """Buffer for accumulating streaming content."""
    
    def __init__(self, flush_threshold: int = 100):
        self.buffer = ""
        self.total_received = 0
        self.flush_threshold = flush_threshold
        self.callbacks: list[Callable[[str], None]] = []
    
    def add_callback(self, callback: Callable[[str], None]):
        """Add a callback to be called on each chunk."""
        self.callbacks.append(callback)
    
    def write(self, chunk: StreamChunk):
        """Write a chunk to the buffer."""
        self.buffer += chunk.content
        self.total_received += len(chunk.content)
        
        # Notify callbacks
        for callback in self.callbacks:
            callback(chunk.content)
        
        # Auto-flush if threshold reached
        if len(self.buffer) >= self.flush_threshold:
            self.flush()
    
    def flush(self) -> str:
        """Flush and return buffer contents."""
        content = self.buffer
        self.buffer = ""
        return content
    
    def get_all(self) -> str:
        """Get all accumulated content."""
        return self.buffer


def simulate_streaming_response(text: str, delay: float = 0.02) -> Iterator[StreamChunk]:
    """Simulate a streaming LLM response.
    
    Args:
        text: The full response text to stream
        delay: Delay between chunks (seconds)
        
    Yields:
        StreamChunk objects
    """
    words = text.split()
    
    for i, word in enumerate(words):
        # Add space between words
        content = word + (" " if i < len(words) - 1 else "")
        
        yield StreamChunk(
            content=content,
            is_final=(i == len(words) - 1),
            token_count=1
        )
        
        time.sleep(delay)


def demo_basic_streaming():
    """Demonstrate basic streaming output."""
    print_info("📡 Basic Streaming Demo\n")
    
    response_text = """The quick brown fox jumps over the lazy dog. 
    This is a demonstration of streaming text output, 
    where each word appears one at a time to simulate 
    real-time LLM response streaming."""
    
    print("  Streaming response:")
    print("  " + "-" * 50)
    print("  ", end="", flush=True)
    
    total_tokens = 0
    for chunk in simulate_streaming_response(response_text, delay=0.03):
        print(chunk.content, end="", flush=True)
        total_tokens += chunk.token_count
    
    print("\n  " + "-" * 50)
    print(f"\n  Total tokens: {total_tokens}")
    print()


def demo_buffered_streaming():
    """Demonstrate buffered streaming with callbacks."""
    print_info("💾 Buffered Streaming Demo\n")
    
    response_text = """Machine learning enables computers to learn from data 
    and improve their performance over time without being explicitly programmed. 
    This paradigm has revolutionized many fields including computer vision, 
    natural language processing, and robotics."""
    
    buffer = StreamBuffer(flush_threshold=50)
    
    # Track progress
    chunks_received = []
    
    def on_chunk(content: str):
        chunks_received.append(content)
    
    buffer.add_callback(on_chunk)
    
    print("  Processing stream with buffer...")
    print("  " + "-" * 50)
    
    for chunk in simulate_streaming_response(response_text, delay=0.02):
        buffer.write(chunk)
        print(chunk.content, end="", flush=True)
    
    print("\n  " + "-" * 50)
    
    final_content = buffer.get_all()
    print(f"\n  Chunks received: {len(chunks_received)}")
    print(f"  Total characters: {buffer.total_received}")
    print()


def demo_progress_indicator():
    """Demonstrate streaming with progress indicator."""
    print_info("📊 Progress Indicator Demo\n")
    
    response_text = """This response demonstrates a progress indicator 
    that shows completion percentage as the stream arrives. 
    Each chunk updates the progress bar until complete."""
    
    words = response_text.split()
    total = len(words)
    
    print("  Generating with progress:")
    print("  " + "-" * 50)
    
    current = 0
    for chunk in simulate_streaming_response(response_text, delay=0.05):
        current += 1
        progress = (current / total) * 100
        bar_length = 20
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Print progress bar on same line
        print(f"\r  [{bar}] {progress:5.1f}%", end="", flush=True)
    
    print("\n  " + "-" * 50)
    print_success("\n  ✅ Streaming complete!")
    print()


def demo_streaming_with_processing():
    """Demonstrate streaming with real-time processing."""
    print_info("⚙️ Real-time Processing Demo\n")
    
    response_text = """Python is a versatile programming language. 
    It supports multiple paradigms. Machine learning is easy with Python. 
    The community is very active. Libraries like NumPy are powerful."""
    
    print("  Processing stream in real-time:")
    print("  (Counting sentences as they arrive)")
    print("  " + "-" * 50)
    
    sentence_count = 0
    word_count = 0
    char_count = 0
    current_sentence = ""
    
    for chunk in simulate_streaming_response(response_text, delay=0.03):
        print(chunk.content, end="", flush=True)
        current_sentence += chunk.content
        word_count += 1
        char_count += len(chunk.content)
        
        # Detect sentence end
        if ". " in chunk.content or chunk.is_final:
            sentence_count += 1
    
    print("\n  " + "-" * 50)
    print(f"\n  Real-time statistics:")
    print(f"    Sentences: {sentence_count}")
    print(f"    Words: {word_count}")
    print(f"    Characters: {char_count}")
    print()


def demo_streaming_error_handling():
    """Demonstrate error handling in streams."""
    print_info("🚨 Error Handling Demo\n")
    
    print("  Simulating stream with potential errors:")
    print("  " + "-" * 50)
    
    def error_prone_stream() -> Iterator[StreamChunk]:
        words = ["Everything", "is", "fine", "<ERROR>", "recovered", "now."]
        for i, word in enumerate(words):
            if word == "<ERROR>":
                # Simulate recoverable error
                yield StreamChunk(content="[stream interrupted]", is_final=False)
                time.sleep(0.1)
                yield StreamChunk(content=" ", is_final=False)
            else:
                yield StreamChunk(
                    content=word + (" " if i < len(words) - 1 else ""),
                    is_final=(i == len(words) - 1)
                )
            time.sleep(0.05)
    
    print("  ", end="")
    error_count = 0
    for chunk in error_prone_stream():
        if "[stream interrupted]" in chunk.content:
            error_count += 1
            print(f"\033[93m{chunk.content}\033[0m", end="")  # Yellow warning inline
        else:
            print(chunk.content, end="", flush=True)
    
    print("\n  " + "-" * 50)
    print(f"\n  Errors handled: {error_count}")
    print_success("  Stream completed despite errors")
    print()


def main():
    """Main demonstration."""
    setup_logging()
    print("=" * 60)
    print("  Streaming Demo - Real-time LLM Output Processing")
    print("=" * 60)
    print()
    
    demo_basic_streaming()
    demo_buffered_streaming()
    demo_progress_indicator()
    demo_streaming_with_processing()
    demo_streaming_error_handling()
    
    print_success("✅ All demos completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
