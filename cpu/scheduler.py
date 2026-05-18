"""
CPU Scheduler Module
Implements various scheduling algorithms for process management
"""

from collections import deque
from typing import List, Optional
import time


class Scheduler:
    """CPU Scheduler implementing multiple scheduling algorithms"""
    
    def __init__(self, algorithm='round_robin', time_quantum=2):
        """
        Initialize the scheduler
        
        Args:
            algorithm: Scheduling algorithm ('round_robin', 'priority', 'fcfs')
            time_quantum: Time quantum for round robin (in time units)
        """
        self.algorithm = algorithm
        self.time_quantum = time_quantum
        self.ready_queue = deque()
        self.current_process = None
        self.cpu_time = 0
        
    def add_process(self, process):
        """Add a process to the ready queue"""
        if self.algorithm == 'priority':
            # Insert based on priority (lower number = higher priority)
            inserted = False
            temp_queue = deque()
            
            while self.ready_queue:
                proc = self.ready_queue.popleft()
                if not inserted and process.priority < proc.priority:
                    temp_queue.append(process)
                    inserted = True
                temp_queue.append(proc)
            
            if not inserted:
                temp_queue.append(process)
            
            self.ready_queue = temp_queue
        else:
            self.ready_queue.append(process)
            
        process.state = 'READY'
        
    def get_next_process(self) -> Optional[object]:
        """Get the next process to execute"""
        if not self.ready_queue:
            return None
            
        if self.algorithm == 'round_robin' or self.algorithm == 'fcfs':
            return self.ready_queue.popleft()
        elif self.algorithm == 'priority':
            return self.ready_queue.popleft()
        
        return None
    
    def schedule(self) -> Optional[object]:
        """
        Execute scheduling algorithm
        
        Returns:
            The process to run next, or None if queue is empty
        """
        # If current process is done, get next one
        if self.current_process is None or self.current_process.state == 'TERMINATED':
            self.current_process = self.get_next_process()
            
        if self.current_process:
            self.current_process.state = 'RUNNING'
            
        return self.current_process
    
    def execute_cycle(self, cycles=1):
        """
        Execute CPU cycles
        
        Args:
            cycles: Number of CPU cycles to execute
            
        Returns:
            Dictionary with execution statistics
        """
        stats = {
            'process_id': None,
            'cycles_executed': 0,
            'process_completed': False,
            'cpu_time': self.cpu_time
        }
        
        if not self.current_process:
            self.schedule()
            
        if not self.current_process:
            return stats
        
        stats['process_id'] = self.current_process.pid
        
        # Execute the process
        for _ in range(cycles):
            if self.current_process.remaining_time > 0:
                self.current_process.remaining_time -= 1
                self.current_process.cpu_time += 1
                self.cpu_time += 1
                stats['cycles_executed'] += 1
                
                # Check if process is complete
                if self.current_process.remaining_time == 0:
                    self.current_process.state = 'TERMINATED'
                    self.current_process.completion_time = self.cpu_time
                    stats['process_completed'] = True
                    self.current_process = None
                    break
                    
                # For round robin, check time quantum
                if self.algorithm == 'round_robin':
                    if self.current_process.cpu_time % self.time_quantum == 0:
                        # Time quantum expired, move to back of queue
                        self.add_process(self.current_process)
                        self.current_process = None
                        break
        
        stats['cpu_time'] = self.cpu_time
        return stats
    
    def get_stats(self):
        """Get scheduler statistics"""
        return {
            'algorithm': self.algorithm,
            'time_quantum': self.time_quantum,
            'queue_length': len(self.ready_queue),
            'total_cpu_time': self.cpu_time,
            'current_process': self.current_process.pid if self.current_process else None
        }
