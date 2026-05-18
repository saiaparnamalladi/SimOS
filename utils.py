"""
Utility Functions for SimOS
Helper functions and utilities
"""

import random
from processes.pcb import PCB


def generate_random_processes(num_processes, min_burst=1, max_burst=20, 
                              min_memory=0, max_memory=100):
    """
    Generate random test processes
    
    Args:
        num_processes: Number of processes to generate
        min_burst: Minimum burst time
        max_burst: Maximum burst time
        min_memory: Minimum memory requirement
        max_memory: Maximum memory requirement
        
    Returns:
        List of process configurations
    """
    processes = []
    
    for i in range(num_processes):
        process = {
            'name': f'P{i+1}',
            'burst_time': random.randint(min_burst, max_burst),
            'priority': random.randint(1, 10),
            'memory': random.randint(min_memory, max_memory)
        }
        processes.append(process)
    
    return processes


def generate_test_files(num_files, min_size=4, max_size=64):
    """
    Generate random test files
    
    Args:
        num_files: Number of files to generate
        min_size: Minimum file size in KB
        max_size: Maximum file size in KB
        
    Returns:
        List of file configurations
    """
    files = []
    
    for i in range(num_files):
        file_info = {
            'name': f'file{i+1}.txt',
            'size': random.randint(min_size, max_size)
        }
        files.append(file_info)
    
    return files


def calculate_scheduling_metrics(processes):
    """
    Calculate scheduling performance metrics
    
    Args:
        processes: List of completed PCB objects
        
    Returns:
        Dictionary of metrics
    """
    if not processes:
        return {}
    
    total_turnaround = sum(p.turnaround_time for p in processes)
    total_waiting = sum(p.waiting_time for p in processes)
    total_burst = sum(p.burst_time for p in processes)
    
    return {
        'avg_turnaround_time': total_turnaround / len(processes),
        'avg_waiting_time': total_waiting / len(processes),
        'avg_burst_time': total_burst / len(processes),
        'throughput': len(processes) / total_turnaround if total_turnaround > 0 else 0,
        'cpu_utilization': (total_burst / total_turnaround * 100) if total_turnaround > 0 else 0
    }


def print_gantt_chart(execution_history, max_width=80):
    """
    Print a simple Gantt chart of process execution
    
    Args:
        execution_history: List of (time, process_id) tuples
        max_width: Maximum width of the chart
    """
    if not execution_history:
        print("No execution history available")
        return
    
    print("\n=== Gantt Chart ===")
    
    # Group consecutive executions of the same process
    groups = []
    current_pid = None
    start_time = 0
    
    for time, pid in execution_history:
        if pid != current_pid:
            if current_pid is not None:
                groups.append((current_pid, start_time, time - 1))
            current_pid = pid
            start_time = time
    
    if current_pid is not None:
        groups.append((current_pid, start_time, len(execution_history) - 1))
    
    # Print the chart
    for pid, start, end in groups:
        duration = end - start + 1
        bar_length = min(duration, max_width - 20)
        bar = '█' * bar_length
        print(f"P{pid:2d} [{start:3d}-{end:3d}] {bar}")
    
    print()


def format_memory_size(size_kb):
    """
    Format memory size in human-readable format
    
    Args:
        size_kb: Size in KB
        
    Returns:
        Formatted string
    """
    if size_kb < 1024:
        return f"{size_kb}KB"
    elif size_kb < 1024 * 1024:
        return f"{size_kb / 1024:.2f}MB"
    else:
        return f"{size_kb / (1024 * 1024):.2f}GB"


def print_table(headers, rows, column_widths=None):
    """
    Print a formatted table
    
    Args:
        headers: List of header strings
        rows: List of row lists
        column_widths: Optional list of column widths
    """
    if not column_widths:
        # Auto-calculate widths
        column_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                column_widths[i] = max(column_widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, column_widths))
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        row_line = " | ".join(str(cell).ljust(w) for cell, w in zip(row, column_widths))
        print(row_line)


def validate_config(config):
    """
    Validate system configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_keys = [
        'scheduler_algorithm', 'memory_size', 'disk_size'
    ]
    
    for key in required_keys:
        if key not in config:
            return False, f"Missing required configuration: {key}"
    
    # Validate values
    if config.get('memory_size', 0) <= 0:
        return False, "Memory size must be positive"
    
    if config.get('disk_size', 0) <= 0:
        return False, "Disk size must be positive"
    
    valid_algorithms = ['round_robin', 'fcfs', 'priority']
    if config.get('scheduler_algorithm') not in valid_algorithms:
        return False, f"Invalid scheduler algorithm. Must be one of: {valid_algorithms}"
    
    valid_mem_strategies = ['first_fit', 'best_fit', 'worst_fit']
    if config.get('memory_strategy') not in valid_mem_strategies:
        return False, f"Invalid memory strategy. Must be one of: {valid_mem_strategies}"
    
    valid_file_strategies = ['contiguous', 'linked', 'indexed']
    if config.get('file_strategy') not in valid_file_strategies:
        return False, f"Invalid file strategy. Must be one of: {valid_file_strategies}"
    
    return True, None


def create_demo_scenario(system):
    """
    Create a demo scenario with sample processes and files
    
    Args:
        system: SimOS instance
    """
    print("Creating demo scenario...")
    
    # Create processes
    processes = [
        ('Browser', 10, 3, 128),
        ('Editor', 8, 2, 64),
        ('Compiler', 15, 5, 256),
        ('Player', 6, 4, 96)
    ]
    
    for name, burst, priority, memory in processes:
        system.create_process(name, burst, priority, memory)
        print(f"  Created process: {name}")
    
    # Create files
    files = [
        ('document.txt', 16),
        ('image.jpg', 48),
        ('video.mp4', 128),
        ('code.py', 8)
    ]
    
    for filename, size in files:
        system.filesystem.allocate_file(filename, size)
        print(f"  Created file: {filename}")
    
    print("Demo scenario ready!\n")


def export_stats_to_dict(system):
    """
    Export all system statistics to a dictionary
    
    Args:
        system: SimOS instance
        
    Returns:
        Dictionary with all statistics
    """
    return {
        'timestamp': system.clock,
        'processes': system.process_manager.get_stats(),
        'scheduler': system.scheduler.get_stats(),
        'memory': system.memory_allocator.get_stats(),
        'filesystem': system.filesystem.get_stats(),
        'paging': system.paging_system.get_stats() if system.paging_system else None
    }
