import pygame
import math
import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="pkg_resources is deprecated as an API")

# Initialize pygame
pygame.init()

# Colors for light and dark themes
LIGHT_THEME = {
    'bg': (240, 240, 240),
    'display_bg': (255, 255, 255),
    'button_bg': (250, 250, 250),
    'button_hover': (245, 245, 245),
    'button_active': (235, 235, 235),
    'num_button': (255, 255, 255),
    'op_button': (230, 230, 230),
    'func_button': (225, 240, 255),
    'special_button': (255, 240, 225),
    'equals_button': (70, 130, 180),
    'text': (40, 40, 40),
    'secondary_text': (100, 100, 100),
    'border': (220, 220, 220),
    'shadow': (210, 210, 210)
}

DARK_THEME = {
    'bg': (30, 30, 35),
    'display_bg': (45, 45, 50),
    'button_bg': (50, 50, 55),
    'button_hover': (60, 60, 65),
    'button_active': (70, 70, 75),
    'num_button': (60, 60, 65),
    'op_button': (70, 70, 75),
    'func_button': (50, 70, 90),
    'special_button': (90, 70, 50),
    'equals_button': (80, 140, 190),
    'text': (220, 220, 220),
    'secondary_text': (150, 150, 150),
    'border': (60, 60, 65),
    'shadow': (20, 20, 25)
}

# Constants
WIDTH, HEIGHT = 500, 750
DISPLAY_HEIGHT = 180
BUTTON_SIZE = 70
BUTTON_MARGIN = 8
BUTTON_RADIUS = 12
SHADOW_OFFSET = 3

# Set up the display with resizable window
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Scientific Calculator by AKafiq")
clock = pygame.time.Clock()

# Load fonts
def get_font(size):
    return pygame.font.SysFont('Segoe UI', size)

# Calculator state
current_input = "0"
previous_input = ""
operation = None
reset_next_input = False
degree_mode = True
second_mode = False
dark_mode = False
history = []
fullscreen = False

# Button definitions
buttons = [
    # Row 0
    ("2nd", 0, 0, 1, "mode", None, "special"),
    ("sin", 0, 1, 1, "func", "sin", "func"),
    ("cos", 0, 2, 1, "func", "cos", "func"),
    ("tan", 0, 3, 1, "func", "tan", "func"),
    ("π", 0, 4, 1, "const", "pi", "func"),
    ("e", 0, 5, 1, "const", "e", "func"),
    
    # Row 1
    ("√", 1, 0, 1, "func", "sqrt", "func"),
    ("x²", 1, 1, 1, "func", "square", "func"),
    ("xʸ", 1, 2, 1, "op", "**", "func"),
    ("log", 1, 3, 1, "func", "log", "func"),
    ("ln", 1, 4, 1, "func", "ln", "func"),
    ("±", 1, 5, 1, "func", "negate", "func"),
    
    # Row 2
    ("(", 2, 0, 1, "op", "(", "op"),
    (")", 2, 1, 1, "op", ")", "op"),
    ("%", 2, 2, 1, "op", "%", "op"),
    ("AC", 2, 3, 1, "clear", "AC", "special"),
    ("DEL", 2, 4, 1, "clear", "DEL", "special"),
    ("÷", 2, 5, 1, "op", "/", "op"),
    
    # Row 3
    ("7", 3, 0, 1, "num", 7, "num"),
    ("8", 3, 1, 1, "num", 8, "num"),
    ("9", 3, 2, 1, "num", 9, "num"),
    ("×", 3, 3, 1, "op", "*", "op"),
    ("x!", 3, 4, 1, "func", "factorial", "func"),
    ("^", 3, 5, 1, "op", "**", "op"),
    
    # Row 4
    ("4", 4, 0, 1, "num", 4, "num"),
    ("5", 4, 1, 1, "num", 5, "num"),
    ("6", 4, 2, 1, "num", 6, "num"),
    ("-", 4, 3, 1, "op", "-", "op"),
    ("10ˣ", 4, 4, 1, "func", "10^x", "func"),
    ("eˣ", 4, 5, 1, "func", "e^x", "func"),
    
    # Row 5
    ("1", 5, 0, 1, "num", 1, "num"),
    ("2", 5, 1, 1, "num", 2, "num"),
    ("3", 5, 2, 1, "num", 3, "num"),
    ("+", 5, 3, 1, "op", "+", "op"),
    ("asin", 5, 4, 1, "func", "asin", "func"),
    ("acos", 5, 5, 1, "func", "acos", "func"),
    
    # Row 6
    ("0", 6, 0, 2, "num", 0, "num"),
    (".", 6, 2, 1, "num", ".", "num"),
    ("=", 6, 3, 1, "equals", None, "equals"),
    ("atan", 6, 4, 1, "func", "atan", "func"),
    ("☀️", 6, 5, 1, "theme", None, "special"),
]

