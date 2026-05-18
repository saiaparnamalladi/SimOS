"""
Paging Module
Implements virtual memory management with paging
"""

from typing import Dict, List, Optional, Tuple
import random


class PageTableEntry:
    """Entry in a page table"""
    
    def __init__(self, frame_number=None, valid=False):
        self.frame_number = frame_number
        self.valid = valid
        self.referenced = False
        self.modified = False
        
    def __repr__(self):
        status = "Valid" if self.valid else "Invalid"
        return f"PTE(Frame: {self.frame_number}, {status})"


class PageTable:
    """Page table for a process"""
    
    def __init__(self, num_pages):
        self.entries = [PageTableEntry() for _ in range(num_pages)]
        self.num_pages = num_pages
        
    def get_entry(self, page_number) -> Optional[PageTableEntry]:
        """Get page table entry for a page"""
        if 0 <= page_number < self.num_pages:
            return self.entries[page_number]
        return None


class PagingSystem:
    """Virtual memory paging system"""
    
    def __init__(self, physical_memory_size=256, page_size=4, replacement_algorithm='fifo'):
        """
        Initialize paging system
        
        Args:
            physical_memory_size: Physical memory size in KB
            page_size: Page/Frame size in KB
            replacement_algorithm: Page replacement algorithm ('fifo', 'lru', 'random')
        """
        self.physical_memory_size = physical_memory_size
        self.page_size = page_size
        self.num_frames = physical_memory_size // page_size
        self.replacement_algorithm = replacement_algorithm
        
        # Frame table: maps frame number to (process_id, page_number)
        self.frame_table = [None] * self.num_frames
        self.free_frames = list(range(self.num_frames))
        
        # Page tables for each process
        self.page_tables: Dict[int, PageTable] = {}
        
        # For FIFO replacement
        self.fifo_queue = []
        
        # For LRU replacement
        self.lru_counter = 0
        self.frame_access_time = {}
        
        # Statistics
        self.page_faults = 0
        self.page_hits = 0
        
    def create_page_table(self, process_id, virtual_memory_size):
        """
        Create page table for a process
        
        Args:
            process_id: Process identifier
            virtual_memory_size: Virtual memory size in KB
        """
        num_pages = (virtual_memory_size + self.page_size - 1) // self.page_size
        self.page_tables[process_id] = PageTable(num_pages)
        
    def translate_address(self, process_id, virtual_address) -> Tuple[Optional[int], bool]:
        """
        Translate virtual address to physical address
        
        Args:
            process_id: Process identifier
            virtual_address: Virtual address to translate
            
        Returns:
            Tuple of (physical_address, page_fault_occurred)
        """
        if process_id not in self.page_tables:
            return None, False
            
        page_table = self.page_tables[process_id]
        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        
        entry = page_table.get_entry(page_number)
        if entry is None:
            return None, False
            
        page_fault = False
        
        # Check if page is in memory
        if not entry.valid:
            # Page fault - need to load page
            page_fault = True
            self.page_faults += 1
            frame_number = self._load_page(process_id, page_number)
            
            if frame_number is None:
                return None, page_fault
                
            entry.frame_number = frame_number
            entry.valid = True
        else:
            self.page_hits += 1
            
        # Update reference information for LRU
        entry.referenced = True
        if self.replacement_algorithm == 'lru':
            self.lru_counter += 1
            frame_key = (process_id, page_number)
            self.frame_access_time[frame_key] = self.lru_counter
            
        physical_address = (entry.frame_number * self.page_size) + offset
        return physical_address, page_fault
    
    def _load_page(self, process_id, page_number) -> Optional[int]:
        """Load a page into a frame"""
        
        # Get a free frame or evict a page
        if self.free_frames:
            frame_number = self.free_frames.pop(0)
        else:
            frame_number = self._evict_page()
            if frame_number is None:
                return None
                
        # Update frame table
        self.frame_table[frame_number] = (process_id, page_number)
        
        # Update FIFO queue
        if self.replacement_algorithm == 'fifo':
            self.fifo_queue.append(frame_number)
            
        # Update LRU tracking
        if self.replacement_algorithm == 'lru':
            self.lru_counter += 1
            frame_key = (process_id, page_number)
            self.frame_access_time[frame_key] = self.lru_counter
            
        return frame_number
    
    def _evict_page(self) -> Optional[int]:
        """Evict a page using the replacement algorithm"""
        
        if self.replacement_algorithm == 'fifo':
            if not self.fifo_queue:
                return None
            frame_number = self.fifo_queue.pop(0)
            
        elif self.replacement_algorithm == 'lru':
            # Find frame with oldest access time
            if not self.frame_access_time:
                return 0
            oldest_frame_key = min(self.frame_access_time, key=self.frame_access_time.get)
            # Find corresponding frame number
            for frame_num, (pid, pg_num) in enumerate(self.frame_table):
                if pid is not None and (pid, pg_num) == oldest_frame_key:
                    frame_number = frame_num
                    break
            else:
                return 0
                
        elif self.replacement_algorithm == 'random':
            frame_number = random.randint(0, self.num_frames - 1)
            
        else:
            return 0
            
        # Invalidate page table entry for evicted page
        if self.frame_table[frame_number] is not None:
            evicted_pid, evicted_page = self.frame_table[frame_number]
            if evicted_pid in self.page_tables:
                entry = self.page_tables[evicted_pid].get_entry(evicted_page)
                if entry:
                    entry.valid = False
                    entry.frame_number = None
                    
            # Remove from LRU tracking
            if self.replacement_algorithm == 'lru':
                frame_key = (evicted_pid, evicted_page)
                if frame_key in self.frame_access_time:
                    del self.frame_access_time[frame_key]
                    
        return frame_number
    
    def free_process_pages(self, process_id):
        """Free all pages allocated to a process"""
        if process_id not in self.page_tables:
            return
            
        # Free all frames used by this process
        for frame_num, frame_data in enumerate(self.frame_table):
            if frame_data and frame_data[0] == process_id:
                self.frame_table[frame_num] = None
                self.free_frames.append(frame_num)
                
                # Remove from FIFO queue
                if self.replacement_algorithm == 'fifo' and frame_num in self.fifo_queue:
                    self.fifo_queue.remove(frame_num)
                    
        # Remove from LRU tracking
        if self.replacement_algorithm == 'lru':
            keys_to_remove = [k for k in self.frame_access_time.keys() if k[0] == process_id]
            for key in keys_to_remove:
                del self.frame_access_time[key]
                
        # Remove page table
        del self.page_tables[process_id]
        
    def get_stats(self):
        """Get paging statistics"""
        total_accesses = self.page_hits + self.page_faults
        hit_rate = (self.page_hits / total_accesses * 100) if total_accesses > 0 else 0
        
        return {
            'num_frames': self.num_frames,
            'free_frames': len(self.free_frames),
            'used_frames': self.num_frames - len(self.free_frames),
            'page_faults': self.page_faults,
            'page_hits': self.page_hits,
            'hit_rate': hit_rate,
            'replacement_algorithm': self.replacement_algorithm
        }
    
    def display_frame_table(self):
        """Display frame table"""
        print("\n=== Frame Table ===")
        for i, frame_data in enumerate(self.frame_table):
            if frame_data:
                pid, page_num = frame_data
                print(f"Frame {i}: Process {pid}, Page {page_num}")
            else:
                print(f"Frame {i}: FREE")
        print()
