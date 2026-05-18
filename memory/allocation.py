"""
Memory Allocation Module
Implements memory management with different allocation strategies
"""

from typing import List, Optional, Tuple


class MemoryBlock:
    """Represents a block of memory"""
    
    def __init__(self, start_address, size, is_free=True, process_id=None):
        self.start_address = start_address
        self.size = size
        self.is_free = is_free
        self.process_id = process_id
        
    def __repr__(self):
        status = "FREE" if self.is_free else f"ALLOCATED (PID: {self.process_id})"
        return f"Block[{self.start_address}:{self.start_address + self.size - 1}] {self.size}KB - {status}"


class MemoryAllocator:
    """Memory allocator implementing various allocation strategies"""
    
    def __init__(self, total_memory=1024, strategy='first_fit'):
        """
        Initialize memory allocator
        
        Args:
            total_memory: Total memory size in KB
            strategy: Allocation strategy ('first_fit', 'best_fit', 'worst_fit')
        """
        self.total_memory = total_memory
        self.strategy = strategy
        self.blocks = [MemoryBlock(0, total_memory, is_free=True)]
        
    def allocate(self, process_id, size) -> Optional[int]:
        """
        Allocate memory for a process
        
        Args:
            process_id: Process identifier
            size: Memory size required in KB
            
        Returns:
            Starting address if successful, None otherwise
        """
        if size <= 0 or size > self.total_memory:
            return None
            
        block_index = self._find_block(size)
        
        if block_index is None:
            return None
            
        block = self.blocks[block_index]
        start_address = block.start_address
        
        # Allocate the memory
        allocated_block = MemoryBlock(start_address, size, is_free=False, process_id=process_id)
        
        # If there's remaining space, create a new free block
        if block.size > size:
            remaining_block = MemoryBlock(
                start_address + size,
                block.size - size,
                is_free=True
            )
            self.blocks[block_index] = allocated_block
            self.blocks.insert(block_index + 1, remaining_block)
        else:
            self.blocks[block_index] = allocated_block
            
        return start_address
    
    def _find_block(self, size) -> Optional[int]:
        """Find a suitable free block based on allocation strategy"""
        
        free_blocks = [(i, block) for i, block in enumerate(self.blocks) 
                       if block.is_free and block.size >= size]
        
        if not free_blocks:
            return None
            
        if self.strategy == 'first_fit':
            return free_blocks[0][0]
            
        elif self.strategy == 'best_fit':
            # Find smallest block that fits
            best = min(free_blocks, key=lambda x: x[1].size)
            return best[0]
            
        elif self.strategy == 'worst_fit':
            # Find largest block
            worst = max(free_blocks, key=lambda x: x[1].size)
            return worst[0]
            
        return None
    
    def deallocate(self, process_id) -> bool:
        """
        Deallocate memory for a process
        
        Args:
            process_id: Process identifier
            
        Returns:
            True if successful, False otherwise
        """
        deallocated = False
        
        for i, block in enumerate(self.blocks):
            if not block.is_free and block.process_id == process_id:
                block.is_free = True
                block.process_id = None
                deallocated = True
                
        if deallocated:
            self._merge_free_blocks()
            
        return deallocated
    
    def _merge_free_blocks(self):
        """Merge adjacent free blocks to reduce fragmentation"""
        i = 0
        while i < len(self.blocks) - 1:
            current = self.blocks[i]
            next_block = self.blocks[i + 1]
            
            if current.is_free and next_block.is_free:
                # Merge blocks
                merged = MemoryBlock(
                    current.start_address,
                    current.size + next_block.size,
                    is_free=True
                )
                self.blocks[i] = merged
                self.blocks.pop(i + 1)
            else:
                i += 1
    
    def get_memory_map(self) -> List[MemoryBlock]:
        """Get current memory map"""
        return self.blocks.copy()
    
    def get_stats(self):
        """Get memory statistics"""
        total_free = sum(block.size for block in self.blocks if block.is_free)
        total_allocated = sum(block.size for block in self.blocks if not block.is_free)
        fragmentation = len([b for b in self.blocks if b.is_free])
        
        return {
            'total_memory': self.total_memory,
            'free_memory': total_free,
            'allocated_memory': total_allocated,
            'utilization': (total_allocated / self.total_memory) * 100,
            'free_blocks': fragmentation,
            'strategy': self.strategy
        }
    
    def display_memory_map(self):
        """Display visual representation of memory"""
        print("\n=== Memory Map ===")
        for block in self.blocks:
            print(block)
        print(f"\nTotal: {self.total_memory}KB")
        stats = self.get_stats()
        print(f"Free: {stats['free_memory']}KB | Allocated: {stats['allocated_memory']}KB")
        print(f"Utilization: {stats['utilization']:.2f}%\n")
