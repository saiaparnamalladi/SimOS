"""
Process Control Block (PCB) Module
Manages process information and state
"""

from enum import Enum
from typing import Optional
import time


class ProcessState(Enum):
    """Process states"""
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"


class PCB:
    """Process Control Block - stores process information"""
    
    _next_pid = 1  # Class variable for generating unique PIDs
    
    def __init__(self, name, burst_time, priority=5, memory_required=0):
        """
        Initialize a Process Control Block
        
        Args:
            name: Process name
            burst_time: Total CPU time required
            priority: Process priority (lower number = higher priority)
            memory_required: Memory required in KB
        """
        self.pid = PCB._next_pid
        PCB._next_pid += 1
        
        self.name = name
        self.state = ProcessState.NEW.value
        
        # CPU scheduling information
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.cpu_time = 0
        self.priority = priority
        
        # Memory management
        self.memory_required = memory_required
        self.memory_start = None
        self.page_table_base = None
        
        # Timing information
        self.arrival_time = 0
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        
        # I/O and other information
        self.io_operations = []
        self.parent_pid = None
        self.children_pids = []
        
    def __repr__(self):
        return (f"PCB(PID={self.pid}, Name='{self.name}', State={self.state}, "
                f"Remaining={self.remaining_time}/{self.burst_time})")
    
    def execute(self, time_units=1):
        """
        Execute the process for specified time units
        
        Args:
            time_units: Number of time units to execute
        """
        if self.state != ProcessState.RUNNING.value:
            self.state = ProcessState.RUNNING.value
            
        if self.start_time is None:
            self.start_time = time.time()
            
        executed = min(time_units, self.remaining_time)
        self.remaining_time -= executed
        self.cpu_time += executed
        
        if self.remaining_time == 0:
            self.state = ProcessState.TERMINATED.value
            self.completion_time = time.time()
            
        return executed
    
    def calculate_metrics(self, current_time):
        """Calculate process timing metrics"""
        if self.completion_time:
            self.turnaround_time = self.completion_time - self.arrival_time
            self.waiting_time = self.turnaround_time - self.burst_time
        else:
            # For incomplete processes
            self.waiting_time = current_time - self.arrival_time - self.cpu_time
    
    def get_info(self):
        """Get process information as dictionary"""
        return {
            'pid': self.pid,
            'name': self.name,
            'state': self.state,
            'priority': self.priority,
            'burst_time': self.burst_time,
            'remaining_time': self.remaining_time,
            'cpu_time': self.cpu_time,
            'memory_required': self.memory_required,
            'memory_start': self.memory_start,
            'waiting_time': self.waiting_time,
            'turnaround_time': self.turnaround_time
        }
    
    @staticmethod
    def reset_pid_counter():
        """Reset the PID counter (useful for testing)"""
        PCB._next_pid = 1


class ProcessManager:
    """Manages all processes in the system"""
    
    def __init__(self):
        self.processes = {}
        self.completed_processes = {}
        
    def create_process(self, name, burst_time, priority=5, memory_required=0) -> PCB:
        """
        Create a new process
        
        Args:
            name: Process name
            burst_time: Total CPU time required
            priority: Process priority
            memory_required: Memory required in KB
            
        Returns:
            The created PCB
        """
        pcb = PCB(name, burst_time, priority, memory_required)
        pcb.arrival_time = time.time()
        self.processes[pcb.pid] = pcb
        return pcb
    
    def get_process(self, pid) -> Optional[PCB]:
        """Get process by PID"""
        return self.processes.get(pid) or self.completed_processes.get(pid)
    
    def terminate_process(self, pid) -> bool:
        """
        Terminate a process
        
        Args:
            pid: Process ID
            
        Returns:
            True if successful, False otherwise
        """
        if pid not in self.processes:
            return False
            
        process = self.processes[pid]
        process.state = ProcessState.TERMINATED.value
        process.completion_time = time.time()
        
        # Move to completed processes
        self.completed_processes[pid] = process
        del self.processes[pid]
        
        return True
    
    def get_active_processes(self):
        """Get list of active (non-terminated) processes"""
        return [p for p in self.processes.values() 
                if p.state != ProcessState.TERMINATED.value]
    
    def get_ready_processes(self):
        """Get list of ready processes"""
        return [p for p in self.processes.values() 
                if p.state == ProcessState.READY.value]
    
    def get_stats(self):
        """Get process statistics"""
        active = len(self.processes)
        completed = len(self.completed_processes)
        
        avg_turnaround = 0
        avg_waiting = 0
        
        if completed > 0:
            avg_turnaround = sum(p.turnaround_time for p in self.completed_processes.values()) / completed
            avg_waiting = sum(p.waiting_time for p in self.completed_processes.values()) / completed
            
        return {
            'active_processes': active,
            'completed_processes': completed,
            'total_processes': active + completed,
            'avg_turnaround_time': avg_turnaround,
            'avg_waiting_time': avg_waiting
        }
    
    def list_processes(self):
        """Display all processes"""
        print("\n=== Active Processes ===")
        if not self.processes:
            print("No active processes")
        else:
            print(f"{'PID':<5} {'Name':<15} {'State':<12} {'Priority':<8} {'CPU Time':<10} {'Remaining':<10}")
            print("-" * 70)
            for process in self.processes.values():
                print(f"{process.pid:<5} {process.name:<15} {process.state:<12} "
                      f"{process.priority:<8} {process.cpu_time:<10} {process.remaining_time:<10}")
        
        if self.completed_processes:
            print("\n=== Completed Processes ===")
            print(f"{'PID':<5} {'Name':<15} {'Burst Time':<12} {'Turnaround':<12} {'Waiting':<10}")
            print("-" * 60)
            for process in self.completed_processes.values():
                print(f"{process.pid:<5} {process.name:<15} {process.burst_time:<12} "
                      f"{process.turnaround_time:<12.2f} {process.waiting_time:<10.2f}")
        print()
