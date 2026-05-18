"""
SimOS System Module
Main system class that integrates all OS components
"""

from cpu.scheduler import Scheduler
from memory.allocation import MemoryAllocator
from memory.paging import PagingSystem
from filesystem.file_allocation import FileAllocationSystem
from processes.pcb import ProcessManager, PCB


class SimOS:
    """Main operating system simulator"""
    
    def __init__(self, config=None):
        """
        Initialize the SimOS
        
        Args:
            config: Configuration dictionary with system parameters
        """
        # Default configuration
        default_config = {
            'scheduler_algorithm': 'round_robin',
            'time_quantum': 2,
            'memory_size': 1024,
            'memory_strategy': 'first_fit',
            'disk_size': 1024,
            'block_size': 4,
            'file_strategy': 'contiguous',
            'enable_paging': True,
            'page_size': 4,
            'replacement_algorithm': 'fifo'
        }
        
        # Merge with provided config
        self.config = {**default_config, **(config or {})}
        
        # Initialize components
        self.process_manager = ProcessManager()
        
        self.scheduler = Scheduler(
            algorithm=self.config['scheduler_algorithm'],
            time_quantum=self.config['time_quantum']
        )
        
        self.memory_allocator = MemoryAllocator(
            total_memory=self.config['memory_size'],
            strategy=self.config['memory_strategy']
        )
        
        self.filesystem = FileAllocationSystem(
            disk_size=self.config['disk_size'],
            block_size=self.config['block_size'],
            strategy=self.config['file_strategy']
        )
        
        # Optional paging system
        self.paging_system = None
        if self.config['enable_paging']:
            self.paging_system = PagingSystem(
                physical_memory_size=self.config['memory_size'],
                page_size=self.config['page_size'],
                replacement_algorithm=self.config['replacement_algorithm']
            )
        
        self.clock = 0
        
    def create_process(self, name, burst_time, priority=5, memory_required=0):
        """
        Create a new process
        
        Args:
            name: Process name
            burst_time: CPU burst time
            priority: Process priority
            memory_required: Memory required in KB
            
        Returns:
            Created process PCB
        """
        # Create process
        process = self.process_manager.create_process(
            name, burst_time, priority, memory_required
        )
        
        # Allocate memory if required
        if memory_required > 0:
            if self.paging_system:
                # Use virtual memory
                self.paging_system.create_page_table(process.pid, memory_required)
            else:
                # Direct memory allocation
                addr = self.memory_allocator.allocate(process.pid, memory_required)
                if addr is not None:
                    process.memory_start = addr
                else:
                    print(f"Warning: Could not allocate {memory_required}KB for process {process.pid}")
        
        # Add to scheduler
        self.scheduler.add_process(process)
        
        return process
    
    def kill_process(self, pid):
        """
        Kill a process and free its resources
        
        Args:
            pid: Process ID
            
        Returns:
            True if successful, False otherwise
        """
        process = self.process_manager.get_process(pid)
        if not process:
            return False
        
        # Free memory
        if self.paging_system:
            self.paging_system.free_process_pages(pid)
        else:
            self.memory_allocator.deallocate(pid)
        
        # Terminate process
        return self.process_manager.terminate_process(pid)
    
    def run_cycle(self, cycles=1):
        """
        Run the system for specified cycles
        
        Args:
            cycles: Number of CPU cycles to run
            
        Returns:
            Execution statistics
        """
        stats = self.scheduler.execute_cycle(cycles)
        self.clock += cycles
        
        # Check if process completed
        if stats['process_completed']:
            pid = stats['process_id']
            self.kill_process(pid)
        
        return stats
    
    def run_until_complete(self, max_cycles=1000):
        """
        Run system until all processes complete or max cycles reached
        
        Args:
            max_cycles: Maximum cycles to run
            
        Returns:
            Total cycles executed
        """
        cycles = 0
        
        while cycles < max_cycles:
            stats = self.run_cycle()
            cycles += 1
            
            # Check if any processes remain
            if not self.scheduler.ready_queue and not self.scheduler.current_process:
                break
        
        return cycles
    
    def get_system_stats(self):
        """Get comprehensive system statistics"""
        return {
            'clock': self.clock,
            'processes': self.process_manager.get_stats(),
            'scheduler': self.scheduler.get_stats(),
            'memory': self.memory_allocator.get_stats(),
            'filesystem': self.filesystem.get_stats(),
            'paging': self.paging_system.get_stats() if self.paging_system else None
        }
    
    def display_status(self):
        """Display comprehensive system status"""
        print("\n" + "=" * 60)
        print("SYSTEM STATUS")
        print("=" * 60)
        
        stats = self.get_system_stats()
        
        print(f"\nSystem Clock: {stats['clock']}")
        
        print(f"\n--- PROCESSES ---")
        print(f"Active: {stats['processes']['active_processes']}")
        print(f"Completed: {stats['processes']['completed_processes']}")
        
        print(f"\n--- SCHEDULER ({stats['scheduler']['algorithm']}) ---")
        print(f"Queue Length: {stats['scheduler']['queue_length']}")
        print(f"Current Process: {stats['scheduler']['current_process']}")
        
        print(f"\n--- MEMORY ({stats['memory']['strategy']}) ---")
        print(f"Total: {stats['memory']['total_memory']}KB")
        print(f"Free: {stats['memory']['free_memory']}KB")
        print(f"Allocated: {stats['memory']['allocated_memory']}KB")
        print(f"Utilization: {stats['memory']['utilization']:.2f}%")
        
        print(f"\n--- FILESYSTEM ({stats['filesystem']['strategy']}) ---")
        print(f"Total Files: {stats['filesystem']['total_files']}")
        print(f"Disk Size: {stats['filesystem']['disk_size']}KB")
        print(f"Free Space: {stats['filesystem']['free_space']}KB")
        print(f"Utilization: {stats['filesystem']['utilization']:.2f}%")
        
        if stats['paging']:
            print(f"\n--- PAGING ({stats['paging']['replacement_algorithm']}) ---")
            print(f"Total Frames: {stats['paging']['num_frames']}")
            print(f"Free Frames: {stats['paging']['free_frames']}")
            print(f"Page Faults: {stats['paging']['page_faults']}")
            print(f"Hit Rate: {stats['paging']['hit_rate']:.2f}%")
        
        print("\n" + "=" * 60 + "\n")
    
    def reset(self):
        """Reset the system to initial state"""
        self.__init__(self.config)
