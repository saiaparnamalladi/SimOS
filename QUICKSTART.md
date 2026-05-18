# SimOS Quick Start Guide

## Installation

1. Extract the SimOS.tar.gz archive:
```bash
tar -xzf SimOS.tar.gz
cd SimOS
```

2. No dependencies needed! Uses only Python 3 standard library.

## Quick Start Examples

### 1. Interactive Mode (Recommended for Beginners)

```bash
python3 main.py
```

Try these commands:
```
SimOS> create Browser 10 3 128
SimOS> create Editor 8 2 64
SimOS> ps
SimOS> run 5
SimOS> mem
SimOS> status
SimOS> help
SimOS> exit
```

### 2. Demo Mode (See Everything in Action)

```bash
python3 main.py --mode demo
```

This runs a pre-configured demonstration showing all features.

### 3. Batch Mode (Test with Multiple Processes)

```bash
python3 main.py --mode batch --num-processes 20
```

### 4. Custom Configuration

```bash
python3 main.py \
  --scheduler priority \
  --memory-strategy best_fit \
  --file-strategy linked \
  --memory-size 2048 \
  --time-quantum 3
```

## Common Scenarios

### Scenario 1: Testing Round Robin Scheduling

```bash
python3 main.py --scheduler round_robin --time-quantum 2
```

Then in the shell:
```
create P1 10
create P2 8
create P3 6
run 20
ps
```

### Scenario 2: Testing Memory Allocation Strategies

Compare different strategies:

**First Fit:**
```bash
python3 main.py --memory-strategy first_fit
```

**Best Fit:**
```bash
python3 main.py --memory-strategy best_fit
```

**Worst Fit:**
```bash
python3 main.py --memory-strategy worst_fit
```

### Scenario 3: File System Allocation

**Contiguous:**
```bash
python3 main.py --file-strategy contiguous
```

**Linked:**
```bash
python3 main.py --file-strategy linked
```

**Indexed:**
```bash
python3 main.py --file-strategy indexed
```

Then create files:
```
mkfile doc1.txt 32
mkfile doc2.txt 64
mkfile doc3.txt 48
ls
disk
```

### Scenario 4: Virtual Memory with Paging

```bash
python3 main.py --page-replacement lru
```

Create processes with memory requirements:
```
create P1 5 5 256
create P2 8 3 384
pages
mem
```

## Shell Command Reference

### Process Commands
- `create <n> <burst> [priority] [memory]` - Create process
- `ps` - List processes
- `kill <pid>` - Terminate process
- `run [cycles]` - Execute scheduler

### Memory Commands
- `mem` - Show memory map
- `alloc <pid> <size>` - Allocate memory
- `free <pid>` - Free memory
- `pages` - Show page tables

### File System Commands
- `ls` - List files
- `mkfile <n> <size>` - Create file
- `rm <n>` - Delete file
- `disk` - Show disk map

### System Commands
- `status` - Overall status
- `config` - Show configuration
- `help` - Command help

## Testing

Run the test suite:
```bash
python3 test_simos.py
```

## Tips

1. **Start Simple**: Use interactive mode first to understand how each component works

2. **Visualize**: Use `status`, `mem`, and `disk` commands frequently to see system state

3. **Experiment**: Try different algorithms and compare results

4. **Watch Processes**: Use `ps` after `run` commands to see process states changing

5. **Check Statistics**: Completed processes show turnaround and waiting times

## Example Session

```bash
$ python3 main.py --scheduler round_robin --time-quantum 3

SimOS> create WebServer 15 2 256
Created process: PID=1, Name='WebServer'

SimOS> create Database 20 1 512
Created process: PID=2, Name='Database'

SimOS> create BackupTask 10 5 128
Created process: PID=3, Name='BackupTask'

SimOS> ps
=== Active Processes ===
PID   Name            State        Priority CPU Time   Remaining 
----------------------------------------------------------------------
1     WebServer       READY        2        0          15        
2     Database        READY        1        0          20        
3     BackupTask      READY        5        0          10        

SimOS> run 10
Running scheduler for 10 cycle(s)...
Cycle 1: Process 1 executed (1 units)
Cycle 2: Process 1 executed (1 units)
Cycle 3: Process 1 executed (1 units)
Cycle 4: Process 2 executed (1 units)
...

SimOS> status
=== System Status ===
...

SimOS> mkfile data.db 128
Created file 'data.db' (128KB)

SimOS> ls
=== File List ===
data.db: 128KB, Blocks: [0, 1, 2, ..., 31]

SimOS> exit
Exiting SimOS...
```

## Troubleshooting

**Problem**: "Module not found" error
**Solution**: Make sure you're in the SimOS directory when running

**Problem**: Memory allocation fails
**Solution**: Check available memory with `mem` command, may need to free some processes

**Problem**: File creation fails
**Solution**: Check disk space with `disk` command, or delete files with `rm`

## Next Steps

1. Read the full README.md for detailed documentation
2. Experiment with different configurations
3. Compare algorithm performance
4. Modify the code to add new features

## Learn More

- Process scheduling algorithms
- Memory management strategies
- Virtual memory and paging
- File allocation methods
- Operating system design

Happy learning! 🚀
