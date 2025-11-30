import pygame


class PromotionButton:

    def __init__(self, piece_name, button_rect, image):
        self.piece_name = piece_name.lower()
        self.rect = button_rect
        self.image = image
        self.hovered = False
        self.clicked = False
        self.click_animation_time = 0

    def update(self, mouse_pos, dt):
        """Update hover state and click animation."""
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.click_animation_time > 0:
            self.click_animation_time -= dt

    def handle_click(self, mouse_pos):
        """Check if button was clicked."""
        if self.rect.collidepoint(mouse_pos):
            self.clicked = True
            self.click_animation_time = 200  # 200ms animation
            return True
        return False

    def draw(self, surface):
        """Draw button with hover and click effects."""
        # Base color changes on hover
        if self.clicked and self.click_animation_time > 0:
            base_color = (40, 40, 40)  # Darker when clicked
            border_color = (255, 255, 100)  # Yellow flash
        elif self.hovered:
            base_color = (90, 90, 90)  # Lighter on hover
            border_color = (255, 255, 255)
        else:
            base_color = (60, 60, 60)
            border_color = (200, 200, 200)

        pygame.draw.rect(surface, base_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=10)

        # Draw image or fallback text
        if self.image:
            img_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, img_rect)
        else:
            f = pygame.font.Font(None, 18)
            t = f.render(self.piece_name.title(), True, (255, 255, 255))
            surface.blit(t, t.get_rect(center=self.rect.center))

        # Optional: draw piece name label below button
        label_font = pygame.font.Font(None, 16)
        label = label_font.render(self.piece_name.title(), True, (255, 255, 255))
        label_rect = label.get_rect(center=(self.rect.centerx, self.rect.bottom + 12))
        surface.blit(label, label_rect)


def show_pawn_promotion_menu(promoting_color):
    """Display promotion menu and return button objects."""
    if promoting_color is None:
        promoting_color = "white"
    menu_width, menu_height = 400, 300
    screen = pygame.display.get_surface()
    screen_rect = screen.get_rect()
    menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
    menu_rect = menu_surface.get_rect(center=screen_rect.center)

    title_font = pygame.font.Font(None, 36)
    title = title_font.render("Promote Pawn To:", True, (255, 255, 255))
    menu_surface.blit(title, title.get_rect(center=(menu_width // 2, 50)))

    button_w, button_h = 80, 80
    spacing = 20
    pieces = ["Queen", "Rook", "Bishop", "Knight"]

    # Load images
    piece_images = {}
    for name in pieces:
        path = f"images/{promoting_color}_{name.lower()}.png"
        try:
            img = pygame.image.load(path).convert_alpha()
            piece_images[name] = pygame.transform.scale(img, (button_w - 10, button_h - 10))
        except Exception as e:
            print("Image load failed:", path, e)
            piece_images[name] = None

    total_w = len(pieces) * button_w + (len(pieces) - 1) * spacing
    start_x = (menu_width - total_w) // 2
    start_y = (menu_height - button_h) // 2

    # Create button objects
    buttons = []
    for i, name in enumerate(pieces):
        x = start_x + i * (button_w + spacing)
        local_rect = pygame.Rect(x, start_y, button_w, button_h)
        # Convert to screen-space rect
        screen_rect_btn = pygame.Rect(
            menu_rect.x + local_rect.x,
            menu_rect.y + local_rect.y,
            local_rect.width,
            local_rect.height
        )
        button = PromotionButton(name, screen_rect_btn, piece_images[name])
        buttons.append(button)

    screen.blit(menu_surface, menu_rect)
    return buttons, menu_rect  # Return both for redrawing


def draw_promotion_menu(buttons, menu_rect, promoting_color):
    """Redraw menu with updated button states."""
    screen = pygame.display.get_surface()
    menu_width, menu_height = menu_rect.width, menu_rect.height
    menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)

    # Redraw title
    title_font = pygame.font.Font(None, 36)
    title = title_font.render("Promote Pawn To:", True, (255, 255, 255))
    menu_surface.blit(title, title.get_rect(center=(menu_width // 2, 50)))

    # Draw buttons on menu surface (convert screen coords back to local)
    for btn in buttons:
        local_rect = pygame.Rect(
            btn.rect.x - menu_rect.x,
            btn.rect.y - menu_rect.y,
            btn.rect.width,
            btn.rect.height
        )
        # Temporarily adjust button rect for drawing
        original_rect = btn.rect
        btn.rect = local_rect
        btn.draw(menu_surface)
        btn.rect = original_rect  # Restore screen coords



    screen.blit(menu_surface, menu_rect.topleft)   
