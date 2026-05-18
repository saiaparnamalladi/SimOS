#!/usr/bin/env python3
"""
SimOS - Simulated Operating System
Main entry point

Author: SimOS Development Team
Version: 1.0
"""

import sys
import argparse
from system import SimOS
from shell.shell import Shell
from utils import create_demo_scenario, generate_random_processes


def run_interactive_mode(config):
    """Run SimOS in interactive shell mode"""
    system = SimOS(config)
    shell = Shell(system)
    shell.start()


def run_demo_mode(config):
    """Run a demonstration of SimOS features"""
    print("\n" + "="*60)
    print("SimOS Demonstration Mode")
    print("="*60 + "\n")
    
    # Create system with specified config
    system = SimOS(config)
    
    # Show initial configuration
    print("System Configuration:")
    print(f"  Scheduler: {config['scheduler_algorithm']}")
    print(f"  Memory: {config['memory_size']}KB ({config['memory_strategy']})")
    print(f"  Filesystem: {config['disk_size']}KB ({config['file_strategy']})")
    print(f"  Paging: {'Enabled' if config['enable_paging'] else 'Disabled'}")
    print()
    
    # Create demo scenario
    create_demo_scenario(system)
    
    # Show initial status
    print("\n--- Initial System Status ---")
    system.display_status()
    
    # Run simulation
    print("Running simulation...")
    input("Press Enter to start execution...")
    
    cycle_count = 0
    max_cycles = 50
    
    while cycle_count < max_cycles:
        stats = system.run_cycle()
        cycle_count += 1
        
        if stats['process_id']:
            print(f"Cycle {cycle_count}: Process {stats['process_id']} executing...")
            if stats['process_completed']:
                print(f"  -> Process {stats['process_id']} completed!")
        else:
            print(f"Cycle {cycle_count}: CPU idle")
        
        # Check if all processes are done
        if (not system.scheduler.ready_queue and 
            not system.scheduler.current_process and
            len(system.process_manager.processes) == 0):
            print("\nAll processes completed!")
            break
        
        # Show status every 10 cycles
        if cycle_count % 10 == 0:
            print(f"\n--- Status at Cycle {cycle_count} ---")
            system.display_status()
            input("Press Enter to continue...")
    
    # Final status
    print("\n--- Final System Status ---")
    system.display_status()
    
    # Show process statistics
    system.process_manager.list_processes()
    
    # Show memory map
    system.memory_allocator.display_memory_map()
    
    # Show disk map
    system.filesystem.display_disk_map()
    
    print("\nDemo completed!")


def run_batch_mode(config, num_processes=10):
    """Run SimOS in batch mode with random processes"""
    print("\n" + "="*60)
    print("SimOS Batch Mode")
    print("="*60 + "\n")
    
    system = SimOS(config)
    
    # Generate random processes
    print(f"Generating {num_processes} random processes...")
    processes = generate_random_processes(num_processes, min_burst=5, max_burst=20,
                                         min_memory=32, max_memory=128)
    
    # Create processes
    for proc in processes:
        system.create_process(proc['name'], proc['burst_time'], 
                            proc['priority'], proc['memory'])
        print(f"  Created: {proc['name']} (Burst: {proc['burst_time']}, "
              f"Priority: {proc['priority']}, Memory: {proc['memory']}KB)")
    
    print()
    
    # Run until completion
    print("Running simulation...")
    cycles = system.run_until_complete(max_cycles=1000)
    
    print(f"\nSimulation completed in {cycles} cycles")
    
    # Show final statistics
    system.display_status()
    system.process_manager.list_processes()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='SimOS - Simulated Operating System')
    
    parser.add_argument('--mode', choices=['interactive', 'demo', 'batch'],
                       default='interactive',
                       help='Execution mode (default: interactive)')
    
    parser.add_argument('--scheduler', choices=['round_robin', 'fcfs', 'priority'],
                       default='round_robin',
                       help='CPU scheduling algorithm')
    
    parser.add_argument('--memory-strategy', choices=['first_fit', 'best_fit', 'worst_fit'],
                       default='first_fit',
                       help='Memory allocation strategy')
    
    parser.add_argument('--file-strategy', choices=['contiguous', 'linked', 'indexed'],
                       default='contiguous',
                       help='File allocation strategy')
    
    parser.add_argument('--memory-size', type=int, default=1024,
                       help='Total memory size in KB')
    
    parser.add_argument('--disk-size', type=int, default=1024,
                       help='Total disk size in KB')
    
    parser.add_argument('--time-quantum', type=int, default=2,
                       help='Time quantum for round robin scheduling')
    
    parser.add_argument('--no-paging', action='store_true',
                       help='Disable paging system')
    
    parser.add_argument('--page-replacement', choices=['fifo', 'lru', 'random'],
                       default='fifo',
                       help='Page replacement algorithm')
    
    parser.add_argument('--num-processes', type=int, default=10,
                       help='Number of processes for batch mode')
    
    args = parser.parse_args()
    
    # Build configuration
    config = {
        'scheduler_algorithm': args.scheduler,
        'time_quantum': args.time_quantum,
        'memory_size': args.memory_size,
        'memory_strategy': args.memory_strategy,
        'disk_size': args.disk_size,
        'block_size': 4,
        'file_strategy': args.file_strategy,
        'enable_paging': not args.no_paging,
        'page_size': 4,
        'replacement_algorithm': args.page_replacement
    }
    
    try:
        if args.mode == 'interactive':
            run_interactive_mode(config)
        elif args.mode == 'demo':
            run_demo_mode(config)
        elif args.mode == 'batch':
            run_batch_mode(config, args.num_processes)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
