class Timeline:
    def __init__(self, canvas):
        self.canvas = canvas
        self.zoom_level = 1.0
        self.time_units = ["day", "week", "month", "quarter", "year"]
        self.current_unit = "month"
        
    def zoom_in(self):
        self.zoom_level = min(2.0, self.zoom_level * 1.2)
        self._update_display()
        
    def zoom_out(self):
        self.zoom_level = max(0.5, self.zoom_level / 1.2)
        self._update_display() 