""" Malgorzata Debska
6-2 Activity: Simulating Memory Allocation and Reclamation
CS-660 
"""
from dataclasses import dataclass, field
import threading
import time


@dataclass
class SimulatedObject:
    name: str
    references: set = field(default_factory=set)


class MemoryPool:
    def __init__(self):
        self.lock = threading.Lock()
        self.objects = {}
        self.roots = {}
        self.next_id = 1
        self.created = 0
        self.reclaimed = 0

    def allocate(self, owner, name, parent=None):
        # Publication is atomic: a new object becomes a root or a child
        # before the collector can inspect it.
        with self.lock:
            if parent is not None and parent not in self.objects:
                raise ValueError("Parent is no longer allocated")
            oid = self.next_id
            self.next_id += 1
            self.objects[oid] = SimulatedObject(name)
            if parent is None:
                self.roots.setdefault(owner, set()).add(oid)
            else:
                self.objects[parent].references.add(oid)
            self.created += 1
            print(f"[{owner}] CREATE / ALLOCATE #{oid} {name}", flush=True)
            return oid

    def link(self, source, target):
        with self.lock:
            if source not in self.objects or target not in self.objects:
                raise ValueError("Cannot link reclaimed objects")
            self.objects[source].references.add(target)

    def release(self, owner, oid):
        # Releasing a root does not free the object immediately.
        with self.lock:
            self.roots.get(owner, set()).discard(oid)
            print(f"[{owner}] RELEASE root #{oid}", flush=True)

    def collect(self, label):
        # Stop-the-world model: keep the same lock for both phases.
        with self.lock:
            marked = set()
            pending = [oid for roots in self.roots.values() for oid in roots]
            while pending:
                oid = pending.pop()
                if oid in self.objects and oid not in marked:
                    marked.add(oid)
                    pending.extend(self.objects[oid].references)
            dead = sorted(set(self.objects) - marked)
            print(f"[GC {label}] MARK {len(marked)} reachable", flush=True)
            for oid in dead:
                del self.objects[oid]
                self.reclaimed += 1
                print(f"[GC {label}] RECLAIM #{oid}", flush=True)
            print(f"[GC {label}] SWEEP {len(dead)}; live={len(self.objects)}",
                  flush=True)
            return len(marked), len(dead), len(self.objects)


def worker(pool, ready, release_roots, finished):
    owner = threading.current_thread().name
    print(f"[{owner}] START", flush=True)
    root = pool.allocate(owner, "parent")
    child = pool.allocate(owner, "child", parent=root)
    pool.link(child, root)  # A cycle: both objects still need only one root.
    ready.wait()
    release_roots.wait()
    pool.release(owner, root)
    print(f"[{owner}] FINISH", flush=True)
    finished.wait()


def main():
    pool = MemoryPool()
    ready = threading.Barrier(4)
    finished = threading.Barrier(4)
    release_roots = threading.Event()
    stop = threading.Event()
    print("Concurrent memory management simulation", flush=True)

    def collector():
        while not stop.wait(0.05):
            pool.collect("background")

    gc_thread = threading.Thread(target=collector, name="Collector")
    gc_thread.start()
    threads = [
        threading.Thread(target=worker, name=f"Worker-{i}",
                         args=(pool, ready, release_roots, finished))
        for i in range(1, 4)
    ]
    for thread in threads:
        thread.start()
    ready.wait()
    # Six objects must survive, including three children with no direct root.
    assert pool.collect("rooted") == (6, 0, 6)
    release_roots.set()
    finished.wait()
    for thread in threads:
        thread.join()
    stop.set()
    gc_thread.join()
    pool.collect("final")
    assert pool.created == pool.reclaimed == 6 and not pool.objects
    print(f"SUMMARY created={pool.created} reclaimed={pool.reclaimed} live=0",
          flush=True)
    print("PASS: reachable children survived; unreachable cycles reclaimed.",
          flush=True)


if __name__ == "__main__":
    main()
