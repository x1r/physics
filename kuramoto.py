from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from pygame_widgets.toggle import Toggle
import pygame
import math
import pygame_widgets
import itertools


class Operator:
    """
    A class to represent an operator in the simulation.
    """

    def __init__(self, name, freq, phase):
        self.name = name
        self.freq = freq
        self.phase = phase


class Settings:
    """
    A class to store all the settings for the simulation.
    """
    K = 0.0
    dt = 0.1
    dt_counter = 0
    syncTrue = False
    syncTime = 0
    run = True
    showSync = True
    syncStatus = 0
    max_distance = [[0, 1, 2, 0, 0]
                    for _ in range(500)]  # [distance, operator i, operator j]


# operators [name, frequency, phase]
# frequencies given are 1,2,4
operator1 = Operator("operator1", 1, 0)
operator2 = Operator("operator2", 0.5, 5)
operator3 = Operator("operator3", 0.25, 10)
allOperators = [operator1, operator2, operator3]


def rk4(deriv, y, dt):
    """
    Runge-Kutta 4th order method for solving differential equations.
    :param deriv: The derivative function.
    :param y: The initial value.
    :param dt: The time step.
    :return: The updated value.
    """
    k1 = dt * deriv(y)
    k2 = dt * deriv(y + k1 / 2)
    k3 = dt * deriv(y + k2 / 2)
    k4 = dt * deriv(y + k3)
    return (k1 + 2 * k2 + 2 * k3 + k4) / 6


def update() -> None:
    """
    Update the phases of the operators.
    :return: None
    """
    K = Settings.K
    dt = Settings.dt  # Time step for RK4 integration

    # Calculating the derivatives of the phases

    def dPhase1(phase):
        return operator1.freq + K * \
            (math.sin(operator2.phase - phase) +
             math.sin(operator3.phase - phase))

    def dPhase2(phase):
        return operator2.freq + K * \
            (math.sin(operator1.phase - phase) +
             math.sin(operator3.phase - phase))

    def dPhase3(phase):
        return operator3.freq + K * \
            (math.sin(operator1.phase - phase) +
             math.sin(operator2.phase - phase))

    # Updating the phases using RK4 method

    rk4op1 = rk4(dPhase1, operator1.phase, dt)
    rk4op2 = rk4(dPhase2, operator2.phase, dt)
    rk4op3 = rk4(dPhase3, operator3.phase, dt)
    operator1.phase += rk4op1
    operator2.phase += rk4op2
    operator3.phase += rk4op3

    # Wrapping the phases within the range [0, 2*pi)
    operator1.phase %= 2 * math.pi
    operator2.phase %= 2 * math.pi
    operator3.phase %= 2 * math.pi


def getPosition(operator: Operator) -> tuple[float, float]:
    """
    Return a tuple with x,y coordinates representing the position of the operator.
    :param operator: An Operator object.
    :return: A tuple containing the x and y coordinates of the operator.
    """
    x = -200 * math.cos(operator.phase) + 640
    y = 200 * math.sin(operator.phase) + 360
    return (x, y)


def draw_circles() -> None:
    """
    Draw the circles representing the operators.
    :return: None
    """
    # Colors
    op1_color: tuple[int, int, int] = (255, 0, 0)  # Red
    op2_color: tuple[int, int, int] = (255, 255, 0)  # Yellow
    op3_color: tuple[int, int, int] = (0, 0, 255)  # Blue
    # White background
    screen.fill((255, 255, 255))
    # Draw a big circle
    pygame.draw.circle(screen, (0, 0, 0), (640, 360),
                       200, width=5)
    # Draw operator1
    pygame.draw.circle(screen, op1_color,
                       getPosition(operator1), 10)
    # Draw operator2
    pygame.draw.circle(screen, op2_color,
                       getPosition(operator2),
                       10)
    # Draw operator3
    pygame.draw.circle(screen, op3_color,
                       getPosition(operator3),
                       10)


def getDistance(operator1: Operator, operator2: Operator, r: float = 200) -> float:
    # Get the phase of each operator
    angle1 = operator1.phase
    angle2 = operator2.phase
    # Calculate the absolute angular difference
    angular_distance = abs(angle1 - angle2)
    # Take the shorter angular distance considering the circular nature
    angular_distance = min(angular_distance, 2 * math.pi - angular_distance)
    # Calculate the actual distance on the circle
    distance = r * angular_distance
    # Return the distance
    return distance