# Second function mappings
second_functions = {
    "sin": "asin", "cos": "acos", "tan": "atan",
    "asin": "sin", "acos": "cos", "atan": "tan",
    "√": "x²", "x²": "√", "log": "10^x", "ln": "e^x",
    "10^x": "log", "e^x": "ln", "xʸ": "√y"
}

def get_theme():
    return DARK_THEME if dark_mode else LIGHT_THEME

def draw_rounded_rect(surface, rect, color, radius=10, shadow=False):
    theme = get_theme()
    if shadow:
        shadow_rect = rect.copy()
        shadow_rect.x += SHADOW_OFFSET
        shadow_rect.y += SHADOW_OFFSET
        pygame.draw.rect(surface, theme['shadow'], shadow_rect, border_radius=radius)
    
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, theme['border'], rect, 1, border_radius=radius)

def draw_button(label, rect, button_type, is_hover=False, is_active=False):
    theme = get_theme()
    
    # Determine button color based on type and state
    if button_type == "num":
        base_color = theme['num_button']
    elif button_type == "op":
        base_color = theme['op_button']
    elif button_type == "func":
        base_color = theme['func_button']
    elif button_type == "special":
        base_color = theme['special_button']
    elif button_type == "equals":
        base_color = theme['equals_button']
    else:
        base_color = theme['button_bg']
    
    if is_active:
        color = theme['button_active']
    elif is_hover:
        color = theme['button_hover']
    else:
        color = base_color
    
    # Draw button with shadow
    draw_rounded_rect(screen, rect, color, BUTTON_RADIUS, shadow=True)
    
    # Draw the label
    if second_mode and label in second_functions:
        # Draw the second function label
        second_label = second_functions[label]
        text_surface = get_font(18).render(second_label, True, theme['secondary_text'])
        text_rect = text_surface.get_rect(center=(rect.centerx, rect.centery - 8))
        screen.blit(text_surface, text_rect)
        
        # Draw the main label
        text_surface = get_font(22).render(label, True, theme['text'])
        text_rect = text_surface.get_rect(center=(rect.centerx, rect.centery + 10))
        screen.blit(text_surface, text_rect)
    else:
        text_color = theme['text']
        if button_type == "equals":
            text_color = (255, 255, 255)
            
        text_surface = get_font(24).render(label, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

def calculate_function(func, value):
    try:
        num = float(value)
        if func == "sin":
            return math.sin(math.radians(num) if degree_mode else num)
        elif func == "cos":
            return math.cos(math.radians(num) if degree_mode else num)
        elif func == "tan":
            return math.tan(math.radians(num) if degree_mode else num)
        elif func == "asin":
            result = math.asin(num)
            return math.degrees(result) if degree_mode else result
        elif func == "acos":
            result = math.acos(num)
            return math.degrees(result) if degree_mode else result
        elif func == "atan":
            result = math.atan(num)
            return math.degrees(result) if degree_mode else result
        elif func == "sqrt":
            return math.sqrt(num)
        elif func == "square":
            return num * num
        elif func == "log":
            return math.log10(num)
        elif func == "ln":
            return math.log(num)
        elif func == "reciprocal":
            return 1 / num
        elif func == "negate":
            return -num
        elif func == "factorial":
            if num < 0 or num != int(num):
                return "Error"
            return math.factorial(int(num))
        elif func == "10^x":
            return 10 ** num
        elif func == "e^x":
            return math.exp(num)
        elif func == "pi":
            return math.pi
        elif func == "e":
            return math.e
    except:
        return "Error"

def evaluate_expression():
    global current_input, history, previous_input
    
    try:
        # Replace visual representations with Python equivalents
        expression = current_input.replace("×", "*").replace("÷", "/")
        
        # Handle special constants
        expression = expression.replace("π", str(math.pi))
        expression = expression.replace("e", str(math.e))
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": None}, {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "sqrt": math.sqrt,
            "log": math.log10,
            "ln": math.log,
            "pi": math.pi,
            "e": math.e
        })
        
        # Format the result
        if result == int(result):
            current_input = str(int(result))
        else:
            current_input = str(round(result, 10))
            
        # Add to history
        history.insert(0, f"{expression} = {current_input}")
        if len(history) > 5:
            history.pop()
            
    except Exception as e:
        current_input = "Error"

def toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

## Main loop
running = True
active_button = None
hover_button = None

