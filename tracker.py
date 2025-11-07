import numpy as np
from scipy.spatial import distance

class CentroidTracker:
    def __init__(self):
        self.next_object_id = 0
        self.objects = {}  # Store {id: centroid}
        self.disappeared = {}  # Track frames object is missing
        
    def register(self, centroid):
        """Register a new object"""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1
    
    def deregister(self, object_id):
        """Remove an object"""
        del self.objects[object_id]
        del self.disappeared[object_id]
    
    def update(self, detections):
        """Update tracker with new detections"""
        # If no detections, mark all as disappeared
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > 50:
                    self.deregister(object_id)
            return self.objects
        
        # If no tracked objects, register all detections
        if len(self.objects) == 0:
            for i in range(len(detections)):
                self.register(detections[i])
        else:
            # Match detections to existing objects
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            # Calculate distances between objects and detections
            D = distance.cdist(np.array(object_centroids), detections)
            
            # Find closest matches
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                object_id = object_ids[row]
                self.objects[object_id] = detections[col]
                self.disappeared[object_id] = 0
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Handle unmatched objects and detections
            unused_rows = set(range(D.shape[0])) - used_rows
            unused_cols = set(range(D.shape[1])) - used_cols
            
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > 50:
                    self.deregister(object_id)
            
            for col in unused_cols:
                self.register(detections[col])
        
        return self.objects