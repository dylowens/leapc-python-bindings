import leap
import pyautogui
import time

class PanMapListener(leap.Listener):
    def __init__(self):
        super(PanMapListener, self).__init__()
        self.previous_positions = {}
        self.is_pinch_detected = False
        self.last_swipe_time = 0
        self.swipe_delay = 0.3  # Minimum time between swipes in seconds

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
        for hand in event.hands:
            self.detect_pinch(hand)
            if self.is_pinch_detected:
                self.pan_map(hand)
            else:
                if hand.id in self.previous_positions:
                    del self.previous_positions[hand.id]

    def detect_pinch(self, hand):
        thumb_tip = hand.digits[0].distal.next_joint
        index_tip = hand.digits[1].distal.next_joint

        # Check if pinching
        pinch_distance = self.calculate_distance(thumb_tip, index_tip)
        if pinch_distance < 20:
            if not self.is_pinch_detected:
                self.is_pinch_detected = True
                self.previous_positions[hand.id] = (time.time(), hand.palm.position)
                print("Pinch detected")
        else:
            if self.is_pinch_detected:
                self.is_pinch_detected = False
                if hand.id in self.previous_positions:
                    del self.previous_positions[hand.id]
                print("Pinch released")

    def calculate_distance(self, vec1, vec2):
        return ((vec1.x - vec2.x) ** 2 + (vec1.y - vec2.y) ** 2 + (vec1.z - vec2.z) ** 2) ** 0.5

    def pan_map(self, hand):
        current_time = time.time()
        current_position = hand.palm.position

        if hand.id in self.previous_positions:
            prev_time, prev_position = self.previous_positions[hand.id]
            delta_time = current_time - prev_time

            if delta_time > 0:
                velocity_x = (current_position.x - prev_position.x) / delta_time
                velocity_y = (current_position.y - prev_position.y) / delta_time
                velocity_z = (current_position.z - prev_position.z) / delta_time

                direction = "none"

                if velocity_x > 150:
                    direction = "right"
                elif velocity_x < -150:
                    direction = "left"
                elif velocity_y > 100:  # Lowered threshold for vertical movement
                    direction = "up"
                elif velocity_y < -100:  # Lowered threshold for vertical movement
                    direction = "down"
                elif velocity_z > 200:
                    direction = "up"  # Moving hand away from sensor
                elif velocity_z < -200:
                    direction = "down"  # Moving hand closer to sensor

                if direction != "none" and (current_time - self.last_swipe_time) > self.swipe_delay:
                    print(f"Detected pan direction: {direction}")
                    self.handle_pan(direction)
                    self.last_swipe_time = current_time

            self.previous_positions[hand.id] = (current_time, current_position)

    def handle_pan(self, direction):
        print(f"Panned {direction}")
        if direction == "right":
            pyautogui.press('right')
        elif direction == "left":
            pyautogui.press('left')
        elif direction == "up":
            pyautogui.press('up')
        elif direction == "down":
            pyautogui.press('down')

def main():
    listener = PanMapListener()
    connection = leap.Connection()
    connection.add_listener(listener)

    with connection.open():
        print("Leap Motion initialized. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(0.05)  # Reduce sleep time to increase responsiveness
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            connection.remove_listener(listener)
            print("Disconnected from Leap Motion.")

if __name__ == "__main__":
    main()
