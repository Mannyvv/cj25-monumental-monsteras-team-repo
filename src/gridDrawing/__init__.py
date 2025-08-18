from dataclasses import dataclass
from typing import Callable, List, Tuple
from nicegui import ui
import math

# If you're on Python 3.12, you can use typing.override.
# For portability, we skip it here.

TextUpdateCallback = Callable[[str], None]


@dataclass
class Point:
    x: float
    y: float


class Stroke:
    def __init__(self):
        self.points: List[Point] = []
    
    def add_point(self, x: float, y: float):
        self.points.append(Point(x, y))
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        if not self.points:
            return 0, 0, 0, 0
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        return min(xs), min(ys), max(xs), max(ys)


class CanvasDrawing:
    """Canvas-based letter drawing with pattern-based letter recognition."""

    def __init__(self, canvas_width: int = 300, canvas_height: int = 200):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.strokes: List[Stroke] = []
        self.current_stroke: Stroke = None
        self.is_drawing = False
        self.callbacks: List[TextUpdateCallback] = []
        self.text: str = ""
        self.current_letter: str = ""
        self.current_score: float = 0.0
        self.stroke_data = []  # Store stroke data from JavaScript

        # Initialize pattern-based recognizer
        self._init_pattern_recognizer()

        self.render()

    def _init_pattern_recognizer(self):
        """Initialize pattern-based letter recognition for canvas drawings."""
        # Define letter patterns as simplified stroke patterns
        # Each pattern is a list of relative positions that represent the letter shape
        self.letter_patterns = {
            'A': [
                # Left diagonal
                [(0.2, 0.8), (0.5, 0.2), (0.8, 0.8)],
                # Horizontal crossbar
                [(0.3, 0.5), (0.7, 0.5)]
            ],
            'B': [
                # Vertical line
                [(0.2, 0.2), (0.2, 0.8)],
                # Top curve
                [(0.2, 0.2), (0.6, 0.2), (0.8, 0.3), (0.8, 0.4), (0.6, 0.5), (0.2, 0.5)],
                # Bottom curve
                [(0.2, 0.5), (0.6, 0.5), (0.8, 0.6), (0.8, 0.7), (0.6, 0.8), (0.2, 0.8)]
            ],
            'C': [
                # C shape
                [(0.8, 0.2), (0.4, 0.2), (0.2, 0.3), (0.2, 0.5), (0.2, 0.7), (0.4, 0.8), (0.8, 0.8)]
            ],
            'D': [
                # Vertical line
                [(0.2, 0.2), (0.2, 0.8)],
                # D curve
                [(0.2, 0.2), (0.6, 0.2), (0.8, 0.4), (0.8, 0.6), (0.6, 0.8), (0.2, 0.8)]
            ],
            'E': [
                # Vertical line
                [(0.2, 0.2), (0.2, 0.8)],
                # Top horizontal
                [(0.2, 0.2), (0.8, 0.2)],
                # Middle horizontal
                [(0.2, 0.5), (0.6, 0.5)],
                # Bottom horizontal
                [(0.2, 0.8), (0.8, 0.8)]
            ],
            'F': [
                # Vertical line
                [(0.2, 0.2), (0.2, 0.8)],
                # Top horizontal
                [(0.2, 0.2), (0.8, 0.2)],
                # Middle horizontal
                [(0.2, 0.5), (0.6, 0.5)]
            ],
            'G': [
                # G shape
                [(0.8, 0.2), (0.4, 0.2), (0.2, 0.3), (0.2, 0.5), (0.2, 0.7), (0.4, 0.8), (0.8, 0.8), (0.8, 0.6), (0.6, 0.6)]
            ],
            'H': [
                # Left vertical
                [(0.2, 0.2), (0.2, 0.8)],
                # Right vertical
                [(0.8, 0.2), (0.8, 0.8)],
                # Middle horizontal
                [(0.2, 0.5), (0.8, 0.5)]
            ],
            'I': [
                # Vertical line
                [(0.5, 0.2), (0.5, 0.8)],
                # Top horizontal
                [(0.3, 0.2), (0.7, 0.2)],
                # Bottom horizontal
                [(0.3, 0.8), (0.7, 0.8)]
            ],
            'J': [
                # Top horizontal
                [(0.3, 0.2), (0.7, 0.2)],
                # Vertical line
                [(0.7, 0.2), (0.7, 0.7)],
                # Bottom curve
                [(0.7, 0.7), (0.5, 0.8), (0.3, 0.7)]
            ],
            'K': [
                # Vertical line
                [(0.2, 0.2), (0.2, 0.8)],
                # Diagonal lines
                [(0.2, 0.5), (0.8, 0.2)],
                [(0.2, 0.5), (0.8, 0.8)]
            ],
            'L': [
                # Vertical line
                [(0.2, 0.2), (0.2, 0.8)],
                # Bottom horizontal
                [(0.2, 0.8), (0.8, 0.8)]
            ],
            'M': [
                # Left vertical
                [(0.2, 0.2), (0.2, 0.8)],
                # Middle peak
                [(0.2, 0.2), (0.5, 0.5), (0.8, 0.2)],
                # Right vertical
                [(0.8, 0.2), (0.8, 0.8)]
            ],
            'N': [
                # Left vertical
                [(0.2, 0.2), (0.2, 0.8)],
                # Diagonal
                [(0.2, 0.2), (0.8, 0.8)],
                # Right vertical
                [(0.8, 0.2), (0.8, 0.8)]
            ],
            'O': [
                # Circle/oval
                [(0.3, 0.2), (0.7, 0.2), (0.8, 0.4), (0.8, 0.6), (0.7, 0.8), (0.3, 0.8), (0.2, 0.6), (0.2, 0.4), (0.3, 0.2)]
            ],
            'P': [
                # Vertical line
                [(0.2, 0.2), (0.2, 0.8)],
                # Top curve
                [(0.2, 0.2), (0.6, 0.2), (0.8, 0.3), (0.8, 0.4), (0.6, 0.5), (0.2, 0.5)]
            ],
            'Q': [
                # Circle/oval
                [(0.3, 0.2), (0.7, 0.2), (0.8, 0.4), (0.8, 0.6), (0.7, 0.8), (0.3, 0.8), (0.2, 0.6), (0.2, 0.4), (0.3, 0.2)],
                # Tail
                [(0.6, 0.6), (0.8, 0.8)]
            ],
            'R': [
                # Vertical line
                [(0.2, 0.2), (0.2, 0.8)],
                # Top curve
                [(0.2, 0.2), (0.6, 0.2), (0.8, 0.3), (0.8, 0.4), (0.6, 0.5), (0.2, 0.5)],
                # Diagonal
                [(0.6, 0.5), (0.8, 0.8)]
            ],
            'S': [
                # S curve
                [(0.8, 0.2), (0.4, 0.2), (0.2, 0.3), (0.2, 0.4), (0.4, 0.5), (0.6, 0.5), (0.8, 0.6), (0.8, 0.7), (0.4, 0.8), (0.2, 0.8)]
            ],
            'T': [
                # Top horizontal
                [(0.2, 0.2), (0.8, 0.2)],
                # Vertical line
                [(0.5, 0.2), (0.5, 0.8)]
            ],
            'U': [
                # Left vertical
                [(0.2, 0.2), (0.2, 0.7)],
                # Bottom curve
                [(0.2, 0.7), (0.5, 0.8), (0.8, 0.7)],
                # Right vertical
                [(0.8, 0.2), (0.8, 0.7)]
            ],
            'V': [
                # V shape
                [(0.2, 0.2), (0.5, 0.8), (0.8, 0.2)]
            ],
            'W': [
                # W shape
                [(0.2, 0.2), (0.3, 0.8), (0.5, 0.5), (0.7, 0.8), (0.8, 0.2)]
            ],
            'X': [
                # Diagonal lines
                [(0.2, 0.2), (0.8, 0.8)],
                [(0.8, 0.2), (0.2, 0.8)]
            ],
            'Y': [
                # Y shape
                [(0.2, 0.2), (0.5, 0.5), (0.8, 0.2)],
                [(0.5, 0.5), (0.5, 0.8)]
            ],
            'Z': [
                # Z shape
                [(0.2, 0.2), (0.8, 0.2)],
                [(0.8, 0.2), (0.2, 0.8)],
                [(0.2, 0.8), (0.8, 0.8)]
            ],
            ' ': [],  # Empty pattern for space
            '.': [[(0.5, 0.8)]],  # Single dot at bottom
            ',': [[(0.5, 0.7), (0.5, 0.8), (0.4, 0.8)]],  # Comma shape
            '!': [[(0.5, 0.2), (0.5, 0.6)], [(0.5, 0.8)]],  # Exclamation mark
            '?': [[(0.3, 0.2), (0.7, 0.2), (0.8, 0.3), (0.8, 0.4), (0.7, 0.5), (0.5, 0.5), (0.5, 0.8)]],  # Question mark
        }

    def _normalize_strokes(self) -> List[List[Tuple[float, float]]]:
        """Normalize strokes to a 0-1 coordinate system for comparison."""
        if not self.strokes:
            return []
        
        # Get overall bounding box
        all_points = []
        for stroke in self.strokes:
            all_points.extend(stroke.points)
        
        if not all_points:
            return []
        
        min_x = min(p.x for p in all_points)
        max_x = max(p.x for p in all_points)
        min_y = min(p.y for p in all_points)
        max_y = max(p.y for p in all_points)
        
        # Normalize to 0-1 range
        width = max_x - min_x if max_x > min_x else 1
        height = max_y - min_y if max_y > min_y else 1
        
        normalized_strokes = []
        for stroke in self.strokes:
            normalized_stroke = []
            for point in stroke.points:
                norm_x = (point.x - min_x) / width
                norm_y = (point.y - min_y) / height
                normalized_stroke.append((norm_x, norm_y))
            normalized_strokes.append(normalized_stroke)
        
        return normalized_strokes

    def _calculate_stroke_similarity(self, drawn_strokes: List[List[Tuple[float, float]]], template_strokes: List[List[Tuple[float, float]]]) -> float:
        """Calculate similarity between drawn strokes and template strokes."""
        if not drawn_strokes and not template_strokes:
            return 1.0
        if not drawn_strokes or not template_strokes:
            return 0.0
        
        # Simple point-based similarity
        drawn_points = []
        for stroke in drawn_strokes:
            drawn_points.extend(stroke)
        
        template_points = []
        for stroke in template_strokes:
            template_points.extend(stroke)
        
        if not drawn_points or not template_points:
            return 0.0
        
        # Calculate average distance between points
        total_distance = 0
        count = 0
        
        for drawn_point in drawn_points:
            min_distance = float('inf')
            for template_point in template_points:
                distance = math.sqrt((drawn_point[0] - template_point[0])**2 + (drawn_point[1] - template_point[1])**2)
                min_distance = min(min_distance, distance)
            total_distance += min_distance
            count += 1
        
        if count == 0:
            return 0.0
        
        avg_distance = total_distance / count
        # Convert distance to similarity (closer = higher similarity)
        similarity = max(0, 1 - avg_distance * 2)  # Scale factor of 2 for reasonable sensitivity
        return similarity

    def _recognize_with_patterns(self) -> tuple[str, float]:
        """Return (best_letter, score) using pattern matching."""
        drawn_strokes = self._normalize_strokes()
        
        if not drawn_strokes:
            return " ", 1.0

        best_letter, best_score = "", 0.0
        for letter, template_strokes in self.letter_patterns.items():
            score = self._calculate_stroke_similarity(drawn_strokes, template_strokes)
            if score > best_score:
                best_letter, best_score = letter, score
        
        return best_letter, best_score

    # ---------- Canvas & UI ----------

    def render(self):
        with ui.column().classes("items-center gap-4"):
            # Instructions
            ui.label("Draw letters on the canvas. Click 'Recognize' after drawing to identify the letter.").classes("text-white text-lg")

            # Canvas
            with ui.card().classes("p-4 bg-gray-800"):
                # Create HTML canvas with JavaScript
                canvas_html = f'''
                <canvas id="drawingCanvas" width="{self.canvas_width}" height="{self.canvas_height}" 
                        style="border: 1px solid #666; background: white; cursor: crosshair;"></canvas>
                <script>
                const canvas = document.getElementById('drawingCanvas');
                const ctx = canvas.getContext('2d');
                let isDrawing = false;
                let strokes = [];
                let currentStroke = [];
                
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 3;
                ctx.lineCap = 'round';
                
                function getMousePos(canvas, evt) {{
                    const rect = canvas.getBoundingClientRect();
                    return {{
                        x: evt.clientX - rect.left,
                        y: evt.clientY - rect.top
                    }};
                }}
                
                canvas.addEventListener('mousedown', function(e) {{
                    isDrawing = true;
                    currentStroke = [];
                    const pos = getMousePos(canvas, e);
                    currentStroke.push({{x: pos.x, y: pos.y}});
                    ctx.beginPath();
                    ctx.moveTo(pos.x, pos.y);
                }});
                
                canvas.addEventListener('mousemove', function(e) {{
                    if (!isDrawing) return;
                    const pos = getMousePos(canvas, e);
                    currentStroke.push({{x: pos.x, y: pos.y}});
                    ctx.lineTo(pos.x, pos.y);
                    ctx.stroke();
                }});
                
                canvas.addEventListener('mouseup', function(e) {{
                    if (isDrawing) {{
                        strokes.push(currentStroke);
                        isDrawing = false;
                    }}
                }});
                
                function clearCanvas() {{
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    strokes = [];
                    currentStroke = [];
                }}
                
                function getStrokes() {{
                    return JSON.stringify(strokes);
                }}
                
                // Make functions available globally
                window.clearCanvas = clearCanvas;
                window.getStrokes = getStrokes;
                </script>
                '''
                
                ui.add_body_html(canvas_html)

            # Controls
            with ui.row().classes("gap-2"):
                ui.button("Clear", on_click=self.clear_canvas).classes("bg-red-600")
                ui.button("Recognize", on_click=self.recognize_drawing).classes("bg-blue-600")
                ui.button("Backspace", on_click=self.backspace).classes("bg-gray-600")

            # Status
            with ui.row().classes("gap-2 items-center"):
                ui.label("Recognized:").classes("text-white")
                self.letter_display = ui.label("").classes("text-2xl font-bold text-green-400")
                self.score_display = ui.label("").classes("text-sm text-gray-300")

            with ui.row().classes("gap-2 items-center"):
                ui.label("Current Text:").classes("text-white")
                self.text_display = ui.label("").classes("text-lg text-yellow-400")

            # Commit button
            with ui.row().classes("gap-2"):
                ui.button("Commit Letter", on_click=self.commit_letter).classes("bg-green-600")

    # ---------- Actions ----------

    def clear_canvas(self):
        self.strokes = []
        self.current_stroke = None
        self.is_drawing = False
        # Clear the canvas via JavaScript
        ui.run_javascript('window.clearCanvas();')
        self.current_letter = ""
        self.current_score = 0.0
        self._update_display()

    def recognize_drawing(self):
        """Recognize the user's drawing on the canvas."""
        # Use a different approach - we'll use a global variable to store stroke data
        # and then access it through a different method
        
        # First, store the strokes in a global variable
        setup_js = '''
        if (typeof window.strokes !== 'undefined' && window.strokes.length > 0) {
            // Convert strokes to a format we can use
            let strokeData = [];
            for (let stroke of window.strokes) {
                let points = [];
                for (let point of stroke) {
                    points.push({x: point.x, y: point.y});
                }
                strokeData.push(points);
            }
            // Store in global variable
            window.pythonStrokes = JSON.stringify(strokeData);
            return window.strokes.length;
        } else {
            window.pythonStrokes = '[]';
            return 0;
        }
        '''
        
        # Execute JavaScript to store strokes
        ui.run_javascript(setup_js)
        
        # Now try to get the stroke data using a different approach
        # Since we can't easily get the result from ui.run_javascript,
        # let's try to access the global variable directly
        
        try:
            import json
            
            # Try to get the stroke data from the global variable
            get_data_js = '''
            return window.pythonStrokes || '[]';
            '''
            
            # Execute JavaScript to get the data
            stroke_json = ui.run_javascript(get_data_js)
            
            # Parse the stroke data
            if stroke_json and str(stroke_json) != '[]':
                strokes_data = json.loads(str(stroke_json))
                
                # Convert to Python Stroke objects
                self.strokes = []
                for stroke_points in strokes_data:
                    stroke = Stroke()
                    for point in stroke_points:
                        stroke.add_point(point['x'], point['y'])
                    self.strokes.append(stroke)
                
                # Trigger recognition
                self.recognize_letter()
                self._update_display()
                
            else:
                # No strokes drawn
                self.letter_display.set_text("No drawing")
                self.score_display.set_text("0.00")
                
        except Exception as e:
            # If there's an error, show a message
            self.letter_display.set_text("Error")
            self.score_display.set_text("0.00")
            print(f"Error processing strokes: {e}")

    def backspace(self):
        if self.text:
            self.text = self.text[:-1]
            self.text_display.set_text(self.text)
            for cb in self.callbacks:
                cb(self.text)

    def commit_letter(self):
        """Manually commit the currently recognized letter."""
        if self.current_letter and self.current_letter != " ":
            self.text += self.current_letter
            self.text_display.set_text(self.text)
            for cb in self.callbacks:
                cb(self.text)
            self.clear_canvas()

    # ---------- Recognition & Commit ----------

    def recognize_letter(self):
        letter, score = self._recognize_with_patterns()
        # Show when fairly confident
        self.current_letter = letter if score >= 0.30 else ""
        self.current_score = score

    def _update_display(self):
        """Update the display elements with current recognition results."""
        if hasattr(self, 'letter_display'):
            self.letter_display.set_text(self.current_letter or "?")
        if hasattr(self, 'score_display'):
            self.score_display.set_text(f"{self.current_score:.2f}")

    # ---------- Typing test integration ----------

    def on_text_update(self, cb: TextUpdateCallback):
        """Register typing-test callback; fires whenever text changes."""
        self.callbacks.append(cb)