def draw_lines(i: Operator, j: Operator) -> None:
    """
    Draw lines between operators based on their distance.
    :return: None
    """
    # Colors
    black_color: tuple[int, int, int] = (0, 0, 0)
    # Draw lines between operators
    pygame.draw.line(screen, black_color,
                     getPosition(allOperators[i - 1]), getPosition(allOperators[j - 1]), 3)


# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Kuramoto Model")

left_x_border = 0
left_y_border = -25

k_slider = Slider(screen, left_x_border + 50, left_y_border + 50, 200, 20, min=0, max=2,
                  step=0.001, initial=0.2, handleColour=(0, 0, 0))
K_text = TextBox(screen, left_x_border + 90, left_y_border +
                 80, 70, 30, fontSize=20, inputBox=True, inputType='numeric')
K_text.disable()

dt_slider = Slider(screen, left_x_border + 50, left_y_border + 150, 200, 20, min=0, max=1,
                   step=0.001, initial=0.01, handleColour=(0, 0, 0))
dt_text = TextBox(screen, left_x_border + 90, left_y_border +
                  180, 70, 30, fontSize=20, inputBox=True, inputType='numeric')
dt_text.disable()
clock = pygame.time.Clock()
# add text to the screen
op_colors = TextBox(screen, left_x_border + 50,
                    left_y_border + 220, 150, 30, fontSize=20)
op_colors.setText("Colors of operators:")
op1_text_color = TextBox(screen, left_x_border + 50,
                         left_y_border + 250, 150, 30, fontSize=20)
op1_text_color.setText("Red - 1 (freq = 4)")
op2_text_color = TextBox(screen, left_x_border + 50,
                         left_y_border + 280, 150, 30, fontSize=20)
op2_text_color.setText("Yellow - 2 (freq = 2)")
op3_text_color = TextBox(screen, left_x_border + 50,
                         left_y_border + 310, 150, 30, fontSize=20)
op3_text_color.setText("Blue - 3 (freq = 1)")

# Define the positions for the "+" and "-" buttons
button_x = left_x_border + 50
button_y = left_y_border + 80

# Create the "+" button for K
k_plusButton = Button(screen, button_x + 120, button_y, 30, 30, text='+', fontSize=20,
                      inactiveColour=(100, 100, 100), pressedColour=(150, 150, 150))
k_plusButton.setInactiveColour((200, 200, 200))

# Create the "-" button for K
k_minusButton = Button(screen, button_x, button_y, 30, 30, text='-', fontSize=20,
                       inactiveColour=(100, 100, 100), pressedColour=(150, 150, 150))
k_minusButton.setInactiveColour((200, 200, 200))

# Create the "+" button for dt
dt_plusButton = Button(screen, button_x + 120, button_y + 100, 30, 30, text='+', fontSize=20,
                       inactiveColour=(100, 100, 100), pressedColour=(150, 150, 150))
dt_plusButton.setInactiveColour((200, 200, 200))

# Create the "-" button for dt
dt_minusButton = Button(screen, button_x, button_y + 100, 30, 30, text='-', fontSize=20,
                        inactiveColour=(100, 100, 100), pressedColour=(150, 150, 150))
dt_minusButton.setInactiveColour((200, 200, 200))

draw_linesActive = False


def toggle_draw_lines():
    global draw_linesActive
    draw_linesActive = not draw_linesActive
    print("toggle_draw_lines()")


draw_linesButton = Button(screen, button_x, button_y + 280, 150, 30, text='Draw lines', fontSize=20,
                          inactiveColour=(100, 100, 100), pressedColour=(150, 150, 150), onClick=toggle_draw_lines)
draw_linesButton.setInactiveColour((200, 200, 200))

