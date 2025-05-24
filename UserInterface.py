import pygame
import cv2 as cv
import numpy as np
from pygame import *

class OpenCVCamera:
    def __init__(self, camera_index=0):
        self.cap = cv.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", camera_index)
        
        # Force landscape orientation by swapping width/height if needed
        self.width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        
        # Ensure width > height (landscape)
        if self.height > self.width:
            self.width, self.height = self.height, self.width
        
        self.fps = self.cap.get(cv.CAP_PROP_FPS)
        
    def get_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            
            # Rotate to landscape if needed
            if frame.shape[0] > frame.shape[1]:  # If height > width (portrait)
                frame = cv.rotate(frame, cv.ROTATE_90_CLOCKWISE)
                
            return frame
        return None
        
    def release(self):
        if self.cap.isOpened():
            self.cap.release()

class PygameDisplay:
    def __init__(self, width=1280, height=1720):  # Default to landscape aspect ratio
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        
    def process_events(self):        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_F8):
                return False
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.display.set_mode((self.screen.get_width(), self.screen.get_height()))
            if event.type == KEYDOWN and event.key == K_F4:
                pygame.display.set_mode((self.screen.get_width(), self.screen.get_height()),pygame.FULLSCREEN)
        return True
        
    def quit(self):
        pygame.quit()

class CameraApp:
    def __init__(self):
        self.camera = OpenCVCamera()
        # Initialize display with landscape dimensions
        
        display_width = max(self.camera.width, self.camera.height)
        display_height = min(self.camera.width, self.camera.height)
        self.display = PygameDisplay(display_width, display_height)
        
    def run(self):
        running = True
        while running:
            frame = self.camera.get_frame()
            if frame is None:
                break

            frame_surface = pygame.surfarray.make_surface(np.rot90(frame))

            rotated_surface = pygame.transform.rotate(frame_surface, 90)

            rotated_surface = pygame.transform.smoothscale(rotated_surface, (self.display.screen.get_width(), self.display.screen.get_height()))

            self.display.screen.blit(rotated_surface, (0, 0))
            pygame.display.flip()

            running = self.display.process_events()
            self.display.clock.tick(self.camera.fps)

        self.camera.release()
        self.display.quit()


if __name__ == "__main__":
    app = CameraApp()
    app.run()