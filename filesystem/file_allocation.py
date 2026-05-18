"""
File Allocation Module
Implements different file allocation strategies
"""

from typing import List, Dict, Optional, Set
import math


class File:
    """Represents a file in the filesystem"""
    
    def __init__(self, name, size, blocks=None):
        self.name = name
        self.size = size  # in KB
        self.blocks = blocks if blocks else []
        self.created_time = None
        
    def __repr__(self):
        return f"File('{self.name}', {self.size}KB, blocks={self.blocks})"


class FileAllocationSystem:
    """File allocation system with multiple strategies"""
    
    def __init__(self, disk_size=1024, block_size=4, strategy='contiguous'):
        """
        Initialize file allocation system
        
        Args:
            disk_size: Total disk size in KB
            block_size: Block size in KB
            strategy: Allocation strategy ('contiguous', 'linked', 'indexed')
        """
        self.disk_size = disk_size
        self.block_size = block_size
        self.num_blocks = disk_size // block_size
        self.strategy = strategy
        
        # Block allocation map: None = free, filename = allocated
        self.block_map = [None] * self.num_blocks
        self.files: Dict[str, File] = {}
        
        # For linked allocation - stores next block pointers
        self.linked_map: Dict[int, int] = {}
        
        # For indexed allocation - stores index blocks
        self.index_blocks: Dict[str, int] = {}
        
    def allocate_file(self, filename, size) -> bool:
        """
        Allocate space for a file
        
        Args:
            filename: Name of the file
            size: File size in KB
            
        Returns:
            True if allocation successful, False otherwise
        """
        if filename in self.files:
            print(f"Error: File '{filename}' already exists")
            return False
            
        num_blocks_needed = math.ceil(size / self.block_size)
        
        if self.strategy == 'contiguous':
            return self._allocate_contiguous(filename, size, num_blocks_needed)
        elif self.strategy == 'linked':
            return self._allocate_linked(filename, size, num_blocks_needed)
        elif self.strategy == 'indexed':
            return self._allocate_indexed(filename, size, num_blocks_needed)
        
        return False
    
    def _allocate_contiguous(self, filename, size, num_blocks_needed) -> bool:
        """Allocate contiguous blocks"""
        # Find contiguous free space
        start_block = self._find_contiguous_space(num_blocks_needed)
        
        if start_block is None:
            print(f"Error: Not enough contiguous space for '{filename}'")
            return False
            
        # Allocate blocks
        blocks = list(range(start_block, start_block + num_blocks_needed))
        for block in blocks:
            self.block_map[block] = filename
            
        self.files[filename] = File(filename, size, blocks)
        return True
    
    def _find_contiguous_space(self, num_blocks) -> Optional[int]:
        """Find contiguous free blocks"""
        count = 0
        start = None
        
        for i in range(self.num_blocks):
            if self.block_map[i] is None:
                if count == 0:
                    start = i
                count += 1
                if count == num_blocks:
                    return start
            else:
                count = 0
                start = None
                
        return None
    
    def _allocate_linked(self, filename, size, num_blocks_needed) -> bool:
        """Allocate using linked allocation"""
        # Find any free blocks
        free_blocks = [i for i in range(self.num_blocks) if self.block_map[i] is None]
        
        if len(free_blocks) < num_blocks_needed:
            print(f"Error: Not enough space for '{filename}'")
            return False
            
        # Allocate blocks and create links
        allocated_blocks = free_blocks[:num_blocks_needed]
        
        for i, block in enumerate(allocated_blocks):
            self.block_map[block] = filename
            if i < len(allocated_blocks) - 1:
                self.linked_map[block] = allocated_blocks[i + 1]
            else:
                self.linked_map[block] = -1  # End of file marker
                
        self.files[filename] = File(filename, size, allocated_blocks)
        return True
    
    def _allocate_indexed(self, filename, size, num_blocks_needed) -> bool:
        """Allocate using indexed allocation"""
        # Need one extra block for the index
        total_blocks_needed = num_blocks_needed + 1
        
        free_blocks = [i for i in range(self.num_blocks) if self.block_map[i] is None]
        
        if len(free_blocks) < total_blocks_needed:
            print(f"Error: Not enough space for '{filename}'")
            return False
            
        # First block is the index block
        index_block = free_blocks[0]
        data_blocks = free_blocks[1:num_blocks_needed + 1]
        
        # Allocate index block
        self.block_map[index_block] = f"{filename}_INDEX"
        self.index_blocks[filename] = index_block
        
        # Allocate data blocks
        for block in data_blocks:
            self.block_map[block] = filename
            
        self.files[filename] = File(filename, size, data_blocks)
        return True
    
    def delete_file(self, filename) -> bool:
        """
        Delete a file and free its blocks
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        if filename not in self.files:
            print(f"Error: File '{filename}' not found")
            return False
            
        file_obj = self.files[filename]
        
        # Free blocks
        for block in file_obj.blocks:
            self.block_map[block] = None
            if block in self.linked_map:
                del self.linked_map[block]
                
        # Free index block if indexed allocation
        if self.strategy == 'indexed' and filename in self.index_blocks:
            index_block = self.index_blocks[filename]
            self.block_map[index_block] = None
            del self.index_blocks[filename]
            
        del self.files[filename]
        return True
    
    def read_file(self, filename) -> Optional[List[int]]:
        """
        Read file blocks
        
        Args:
            filename: Name of the file
            
        Returns:
            List of block numbers in order, or None if file not found
        """
        if filename not in self.files:
            return None
            
        if self.strategy == 'contiguous' or self.strategy == 'indexed':
            return self.files[filename].blocks
            
        elif self.strategy == 'linked':
            # Follow the linked list
            blocks = []
            current_block = self.files[filename].blocks[0]
            
            while current_block != -1:
                blocks.append(current_block)
                current_block = self.linked_map.get(current_block, -1)
                
            return blocks
            
        return None
    
    def get_free_space(self) -> int:
        """Get free disk space in KB"""
        free_blocks = sum(1 for block in self.block_map if block is None)
        return free_blocks * self.block_size
    
    def get_stats(self):
        """Get filesystem statistics"""
        total_files = len(self.files)
        used_space = sum(file.size for file in self.files.values())
        free_space = self.get_free_space()
        
        # Calculate fragmentation
        if self.strategy == 'contiguous':
            fragments = 0
            in_free_region = False
            for block in self.block_map:
                if block is None:
                    if not in_free_region:
                        fragments += 1
                        in_free_region = True
                else:
                    in_free_region = False
        else:
            fragments = sum(1 for block in self.block_map if block is None)
            
        return {
            'disk_size': self.disk_size,
            'block_size': self.block_size,
            'num_blocks': self.num_blocks,
            'strategy': self.strategy,
            'total_files': total_files,
            'used_space': used_space,
            'free_space': free_space,
            'utilization': (used_space / self.disk_size) * 100,
            'fragmentation': fragments
        }
    
    def list_files(self):
        """List all files"""
        if not self.files:
            print("No files in filesystem")
            return
            
        print("\n=== File List ===")
        for filename, file_obj in self.files.items():
            print(f"{filename}: {file_obj.size}KB, Blocks: {file_obj.blocks}")
    
    def display_disk_map(self):
        """Display visual representation of disk"""
        print("\n=== Disk Allocation Map ===")
        print(f"Strategy: {self.strategy}")
        print(f"Block size: {self.block_size}KB\n")
        
        # Display blocks in rows of 16
        for i in range(0, self.num_blocks, 16):
            row = self.block_map[i:i+16]
            print(f"Blocks {i:3d}-{min(i+15, self.num_blocks-1):3d}: ", end="")
            for block in row:
                if block is None:
                    print(".", end=" ")
                elif "_INDEX" in str(block):
                    print("I", end=" ")
                else:
                    # Show first letter of filename
                    print(block[0].upper(), end=" ")
            print()
        
        print()
        stats = self.get_stats()
        print(f"Used: {stats['used_space']}KB | Free: {stats['free_space']}KB")
        print(f"Utilization: {stats['utilization']:.2f}%\n")