while running:
    theme = get_theme()
    screen.fill(theme['bg'])
    
    # Get current window size
    win_width, win_height = screen.get_size()
    
    # Calculate scaling factors
    scale_x = win_width / WIDTH
    scale_y = win_height / HEIGHT
    scale = min(scale_x, scale_y)
    
    # Calculate offset to center the calculator
    offset_x = (win_width - WIDTH * scale) / 2
    offset_y = (win_height - HEIGHT * scale) / 2
    
    # Draw display area
    display_rect = pygame.Rect(offset_x + 20 * scale, offset_y + 20 * scale, 
                              (WIDTH-40) * scale, DISPLAY_HEIGHT * scale)
    # FIX: Convert the radius to an integer before passing it to the function
    draw_rounded_rect(screen, display_rect, theme['display_bg'], int(15 * scale))
    
    # Draw previous input
    prev_text = get_font(int(22 * scale)).render(previous_input, True, theme['secondary_text'])
    screen.blit(prev_text, (offset_x + 40 * scale, offset_y + 40 * scale))
    
    # Draw current input with a scrolling effect if it's too long
    if len(current_input) > 25:
        display_text = "..." + current_input[-22:]
    else:
        display_text = current_input
        
    current_text = get_font(int(42 * scale)).render(display_text, True, theme['text'])
    screen.blit(current_text, (offset_x + 40 * scale, offset_y + 90 * scale))
    
    # Draw mode indicators
    mode_text = get_font(int(18 * scale)).render("DEG" if degree_mode else "RAD", True, theme['secondary_text'])
    screen.blit(mode_text, (offset_x + (WIDTH - 80) * scale, offset_y + 40 * scale))
    
    if second_mode:
        second_text = get_font(int(18 * scale)).render("2nd", True, theme['secondary_text'])
        screen.blit(second_text, (offset_x + (WIDTH - 120) * scale, offset_y + 40 * scale))
    
    # Draw buttons
    button_rects = []
    for label, row, col, width, func_type, value, button_type in buttons:
        x = offset_x + (col * (BUTTON_SIZE + BUTTON_MARGIN) + 20) * scale
        y = offset_y + (row * (BUTTON_SIZE + BUTTON_MARGIN) + DISPLAY_HEIGHT + 40) * scale
        button_width = (width * BUTTON_SIZE + (width - 1) * BUTTON_MARGIN) * scale
        button_height = BUTTON_SIZE * scale
        
        button_rect = pygame.Rect(x, y, button_width, button_height)
        
        is_hover = hover_button == (label, func_type, value)
        is_active = active_button == (label, func_type, value)
        
        draw_button(label, button_rect, button_type, is_hover, is_active)
        button_rects.append((button_rect, label, func_type, value, button_type))
    
    # Draw history
    history_y = offset_y + (DISPLAY_HEIGHT + 40 + 7 * (BUTTON_SIZE + BUTTON_MARGIN) + 20) * scale
    for i, item in enumerate(history[:3]):
        history_text = get_font(int(16 * scale)).render(item, True, theme['secondary_text'])
        screen.blit(history_text, (offset_x + 20 * scale, history_y + i * 25 * scale))
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE and fullscreen:
                toggle_fullscreen()
        
        elif event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            hover_button = None
            for rect, label, func_type, value, button_type in button_rects:
                if rect.collidepoint(pos):
                    hover_button = (label, func_type, value)
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            for rect, label, func_type, value, button_type in button_rects:
                if rect.collidepoint(pos):
                    active_button = (label, func_type, value)
                    
                    if func_type == "num":
                        if reset_next_input:
                            current_input = str(value)
                            reset_next_input = False
                        else:
                            if current_input == "0" and value != ".":
                                current_input = str(value)
                            else:
                                current_input += str(value)
                    
                    elif func_type == "op":
                        current_input += f" {value} "
                        reset_next_input = False
                    
                    elif func_type == "func":
                        actual_func = second_functions[label] if second_mode and label in second_functions else label
                        result = calculate_function(actual_func, current_input)
                        
                        if result != "Error":
                            current_input = str(result)
                        else:
                            current_input = "Error"
                        reset_next_input = True
                    
                    elif func_type == "const":
                        current_input = str(calculate_function(value, "0"))
                        reset_next_input = True
                    
                    elif func_type == "clear":
                        if label == "AC":
                            current_input = "0"
                            previous_input = ""
                            operation = None
                        elif label == "DEL":
                            if len(current_input) > 1:
                                current_input = current_input[:-1]
                            else:
                                current_input = "0"
                    
                    elif func_type == "mode":
                        if label == "2nd":
                            second_mode = not second_mode
                    
                    elif func_type == "theme":
                        dark_mode = not dark_mode
                    
                    elif func_type == "equals":
                        previous_input = current_input
                        evaluate_expression()
                        reset_next_input = True
                    
                    break
        
        elif event.type == pygame.MOUSEBUTTONUP:
            active_button = None
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
