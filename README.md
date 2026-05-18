# SimOS - Simulated Operating System

A comprehensive operating system simulator implementing core OS concepts including process scheduling, memory management, virtual memory with paging, and file allocation.

## Features

### 1. Process Management
- **Process Control Block (PCB)** implementation
- Process states: NEW, READY, RUNNING, WAITING, TERMINATED
- Process statistics and metrics

### 2. CPU Scheduling
- **Round Robin** scheduling with configurable time quantum
- **First Come First Serve (FCFS)**
- **Priority-based** scheduling
- Process execution tracking and statistics

### 3. Memory Management
- **First Fit** allocation
- **Best Fit** allocation
- **Worst Fit** allocation
- Memory block visualization
- Automatic defragmentation

### 4. Virtual Memory (Paging)
- Page table management
- Virtual to physical address translation
- Page replacement algorithms:
  - FIFO (First In First Out)
  - LRU (Least Recently Used)
  - Random replacement
- Page fault tracking and statistics

### 5. File System
- File allocation strategies:
  - **Contiguous** allocation
  - **Linked** allocation
  - **Indexed** allocation
- Disk space management
- File operations (create, delete, read)

## Installation

No external dependencies required! Uses only Python standard library.

```bash
# Clone or download the SimOS directory
cd SimOS
```

## Usage

### Interactive Mode (Default)

Run SimOS with an interactive shell:

```bash
python main.py
```

or

```bash
python main.py --mode interactive
```

### Demo Mode

Run a pre-configured demonstration:

```bash
python main.py --mode demo
```

### Batch Mode

Run with randomly generated processes:

```bash
python main.py --mode batch --num-processes 15
```

## Configuration Options

Customize SimOS behavior with command-line arguments:

```bash
python main.py \
  --scheduler round_robin \
  --memory-strategy first_fit \
  --file-strategy contiguous \
  --memory-size 2048 \
  --disk-size 2048 \
  --time-quantum 3 \
  --page-replacement lru
```

### Available Options

- `--mode`: Execution mode (interactive, demo, batch)
- `--scheduler`: CPU scheduling algorithm (round_robin, fcfs, priority)
- `--memory-strategy`: Memory allocation (first_fit, best_fit, worst_fit)
- `--file-strategy`: File allocation (contiguous, linked, indexed)
- `--memory-size`: Total memory in KB (default: 1024)
- `--disk-size`: Total disk size in KB (default: 1024)
- `--time-quantum`: Time quantum for round robin (default: 2)
- `--page-replacement`: Page replacement algorithm (fifo, lru, random)
- `--no-paging`: Disable virtual memory paging
- `--num-processes`: Number of processes for batch mode (default: 10)

## Interactive Shell Commands

### Process Management
```
create <name> <burst_time> [priority] [memory]  - Create a process
ps                                              - List all processes
kill <pid>                                      - Kill a process
run [cycles]                                    - Run scheduler
```

### Memory Management
```
mem                                             - Show memory status
alloc <pid> <size>                              - Allocate memory
free <pid>                                      - Free process memory
pages                                           - Show page table status
```

### File System
```
ls                                              - List files
mkfile <name> <size>                            - Create a file
rm <name>                                       - Delete a file
disk                                            - Show disk status
```

### System
```
status                                          - Show system status
config                                          - Show configuration
clear                                           - Clear screen
help                                            - Show help
exit/quit                                       - Exit SimOS
```

## Examples

### Example 1: Creating and Running Processes

```
SimOS> create P1 10 5 64
Created process: PID=1, Name='P1'

SimOS> create P2 8 3 128
Created process: PID=2, Name='P2'

SimOS> ps
=== Active Processes ===
PID   Name            State        Priority CPU Time   Remaining 
----------------------------------------------------------------------
1     P1              READY        5        0          10        
2     P2              READY        3        0          8         

SimOS> run 5
Running scheduler for 5 cycle(s)...
Cycle 1: Process 1 executed (1 units)
Cycle 2: Process 1 executed (1 units)
Cycle 3: Process 2 executed (1 units)
Cycle 4: Process 2 executed (1 units)
Cycle 5: Process 1 executed (1 units)
```

### Example 2: Memory Management

```
SimOS> mem
=== Memory Map ===
Block[0:1023] 1024KB - FREE

Total: 1024KB
Free: 1024KB | Allocated: 0KB
Utilization: 0.00%

SimOS> alloc 1 256
Allocated 256KB at address 0 for process 1

SimOS> mem
=== Memory Map ===
Block[0:255] 256KB - ALLOCATED (PID: 1)
Block[256:1023] 768KB - FREE

Total: 1024KB
Free: 768KB | Allocated: 256KB
Utilization: 25.00%
```

### Example 3: File System Operations

```
SimOS> mkfile document.txt 32
Created file 'document.txt' (32KB)

SimOS> mkfile image.jpg 64
Created file 'image.jpg' (64KB)

SimOS> ls
=== File List ===
document.txt: 32KB, Blocks: [0, 1, 2, 3, 4, 5, 6, 7]
image.jpg: 64KB, Blocks: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

SimOS> disk
=== Disk Allocation Map ===
Strategy: contiguous
Block size: 4KB

Blocks   0- 15: D D D D D D D D I I I I I I I I 
Blocks  16- 31: I I I I I I I I . . . . . . . . 
...
```

## Project Structure

```
SimOS/
├── cpu/
│   └── scheduler.py          # CPU scheduling algorithms
├── memory/
│   ├── allocation.py         # Memory allocation strategies
│   └── paging.py             # Virtual memory and paging
├── filesystem/
│   └── file_allocation.py    # File allocation strategies
├── processes/
│   └── pcb.py                # Process Control Block
├── shell/
│   └── shell.py              # Interactive shell interface
├── system.py                 # Main system integration
├── utils.py                  # Utility functions
├── main.py                   # Entry point
└── README.md                 # This file
```

## Learning Outcomes

This simulator helps understand:

1. **Process Scheduling**: How different algorithms affect process execution
2. **Memory Management**: Trade-offs between allocation strategies
3. **Virtual Memory**: Address translation and page replacement
4. **File Systems**: Different file allocation methods and their impacts
5. **OS Integration**: How different OS components work together

## Educational Use

SimOS is designed for:
- Operating Systems courses
- Self-study of OS concepts
- Algorithm comparison and analysis
- Understanding OS trade-offs

## Future Enhancements

Potential additions:
- Thread management
- Deadlock detection and prevention
- Inter-process communication
- Device drivers simulation
- Network stack simulation
- Security and access control

## License

Educational use - Feel free to modify and extend!

## Contributing

This is an educational project. Contributions welcome:
- Bug fixes
- New scheduling algorithms
- Additional memory management strategies
- Enhanced visualization
- Performance optimizations

---

**Author**: SimOS Development Team  
**Version**: 1.0  
**Purpose**: Educational Operating System Simulator
