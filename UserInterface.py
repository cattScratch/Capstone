import pygame
import cv2 as cv
import numpy as np
from pygame import *

class OpenCVCamera:
    def __init__(self, camera_index=0):
        self.cap = cv.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", camera_index)
        
        self.width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv.CAP_PROP_FPS)
        
    def get_frame(self):
        ret, frame = self.cap.read()
        if ret:
            return cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        return None
        
    def release(self):
        if self.cap.isOpened():
            self.cap.release()

class PygameDisplay:
    def __init__(self, width=500, height=500):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        
    def process_events(self):        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_F8):
                return False
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.display.set_mode((self.screen.get_width(), self.screen.get_height()))
        return True
        
    def quit(self):
        pygame.quit()

class CameraApp:
    def __init__(self):
        self.camera = OpenCVCamera()
        self.display = PygameDisplay(self.camera.width, self.camera.height)
        
    def run(self):
        running = True
        while running:
            frame = self.camera.get_frame()
            if frame is None:
                break
            
            # Convert the frame to a pygame surface and display it
            frame = np.rot90(frame)  # Rotate if needed
            frame = pygame.surfarray.make_surface(frame)
            self.display.screen.blit(frame, (0, 0))
            pygame.display.flip()
            
            running = self.display.process_events()
            self.display.clock.tick(self.camera.fps)
            
        self.camera.release()
        self.display.quit()

if __name__ == "__main__":
    app = CameraApp()
    app.run()