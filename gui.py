import pygame
import serial
import math

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 700, 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RC Controller")

# Colors
PURPLE = (75, 44, 109)  # 4b2c6d
WHITE = (255, 255, 255)  # pure white
CYAN = (94, 203, 241)  # 5ecbf1

# Serial setup
try:
    ser = serial.Serial('COM7', 115200, timeout=1)  # Replace 'COM7' with your port
    print("Serial connection established")
except Exception as e:
    print(f"Error connecting to serial device: {e}")
    ser = None

# Function to send a command
def send_command(channel, value):
    if ser:
        command = f"C{channel} {value}\n"
        try:
            ser.write(command.encode())
            print(f"Sent: {command.strip()}")
        except Exception as e:
            print(f"Error sending command: {e}")
    else:
        print(f"Channel {channel} -> {value}")

# Helper function to map value ranges
def map_value(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# RC Controller components
ROLL_PITCH_AREA = pygame.Rect(50, 100, 250, 250)  # Area for roll and pitch control
roll_pitch_pos = [ROLL_PITCH_AREA.centerx, ROLL_PITCH_AREA.centery]  # Knob position
THROTTLE_SLIDER = pygame.Rect(350, 100, 40, 250)  # Area for throttle slider
throttle_value = 1500
YAW_CENTER = (550, 225)  # Center of yaw dial
YAW_RADIUS = 75
yaw_angle = 0  # Angle of yaw in degrees

# Track last sent values
last_roll_value = None
last_pitch_value = None
last_throttle_value = None
last_yaw_value = None

# Reset function
def reset_controls():
    global roll_pitch_pos, throttle_value, yaw_angle
    roll_pitch_pos = [ROLL_PITCH_AREA.centerx, ROLL_PITCH_AREA.centery]
    throttle_value = 1500
    yaw_angle = 0
    send_command(1, 1500)  # Reset roll
    send_command(2, 1500)  # Reset pitch
    send_command(3, 1500)  # Reset yaw
    send_command(4, 1500)  # Reset throttle

# Main loop
running = True
dragging_knob = False
dragging_throttle = False
yaw_dragging = False
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ROLL_PITCH_AREA.collidepoint(mouse_pos):
                dragging_knob = True
            elif THROTTLE_SLIDER.collidepoint(mouse_pos):
                dragging_throttle = True
            elif (mouse_pos[0] - YAW_CENTER[0]) ** 2 + (mouse_pos[1] - YAW_CENTER[1]) ** 2 <= YAW_RADIUS ** 2:
                yaw_dragging = True
            elif 550 <= mouse_pos[0] <= 650 and 400 <= mouse_pos[1] <= 450:  # Reset button area
                reset_controls()

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_knob = False
            dragging_throttle = False
            yaw_dragging = False

    # Roll and Pitch (Knob)
    if dragging_knob:
        roll_pitch_pos[0] = max(ROLL_PITCH_AREA.left, min(mouse_pos[0], ROLL_PITCH_AREA.right))
        roll_pitch_pos[1] = max(ROLL_PITCH_AREA.top, min(mouse_pos[1], ROLL_PITCH_AREA.bottom))

    roll_value = map_value(roll_pitch_pos[0], ROLL_PITCH_AREA.left, ROLL_PITCH_AREA.right, 1000, 2000)
    pitch_value = map_value(roll_pitch_pos[1], ROLL_PITCH_AREA.top, ROLL_PITCH_AREA.bottom, 2000, 1000)  # Inverted

    if roll_value != last_roll_value:
        send_command(1, roll_value)
        last_roll_value = roll_value

    if pitch_value != last_pitch_value:
        send_command(2, pitch_value)
        last_pitch_value = pitch_value

    # Throttle (Vertical Slider)
    if dragging_throttle:
        throttle_value = map_value(mouse_pos[1], THROTTLE_SLIDER.top, THROTTLE_SLIDER.bottom, 2000, 1000)
        throttle_value = max(1000, min(2000, throttle_value))

    if throttle_value != last_throttle_value:
        send_command(4, throttle_value)
        last_throttle_value = throttle_value

    # Yaw (Rotational Dial)
    if yaw_dragging:
        dx = mouse_pos[0] - YAW_CENTER[0]
        dy = mouse_pos[1] - YAW_CENTER[1]
        yaw_angle = (math.atan2(-dy, dx) * 180 / math.pi) % 360

    yaw_value = map_value(yaw_angle, 0, 360, 1000, 2000)

    if yaw_value != last_yaw_value:
        send_command(3, yaw_value)
        last_yaw_value = yaw_value

    # Draw Roll and Pitch Area
    pygame.draw.rect(screen, CYAN, ROLL_PITCH_AREA)
    pygame.draw.circle(screen, PURPLE, roll_pitch_pos, 10)

    # Draw Throttle Slider
    pygame.draw.rect(screen, CYAN, THROTTLE_SLIDER)
    throttle_pos = map_value(throttle_value, 2000, 1000, THROTTLE_SLIDER.top, THROTTLE_SLIDER.bottom)
    pygame.draw.line(screen, PURPLE, (THROTTLE_SLIDER.left, throttle_pos), (THROTTLE_SLIDER.right, throttle_pos), 5)

    # Draw Yaw Dial
    pygame.draw.circle(screen, CYAN, YAW_CENTER, YAW_RADIUS)

    yaw_knob_x = YAW_CENTER[0] + YAW_RADIUS * math.cos(math.radians(yaw_angle))
    yaw_knob_y = YAW_CENTER[1] - YAW_RADIUS * math.sin(math.radians(yaw_angle))

    pygame.draw.line(screen, PURPLE, YAW_CENTER, (yaw_knob_x, yaw_knob_y), 5)
    pygame.draw.circle(screen, PURPLE, (int(yaw_knob_x), int(yaw_knob_y)), 10)

    # Draw Reset Button
    pygame.draw.rect(screen, CYAN, (550, 400, 100, 50))
    font = pygame.font.Font(None, 24)
    text = font.render("RESET", True, PURPLE)
    screen.blit(text, (570, 410))

    # Update display
    pygame.display.flip()
    #clock.tick(30)

# Quit pygame and close serial
pygame.quit()
if ser:
    ser.close()
    print("Serial connection closed")