while Settings.run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Settings.run = False
    update()
    draw_circles()

    if k_plusButton.clicked:
        # Increase K value by 0.1
        k_slider.setValue(k_slider.getValue() + 0.0001)
    if k_minusButton.clicked:
        # Decrease K value by 0.1
        k_slider.setValue(k_slider.getValue() - 0.0001)
    if dt_plusButton.clicked:
        # Increase dt value by 0.001
        dt_slider.setValue(dt_slider.getValue() + 0.001)
    if dt_minusButton.clicked:
        # Decrease dt value by 0.001
        dt_slider.setValue(dt_slider.getValue() - 0.001)

    # Draw the buttons on the screen
    k_plusButton.draw()
    k_minusButton.draw()
    dt_plusButton.draw()
    dt_minusButton.draw()

    K_val = round(k_slider.getValue(), 3)
    K_text.setText(f"K = {K_val:.3f}")
    if K_val != Settings.K:
        Settings.syncTrue = False
        Settings.syncTime = 0
        Settings.showSync = False
    Settings.K = K_val

    dt_val = round(dt_slider.getValue(), 3)
    dt_text.setText(f"dt = {dt_val:.3f}")
    if dt_val != Settings.dt:
        Settings.syncTrue = False
        Settings.syncTime = 0
        Settings.showSync = False
    Settings.dt = dt_val

    Settings.dt_counter += dt_slider.getValue()
    font = pygame.font.SysFont("comicsansms", 20)
    text = font.render(
        f"t={round(Settings.dt_counter, 3):.2f}", True, (0, 0, 0))
    screen.blit(text, (1090, 160))

    current_max_distance = getDistance(operator1, operator2)
    current_max_distance_indexes = [1, 2]

    for idx, (i, j) in enumerate(itertools.combinations([operator1, operator2, operator3], 2)):
        if getDistance(i, j) > current_max_distance:
            current_max_distance = getDistance(i, j)
            current_max_distance_indexes = [int(i.name[-1]), int(j.name[-1])]

    theOtherOperator = 1 + 2 + 3 - sum(current_max_distance_indexes)
    theOtherDistance1 = getDistance(allOperators[current_max_distance_indexes[0] - 1],
                                    allOperators[theOtherOperator - 1])
    theOtherDistance2 = getDistance(allOperators[current_max_distance_indexes[1] - 1],
                                    allOperators[theOtherOperator - 1])
    Settings.max_distance = Settings.max_distance[1:]
    Settings.max_distance.append(
        [current_max_distance, *current_max_distance_indexes, theOtherDistance1, theOtherDistance2])

    if draw_linesActive:
        draw_lines(*current_max_distance_indexes)
        draw_lines(current_max_distance_indexes[0], theOtherOperator)
        draw_lines(current_max_distance_indexes[1], theOtherOperator)

    Settings.showSync = True
    for i in range(1, 500):
        if Settings.max_distance[i][0] - Settings.max_distance[i - 1][0] > 0.001:
            Settings.showSync = False
            syncTrue = False
            syncTime = 0
            break

    if Settings.showSync:
        Settings.syncTrue = True
        Settings.syncTime = Settings.dt_counter - 350 * \
                            Settings.dt if Settings.syncTime == 0 else Settings.syncTime

    if Settings.syncTime > 0:
        text = font.render(
            f"Synchronized at t=~{str(round(Settings.syncTime, 3))}", True, (0, 0, 0))
        screen.blit(text, (1015, 120))

    text = font.render(f"Max distance between points", True, (0, 0, 0))
    screen.blit(text, (1000, 10))
    string_to_render = f"{Settings.max_distance[-1][1]} - {Settings.max_distance[-1][2]} = {round(Settings.max_distance[-1][0], 3):.3f}"
    text = font.render(string_to_render, True, (0, 0, 0))
    screen.blit(text, (1050, 35))
    string_to_render = f"{Settings.max_distance[-1][1]} - {theOtherOperator} = {round(Settings.max_distance[-1][3], 3):.3f}"
    text = font.render(string_to_render, True, (0, 0, 0))
    screen.blit(text, (1050, 60))
    string_to_render = f"{Settings.max_distance[-1][2]} - {theOtherOperator} = {round(Settings.max_distance[-1][4], 3):.3f}"
    text = font.render(string_to_render, True, (0, 0, 0))
    screen.blit(text, (1050, 85))

    pygame_widgets.update(pygame.event.get())

    pygame.display.flip()

pygame.display.quit()

pygame.quit()
