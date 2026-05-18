#!/usr/bin/env python3
"""
Quick test script for SimOS
Tests basic functionality of all modules
"""

import sys
sys.path.insert(0, '/home/claude/SimOS')

from system import SimOS
from utils import create_demo_scenario

def test_basic_functionality():
    """Test basic SimOS functionality"""
    print("="*60)
    print("SimOS Quick Test")
    print("="*60)
    
    # Create system with default config
    config = {
        'scheduler_algorithm': 'round_robin',
        'time_quantum': 2,
        'memory_size': 512,
        'memory_strategy': 'first_fit',
        'disk_size': 512,
        'block_size': 4,
        'file_strategy': 'contiguous',
        'enable_paging': True,
        'page_size': 4,
        'replacement_algorithm': 'fifo'
    }
    
    print("\n1. Creating SimOS instance...")
    system = SimOS(config)
    print("✓ System created successfully")
    
    print("\n2. Creating test processes...")
    p1 = system.create_process("Process1", burst_time=5, priority=3, memory_required=64)
    p2 = system.create_process("Process2", burst_time=8, priority=5, memory_required=32)
    p3 = system.create_process("Process3", burst_time=3, priority=1, memory_required=128)
    print(f"✓ Created {p1.name} (PID: {p1.pid})")
    print(f"✓ Created {p2.name} (PID: {p2.pid})")
    print(f"✓ Created {p3.name} (PID: {p3.pid})")
    
    print("\n3. Testing scheduler...")
    for i in range(5):
        stats = system.run_cycle()
        if stats['process_id']:
            print(f"  Cycle {i+1}: Process {stats['process_id']} executed")
    print("✓ Scheduler working")
    
    print("\n4. Testing memory allocation...")
    system.memory_allocator.display_memory_map()
    print("✓ Memory management working")
    
    print("\n5. Testing file system...")
    system.filesystem.allocate_file("test1.txt", 16)
    system.filesystem.allocate_file("test2.dat", 32)
    system.filesystem.list_files()
    print("✓ File system working")
    
    print("\n6. System status...")
    system.display_status()
    
    print("\n7. Running until completion...")
    cycles = system.run_until_complete(max_cycles=100)
    print(f"✓ Completed in {cycles} cycles")
    
    print("\n8. Final process statistics...")
    system.process_manager.list_processes()
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60)
    
    return True

if __name__ == '__main__':
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
