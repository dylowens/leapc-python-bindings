import leap
import pygame
import time

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Finger Tracker")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Sensitivity factors
X_SENSITIVITY = 2.0
Z_SENSITIVITY = 4.0

class FingerTrackerListener(leap.Listener):
    def __init__(self):
        super(FingerTrackerListener, self).__init__()
        self.running = True
        self.hand_detected = False
        self.hand_lost = True

    def on_init(self, connection):
        print("Initialized")

    def on_connection_event(self, event):
        print("Connected")

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()
        print(f"Found device {info.serial}")

    def on_tracking_event(self, event):
        if event.hands:
            if self.hand_lost:
                self.reset_dot()
                self.hand_lost = False
            self.hand_detected = True
            for hand in event.hands:
                self.track_finger(hand)
        else:
            self.hand_detected = False
            self.hand_lost = True
            self.update_screen(None, None)

    def reset_dot(self):
        screen_width, screen_height = screen.get_size()
        self.update_screen(screen_width // 2, screen_height // 2)

    def track_finger(self, hand):
        index_tip = hand.digits[1].distal.next_joint

        # Map Leap Motion coordinates to screen coordinates
        screen_width, screen_height = screen.get_size()
        leap_width, leap_height = 300, 300  # Example dimensions, adjust as necessary

        # Adjust sensitivity
        dot_x = int((index_tip.x * X_SENSITIVITY + leap_width / 2) * screen_width / leap_width)
        dot_y = int(((index_tip.z * Z_SENSITIVITY + leap_height / 2) * screen_height / leap_height))

        self.update_screen(dot_x, dot_y)

    def update_screen(self, x, y):
        screen.fill(black)  # Clear the screen
        if self.hand_detected and x is not None and y is not None:
            pygame.draw.circle(screen, white, (x, y), 10)  # Draw the white dot
        pygame.display.flip()

def main():
    listener = FingerTrackerListener()
    connection = leap.Connection()
    connection.add_listener(listener)

    with connection.open():
        print("Leap Motion initialized. Press Ctrl+C to exit.")
        try:
            while listener.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        listener.running = False
                time.sleep(0.005)  # Reduce sleep time to increase responsiveness
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            connection.remove_listener(listener)
            pygame.quit()
            print("Disconnected from Leap Motion.")

if __name__ == "__main__":
    main()
