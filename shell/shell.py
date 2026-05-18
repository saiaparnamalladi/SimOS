"""
Shell Module
Interactive command-line interface for SimOS
"""

import sys


class Shell:
    """Command-line interface for SimOS"""
    
    def __init__(self, system):
        """
        Initialize the shell
        
        Args:
            system: Reference to the SimOS system
        """
        self.system = system
        self.running = False
        self.commands = {
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            
            # Process commands
            'create': self.cmd_create_process,
            'ps': self.cmd_list_processes,
            'kill': self.cmd_kill_process,
            'run': self.cmd_run_scheduler,
            
            # Memory commands
            'mem': self.cmd_memory_status,
            'alloc': self.cmd_allocate_memory,
            'free': self.cmd_free_memory,
            'pages': self.cmd_page_status,
            
            # Filesystem commands
            'ls': self.cmd_list_files,
            'mkfile': self.cmd_create_file,
            'rm': self.cmd_delete_file,
            'disk': self.cmd_disk_status,
            
            # System commands
            'status': self.cmd_system_status,
            'config': self.cmd_show_config,
            'clear': self.cmd_clear,
        }
        
    def start(self):
        """Start the shell"""
        self.running = True
        print("=" * 60)
        print("SimOS - Simulated Operating System")
        print("=" * 60)
        print("Type 'help' for available commands")
        print()
        
        while self.running:
            try:
                command_line = input("SimOS> ").strip()
                if command_line:
                    self.execute_command(command_line)
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nExiting SimOS...")
    
    def execute_command(self, command_line):
        """Execute a command"""
        parts = command_line.split()
        command = parts[0].lower()
        args = parts[1:]
        
        if command in self.commands:
            self.commands[command](args)
        else:
            print(f"Unknown command: {command}")
            print("Type 'help' for available commands")
    
    # Command implementations
    
    def cmd_help(self, args):
        """Show help information"""
        print("\n=== SimOS Commands ===")
        print("\nProcess Management:")
        print("  create <name> <burst_time> [priority] [memory] - Create a process")
        print("  ps                                              - List all processes")
        print("  kill <pid>                                      - Kill a process")
        print("  run [cycles]                                    - Run scheduler")
        
        print("\nMemory Management:")
        print("  mem                                             - Show memory status")
        print("  alloc <pid> <size>                              - Allocate memory")
        print("  free <pid>                                      - Free process memory")
        print("  pages                                           - Show page table status")
        
        print("\nFilesystem:")
        print("  ls                                              - List files")
        print("  mkfile <name> <size>                            - Create a file")
        print("  rm <name>                                       - Delete a file")
        print("  disk                                            - Show disk status")
        
        print("\nSystem:")
        print("  status                                          - Show system status")
        print("  config                                          - Show configuration")
        print("  clear                                           - Clear screen")
        print("  help                                            - Show this help")
        print("  exit/quit                                       - Exit SimOS")
        print()
    
    def cmd_exit(self, args):
        """Exit the shell"""
        self.running = False
    
    def cmd_create_process(self, args):
        """Create a new process"""
        if len(args) < 2:
            print("Usage: create <name> <burst_time> [priority] [memory]")
            return
            
        name = args[0]
        try:
            burst_time = int(args[1])
            priority = int(args[2]) if len(args) > 2 else 5
            memory = int(args[3]) if len(args) > 3 else 0
            
            process = self.system.create_process(name, burst_time, priority, memory)
            print(f"Created process: PID={process.pid}, Name='{name}'")
            
        except ValueError:
            print("Error: Invalid numeric value")
    
    def cmd_list_processes(self, args):
        """List all processes"""
        self.system.process_manager.list_processes()
    
    def cmd_kill_process(self, args):
        """Kill a process"""
        if len(args) < 1:
            print("Usage: kill <pid>")
            return
            
        try:
            pid = int(args[0])
            if self.system.kill_process(pid):
                print(f"Process {pid} terminated")
            else:
                print(f"Error: Process {pid} not found")
        except ValueError:
            print("Error: Invalid PID")
    
    def cmd_run_scheduler(self, args):
        """Run the scheduler"""
        cycles = int(args[0]) if args else 1
        
        print(f"\nRunning scheduler for {cycles} cycle(s)...")
        for i in range(cycles):
            stats = self.system.run_cycle()
            if stats['process_id']:
                print(f"Cycle {i+1}: Process {stats['process_id']} executed "
                      f"({stats['cycles_executed']} units)")
                if stats['process_completed']:
                    print(f"  -> Process {stats['process_id']} completed!")
            else:
                print(f"Cycle {i+1}: No process to execute")
        print()
    
    def cmd_memory_status(self, args):
        """Show memory status"""
        self.system.memory_allocator.display_memory_map()
    
    def cmd_allocate_memory(self, args):
        """Allocate memory for a process"""
        if len(args) < 2:
            print("Usage: alloc <pid> <size>")
            return
            
        try:
            pid = int(args[0])
            size = int(args[1])
            
            process = self.system.process_manager.get_process(pid)
            if not process:
                print(f"Error: Process {pid} not found")
                return
                
            addr = self.system.memory_allocator.allocate(pid, size)
            if addr is not None:
                process.memory_start = addr
                print(f"Allocated {size}KB at address {addr} for process {pid}")
            else:
                print(f"Error: Could not allocate {size}KB")
                
        except ValueError:
            print("Error: Invalid numeric value")
    
    def cmd_free_memory(self, args):
        """Free process memory"""
        if len(args) < 1:
            print("Usage: free <pid>")
            return
            
        try:
            pid = int(args[0])
            if self.system.memory_allocator.deallocate(pid):
                print(f"Freed memory for process {pid}")
            else:
                print(f"Error: No memory allocated for process {pid}")
        except ValueError:
            print("Error: Invalid PID")
    
    def cmd_page_status(self, args):
        """Show paging status"""
        if self.system.paging_system:
            self.system.paging_system.display_frame_table()
            stats = self.system.paging_system.get_stats()
            print(f"Page Faults: {stats['page_faults']}, Hits: {stats['page_hits']}, "
                  f"Hit Rate: {stats['hit_rate']:.2f}%")
        else:
            print("Paging not enabled")
    
    def cmd_list_files(self, args):
        """List files"""
        self.system.filesystem.list_files()
    
    def cmd_create_file(self, args):
        """Create a file"""
        if len(args) < 2:
            print("Usage: mkfile <name> <size>")
            return
            
        try:
            name = args[0]
            size = int(args[1])
            
            if self.system.filesystem.allocate_file(name, size):
                print(f"Created file '{name}' ({size}KB)")
            else:
                print(f"Error: Could not create file '{name}'")
                
        except ValueError:
            print("Error: Invalid size")
    
    def cmd_delete_file(self, args):
        """Delete a file"""
        if len(args) < 1:
            print("Usage: rm <name>")
            return
            
        name = args[0]
        if self.system.filesystem.delete_file(name):
            print(f"Deleted file '{name}'")
    
    def cmd_disk_status(self, args):
        """Show disk status"""
        self.system.filesystem.display_disk_map()
    
    def cmd_system_status(self, args):
        """Show overall system status"""
        print("\n=== System Status ===")
        
        # Process stats
        proc_stats = self.system.process_manager.get_stats()
        print(f"\nProcesses: {proc_stats['active_processes']} active, "
              f"{proc_stats['completed_processes']} completed")
        
        # Memory stats
        mem_stats = self.system.memory_allocator.get_stats()
        print(f"\nMemory: {mem_stats['allocated_memory']}KB used, "
              f"{mem_stats['free_memory']}KB free ({mem_stats['utilization']:.1f}% utilization)")
        
        # Filesystem stats
        fs_stats = self.system.filesystem.get_stats()
        print(f"\nDisk: {fs_stats['used_space']}KB used, "
              f"{fs_stats['free_space']}KB free ({fs_stats['utilization']:.1f}% utilization)")
        
        # Scheduler stats
        sched_stats = self.system.scheduler.get_stats()
        print(f"\nScheduler: {sched_stats['algorithm']}, "
              f"{sched_stats['queue_length']} processes in queue")
        
        print()
    
    def cmd_show_config(self, args):
        """Show system configuration"""
        print("\n=== System Configuration ===")
        print(f"\nScheduling Algorithm: {self.system.scheduler.algorithm}")
        print(f"Time Quantum: {self.system.scheduler.time_quantum}")
        print(f"\nMemory Allocation Strategy: {self.system.memory_allocator.strategy}")
        print(f"Total Memory: {self.system.memory_allocator.total_memory}KB")
        print(f"\nFile Allocation Strategy: {self.system.filesystem.strategy}")
        print(f"Disk Size: {self.system.filesystem.disk_size}KB")
        print(f"Block Size: {self.system.filesystem.block_size}KB")
        
        if self.system.paging_system:
            paging_stats = self.system.paging_system.get_stats()
            print(f"\nPaging: Enabled")
            print(f"Page Replacement: {paging_stats['replacement_algorithm']}")
            print(f"Total Frames: {paging_stats['num_frames']}")
        else:
            print(f"\nPaging: Disabled")
        
        print()
    
    def cmd_clear(self, args):
        """Clear the screen"""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
