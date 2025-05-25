import cv2
import pytesseract
import re
import numpy as np
from PIL import Image
from GUI import Modal

class IDScanner:
    def __init__(self):
        # Initialize the camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Configure Tesseract (adjust path if needed)
        # For Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        self.last_scanned_data = {"student_no": "", "name": "", "course": "", "year": ""}
        
    def calculate_scan_area(self, frame_width, frame_height):
        """Calculate optimal scan area based on frame resolution and ID card proportions"""
        # Standard ID card aspect ratio is approximately 1.586:1 (CR80 standard - 85.60 × 53.98 mm)
        id_aspect_ratio = 85.60 / 53.98  # ≈ 1.586
            
        # Calculate scan area dimensions as percentage of frame size
        # Use 60% of frame width as maximum scan width, adjust for different resolutions
        if frame_width >= 1920:  # 1080p and higher
            scan_width_ratio = 0.5  # 50% of frame width
            margin_ratio = 0.05     # 5% margin from edges
        elif frame_width >= 1280:  # 720p
            scan_width_ratio = 0.6  # 60% of frame width
            margin_ratio = 0.08     # 8% margin from edges
        else:  # Lower resolutions
            scan_width_ratio = 0.7  # 70% of frame width
            margin_ratio = 0.1      # 10% margin from edges
        
        # Calculate scan area dimensions
        scan_width = int(frame_width * scan_width_ratio)
        scan_height = int(scan_width / id_aspect_ratio)
        
        # Ensure scan area fits within frame with margins
        max_scan_height = int(frame_height * (1 - 2 * margin_ratio))
        if scan_height > max_scan_height:
            scan_height = max_scan_height
            scan_width = int(scan_height * id_aspect_ratio)
        
        # Center the scan area
        x = (frame_width - scan_width) // 2
        y = (frame_height - scan_height) // 2
        
        return x, y, scan_width, scan_height
    
    def draw_scan_overlay(self, frame):
        """Draw scanning overlay with guidelines and instructions"""
        height, width = frame.shape[:2]
        x, y, scan_width, scan_height = self.calculate_scan_area(width, height)
        
        # Draw main scanning rectangle
        cv2.rectangle(frame, (x, y), (x + scan_width, y + scan_height), (0, 255, 0), 3)
        
        # Draw corner indicators for better visual guidance
        corner_length = min(30, scan_width // 10, scan_height // 10)
        thickness = 4
        
        # Top-left corner
        cv2.line(frame, (x, y), (x + corner_length, y), (0, 255, 0), thickness)
        cv2.line(frame, (x, y), (x, y + corner_length), (0, 255, 0), thickness)
        
        # Top-right corner
        cv2.line(frame, (x + scan_width, y), (x + scan_width - corner_length, y), (0, 255, 0), thickness)
        cv2.line(frame, (x + scan_width, y), (x + scan_width, y + corner_length), (0, 255, 0), thickness)
        
        # Bottom-left corner
        cv2.line(frame, (x, y + scan_height), (x + corner_length, y + scan_height), (0, 255, 0), thickness)
        cv2.line(frame, (x, y + scan_height), (x, y + scan_height - corner_length), (0, 255, 0), thickness)
        
        # Bottom-right corner
        cv2.line(frame, (x + scan_width, y + scan_height), (x + scan_width - corner_length, y + scan_height), (0, 255, 0), thickness)
        cv2.line(frame, (x + scan_width, y + scan_height), (x + scan_width, y + scan_height - corner_length), (0, 255, 0), thickness)
        
        # Draw center crosshair for alignment
        center_x = x + scan_width // 2
        center_y = y + scan_height // 2
        crosshair_size = 20
        cv2.line(frame, (center_x - crosshair_size, center_y), (center_x + crosshair_size, center_y), (0, 255, 0), 2)
        cv2.line(frame, (center_x, center_y - crosshair_size), (center_x, center_y + crosshair_size), (0, 255, 0), 2)
        
        # Add instruction text with better positioning
        font_scale = width / 1920 * 0.8  # Scale font with resolution
        instruction_text = "Align ID card within the green frame"
        text_size = cv2.getTextSize(instruction_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        text_x = (width - text_size[0]) // 2
        text_y = y - 20 if y > 50 else y + scan_height + 40
        
        # Add background for better text visibility
        cv2.rectangle(frame, (text_x - 10, text_y - text_size[1] - 10), 
                     (text_x + text_size[0] + 10, text_y + 10), (0, 0, 0), -1)
        cv2.putText(frame, instruction_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 2)
        
        return x, y, scan_width, scan_height
        
    def preprocess_image(self, image, scan_area=None):
        """Preprocess the image for better OCR results"""
        # If scan area is provided, crop to that region first
        if scan_area:
            x, y, w, h = scan_area
            image = image[y:y+h, x:x+w]
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Morphological operations to clean up the image
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_student_info(self, text):
        """Extract student number, name, course, and year from OCR text"""
        lines = text.split('\n')
        student_no = ""
        name = ""
        course = ""
        year = ""
        
        # Look for student number pattern (like 1284-21)
        student_no_pattern = r'\b\d{4}-\d{2}\b'
        
        # Look for course patterns (like BSCPE, BSIT, etc.)
        course_pattern = r'\b(BS[A-Z]{2,4}|BA[A-Z]{2,4}|AB[A-Z]{2,4}|BSC[A-Z]{2,4})\b'
        
        # Look for year patterns
        year_pattern = r'\b(FIRST|SECOND|THIRD|FOURTH|1ST|2ND|3RD|4TH)[\s]*YEAR\b'
        
        name_found = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            line_upper = line.upper()
            
            # Search for student number
            student_match = re.search(student_no_pattern, line)
            if student_match:
                student_no = student_match.group()
            
            # Search for course
            course_match = re.search(course_pattern, line_upper)
            if course_match:
                course = course_match.group()
            
            # Search for year
            year_match = re.search(year_pattern, line_upper)
            if year_match:
                year = year_match.group()
            
            # Search for name
            if "NAME" in line_upper and i + 1 < len(lines):
                # Name is usually on the next line after "NAME"
                name = lines[i + 1].strip()
                name_found = True
            elif "NAME" in line_upper:
                # Sometimes name is on the same line
                name_part = line_upper.split("NAME")
                if len(name_part) > 1:
                    name = name_part[1].strip()
                    name_found = True
            
            # Look for course after "COURSE" keyword
            if "COURSE" in line_upper and i + 1 < len(lines):
                potential_course = lines[i + 1].strip().upper()
                course_regex = r'^(BS|BA|AB)[A-Z]{2,4}$'
                if re.match(course_regex, potential_course):
                    course = potential_course
            elif "COURSE" in line_upper:
                course_part = line_upper.split("COURSE")
                if len(course_part) > 1:
                    potential_course = course_part[1].strip()
                    course_regex = r'^(BS|BA|AB)[A-Z]{2,4}$'
                    if re.match(course_regex, potential_course):
                        course = potential_course
            
            # Look for year after "YEAR" keyword
            if "YEAR" in line_upper and not year:
                # Check current line for year info
                year_keywords = ["FIRST", "SECOND", "THIRD", "FOURTH", "1ST", "2ND", "3RD", "4TH"]
                if any(yr in line_upper for yr in year_keywords):
                    year = line.strip()
                # Check previous line for year info
                elif i > 0:
                    prev_line = lines[i-1].strip().upper()
                    if any(yr in prev_line for yr in year_keywords):
                        year = lines[i-1].strip()
            
            # If we haven't found name yet, look for capitalized words that could be a name
            if not name_found and len(line) > 5 and line.replace(' ', '').replace('.', '').isalpha():
                words = line.split()
                if len(words) >= 2 and all(word[0].isupper() for word in words if word):
                    # Make sure it's not a course or year line
                    if not re.search(course_pattern, line_upper) and "YEAR" not in line_upper:
                        name = line
                        name_found = True
        
        return student_no, name, course, year
    
    def scan_frame(self, frame, scan_area):
        """Process a single frame and extract ID information"""
        x, y, w, h = scan_area
        
        # Preprocess the image with scan area cropping
        processed = self.preprocess_image(frame, scan_area)
        
        # Convert back to PIL Image for pytesseract
        pil_image = Image.fromarray(processed)
        
        # Perform OCR
        try:
            text = pytesseract.image_to_string(pil_image, config='--psm 6')
            student_no, name, course, year = self.extract_student_info(text)
            
            if student_no or name or course or year:
                self.last_scanned_data = {
                    "student_no": student_no,
                    "name": name,
                    "course": course,
                    "year": year
                }
                return True
        except Exception as e:
            print(f"OCR Error: {e}")
        
        return False
    
    def run(self):
        """Main loop for live feed scanning"""
        print("ID Scanner Started!")
        print("Press 'q' to quit, 's' to save current scan, 'c' to clear")
        print("-" * 50)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Create a copy for processing
            scan_frame = frame.copy()
            
            # Draw scan overlay and get scan area coordinates
            x, y, scan_width, scan_height = self.draw_scan_overlay(scan_frame)
            scan_area = (x, y, scan_width, scan_height)
            
            # Try to scan the current frame
            scan_success = self.scan_frame(frame, scan_area)
            
            # Display current scan results with better scaling
            height, width = frame.shape[:2]
            font_scale = width / 1920 * 0.7
            y_offset = 30
            
            if self.last_scanned_data["student_no"]:
                cv2.putText(scan_frame, f"Student No: {self.last_scanned_data['student_no']}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 2)
                y_offset += int(35 * font_scale / 0.7)
            
            if self.last_scanned_data["name"]:
                cv2.putText(scan_frame, f"Name: {self.last_scanned_data['name']}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 2)
                y_offset += int(35 * font_scale / 0.7)
            
            if self.last_scanned_data["course"]:
                cv2.putText(scan_frame, f"Course: {self.last_scanned_data['course']}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 2)
                y_offset += int(35 * font_scale / 0.7)
            
            if self.last_scanned_data["year"]:
                cv2.putText(scan_frame, f"Year: {self.last_scanned_data['year']}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 2)
                y_offset += int(35 * font_scale / 0.7)
            
            # Show scan status
            status_color = (0, 255, 0) if scan_success else (0, 0, 255)
            status_text = "SCANNING..." if scan_success else "Position ID in green frame"
            cv2.putText(scan_frame, status_text, (10, height-20), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.8, status_color, 2)
            
            # Display the frame
            # Set the OpenCV window to full screen
            cv2.namedWindow("ID Scanner - Live Feed", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("ID Scanner - Live Feed", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            # Show the frame in full screen
            cv2.imshow('ID Scanner - Live Feed', scan_frame)   
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.save_scanned_data()
            elif key == ord('c'):
                self.clear_data()
    
    def save_scanned_data(self):
        """Save the current scanned data"""
        data = self.last_scanned_data
        if any(data.values()):
            print("\n" + "="*50)
            print("SCANNED DATA:")
            print(f"Student No: {data['student_no']}")
            print(f"Name: {data['name']}")
            print(f"Course: {data['course']}")
            print(f"Year: {data['year']}")
            print("="*50 + "\n")
            
            # Optionally save to file
            with open("scanned_ids.txt", "a") as f:
                f.write(f"Student No: {data['student_no']}, Name: {data['name']}, Course: {data['course']}, Year: {data['year']}\n")
            print("Data saved to scanned_ids.txt")
        else:
            print("No data to save!")
    
    def clear_data(self):
        """Clear the current scanned data"""
        self.last_scanned_data = {"student_no": "", "name": "", "course": "", "year": ""}
        print("Scan data cleared!")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'cap'):
            self.cap.release()
        cv2.destroyAllWindows()

# Usage
if __name__ == "__main__":
    try:
        # Create and run the scanner
        scanner = IDScanner()
        scanner.run()
    except KeyboardInterrupt:
        print("\nScanner stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cv2.destroyAllWindows()