import pygame
import sys
import os
import subprocess
import time  # Keep this import
from pygame import *

pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
pygame.display.set_caption("Confirmation")

# Colors
RED = (255, 0, 0)
GREEN = (0, 200, 0)
HOVER_COLOR = (240, 230, 180)
FONT_COLOR = "black"
BACKGROUND = "white"
BLUE = (0, 0, 255)

# Fonts
font = pygame.font.SysFont("arial", 30)
big_font = pygame.font.SysFont("arial", 40)
title_font = pygame.font.SysFont("arial", 50)

def load_scan_data():
    """Load scanned data from temp file"""
    try:
        temp_file_path = os.path.join(os.path.dirname(__file__), "temp_scan_data.txt")
        with open(temp_file_path, "r") as f:
            lines = f.readlines()
            student_no = lines[0].strip() if len(lines) > 0 else "Not found"
            name = lines[1].strip() if len(lines) > 1 else "Not found"
            return student_no, name
    except FileNotFoundError:
        print("Temp file not found, using default values")
        return "Not found", "Not found"
    except Exception as e:
        print(f"Error loading scan data: {e}")
        return "Not found", "Not found"

def restart_scanner():
    """Restart the ID scanner and wait for it to launch"""
    try:
        # Updated path to correctly point to idScanner folder
        scanner_script = os.path.join(os.path.dirname(__file__), "..", "idScanner", "IDscan.py")
        scanner_script = os.path.normpath(scanner_script)
        print(f"Launching scanner script: {scanner_script}")
        
        # Check if the script exists
        if not os.path.exists(scanner_script):
            print(f"Scanner script not found at: {scanner_script}")
            pygame.quit()
            sys.exit(1)
        
        # Launch the scanner in a separate process with proper arguments
        scanner_process = subprocess.Popen(
            [sys.executable, scanner_script],
            cwd=os.path.dirname(scanner_script),  # Set working directory
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        
        print(f"Scanner process started with PID: {scanner_process.pid}")
        
        # Give the process a moment to start
        import time as time_module
        time_module.sleep(0.5)
        
        # Check if process is still running (didn't crash immediately)
        if scanner_process.poll() is None:
            print("Scanner process is running successfully")
        else:
            print(f"Scanner process exited immediately with code: {scanner_process.returncode}")
        
        # Only quit pygame after we've launched the scanner
        pygame.quit()
        sys.exit()
    except Exception as e:
        print(f"Error restarting scanner: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

def confirm_and_save():
    """Confirm the data and save to final file"""
    try:
        # Load current data
        student_no, name = load_scan_data()
        
        # Create confirmed_scans directory if it doesn't exist
        confirmed_dir = "confirmed_scans"
        if not os.path.exists(confirmed_dir):
            os.makedirs(confirmed_dir)
        
        # Save confirmed data
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        confirmed_file = os.path.join(confirmed_dir, f"confirmed_scan_{timestamp}.txt")
        
        with open(confirmed_file, "w") as f:
            f.write(f"Confirmation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"STUDENT NO: {student_no}\n")
            f.write(f"NAME: {name}\n")
            f.write(f"STATUS: CONFIRMED\n")
        
        print(f"Confirmed data saved to: {confirmed_file}")
        
        # Clean up temp file
        temp_file_path = os.path.join(os.path.dirname(__file__), "temp_scan_data.txt")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        return True
    except Exception as e:
        print(f"Error saving confirmed data: {e}")
        return False

class Button():
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = HOVER_COLOR
        self.text = font.render(text, True, FONT_COLOR)
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=20)
        surface.blit(self.text, self.text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Load data
student_no, name = load_scan_data()

# Create buttons - positioned better for all data
cancel_button = Button(200, 600, 200, 80, "Cancel", RED)
confirm_button = Button(500, 600, 200, 80, "Confirm", GREEN)

# Main loop
running = True
clock = pygame.time.Clock()

print("Confirmation screen started")
print(f"Loaded data: {student_no}, {name}")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            restart_scanner()
            
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                restart_scanner()
            elif event.key == K_RETURN:
                if confirm_and_save():
                    print("Data confirmed and saved successfully")
                    # Show a brief confirmation message before restarting
                    screen.fill(BACKGROUND)
                    success_text = big_font.render("Data Saved Successfully!", True, GREEN)
                    screen.blit(success_text, (screen.get_width()//2 - success_text.get_width()//2, screen.get_height()//2))
                    pygame.display.flip()
                    
                    # Brief pause to show the message
                    import time as time_module
                    time_module.sleep(1.5)
                    
                    restart_scanner()
                else:
                    print("Failed to save data")
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if cancel_button.is_clicked(mouse_pos):
                restart_scanner()
            elif confirm_button.is_clicked(mouse_pos):
                if confirm_and_save():
                    print("Data confirmed and saved successfully")
                    # Show a brief confirmation message before restarting
                    screen.fill(BACKGROUND)
                    success_text = big_font.render("Data Saved Successfully!", True, GREEN)
                    screen.blit(success_text, (screen.get_width()//2 - success_text.get_width()//2, screen.get_height()//2))
                    pygame.display.flip()
                    
                    # Brief pause to show the message
                    import time as time_module
                    time_module.sleep(1.5)
                    
                    restart_scanner()
                else:
                    print("Failed to save data")

    # Draw everything
    screen.fill(BACKGROUND)
    
    # Title
    title = title_font.render("Confirm Student Information", True, BLUE)
    screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))
    
    # Display boxes - made smaller since we have less data
    info_box = pygame.Rect(100, 150, 700, 300)
    pygame.draw.rect(screen, (240, 240, 240), info_box, border_radius=10)
    pygame.draw.rect(screen, (200, 200, 200), info_box, 2, border_radius=10)
    
    # Display data with better spacing
    y_offset = 200
    line_spacing = 70
    
    # Student Number
    id_label = big_font.render("Student No:", True, FONT_COLOR)
    screen.blit(id_label, (150, y_offset))
    id_text = big_font.render(student_no if student_no else "Not found", True, BLUE)
    screen.blit(id_text, (350, y_offset))
    
    # Name
    y_offset += line_spacing
    name_label = big_font.render("Name:", True, FONT_COLOR)
    screen.blit(name_label, (150, y_offset))
    name_text = big_font.render(name if name else "Not found", True, BLUE)
    screen.blit(name_text, (350, y_offset))

    # Draw buttons
    cancel_button.draw(screen)
    confirm_button.draw(screen)
    
    # Instructions
    instruction_text = font.render("Press ESC to cancel, ENTER to confirm, or click buttons", True, FONT_COLOR)
    screen.blit(instruction_text, (screen.get_width()//2 - instruction_text.get_width()//2, 720))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

# Cleanup
pygame.quit()
sys.exit()