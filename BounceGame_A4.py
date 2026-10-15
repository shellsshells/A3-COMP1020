#Ian Kim

import pygame, sys, math, random

# Test if two sprite masks overlap
def pixel_collision(mask1, rect1, mask2, rect2):
    offset_x = rect2[0] - rect1[0]
    offset_y = rect2[1] - rect1[1]
    # See if the two masks at the offset are overlapping.
    overlap = mask1.overlap(mask2, (offset_x, offset_y))
    if overlap:
        return True
    else:
        return False

class Sprite:
    def __init__(self, image):
        self.image = image
        self.rectangle = image.get_rect()
        self.mask = pygame.mask.from_surface(image)

    def draw(self, screen):
        screen.blit(self.image, self.rectangle)

    def is_colliding(self, other_sprite):
        return pixel_collision(self.mask, self.rectangle, other_sprite.mask, other_sprite.rectangle)


class Player(Sprite):
    def __init__(self, image):
        super().__init__(image)

    def set_position(self, new_position):
        self.rectangle.center = new_position

    def set_image(self, image):
        center = self.rectangle.center
        self.image = image
        self.rectangle = image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(image)


class Enemy(Sprite):
    def __init__(self, image, width, height):
        super().__init__(image)

        half_w = self.rectangle.width // 2
        half_h = self.rectangle.height // 2
        x = random.randint(half_w, width - half_w)
        y = random.randint(half_h, height - half_h)
        self.rectangle.center = (x, y)

        vx = random.randint(1, 4) * random.choice([-1, 1])
        vy = random.randint(1, 4) * random.choice([-1, 1])
        self.speed = (vx, vy)

    def move(self):
        vx, vy = self.speed
        self.rectangle.move_ip(vx, vy)

    def bounce(self, width, height):
        vx, vy = self.speed
        if self.rectangle.left < 0 or self.rectangle.right > width:
            vx = -vx
        if self.rectangle.top < 0 or self.rectangle.bottom > height:
            vy = -vy
        self.speed = (vx, vy)


class PlatformEnemy(Enemy):
    def __init__(self, image, width, height):
        super().__init__(image, width, height)
        vx, vy = self.speed
        self.speed = (vx, 0)


class PowerUp(Sprite):
    def __init__(self, image, width, height):
        super().__init__(image)

        half_w = self.rectangle.width // 2
        half_h = self.rectangle.height // 2
        x = random.randint(half_w, width - half_w)
        y = random.randint(half_h, height - half_h)
        self.rectangle.center = (x, y)


class RotatingPowerUp(PowerUp):
    def __init__(self, image, width, height):
        super().__init__(image, width, height)
        self.angle = 0
        self.original_image = image

    def draw(self, screen):
        self.angle = self.angle + 3
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        self.image = rotated_image

        center = self.rectangle.center
        self.rectangle = self.image.get_rect()
        self.rectangle.center = center

        self.mask = pygame.mask.from_surface(self.image)

        super().draw(screen)


def main():
    # Setup pygame
    pygame.init()

    # Get a font for printing the lives left on the screen.
    myfont = pygame.font.SysFont('monospace', 24)

    # Define the screen
    width, height = 600, 400
    size = width, height
    screen = pygame.display.set_mode((width, height))

    # Load image assets
    enemy = pygame.image.load("sprites/fire.png").convert_alpha()
    enemy_image = pygame.transform.smoothscale(enemy, (50, 50))

    platform_enemy = pygame.image.load("sprites/fire.png").convert_alpha()
    platform_enemy_image = pygame.transform.smoothscale(platform_enemy, (70, 35))

    enemy_sprites = []
    for i in range(2):
        enemy_sprites.append(Enemy(enemy_image, width, height))
    for i in range(2):
        enemy_sprites.append(PlatformEnemy(platform_enemy_image, width, height))

    player_image = pygame.image.load("sprites/ice.png").convert_alpha()
    player_sprite = Player(player_image)
    life = 5
    base_player_image = player_image
    base_w, base_h = base_player_image.get_size()
    frame_count = 0

    powerup_image = pygame.image.load("sprites/flake.png").convert_alpha()
    rotating_powerup = pygame.image.load("sprites/flake2.png").convert_alpha()
    rotating_powerup_image = pygame.transform.smoothscale(rotating_powerup, (40, 40))
    powerups = []

    # Main part of the game
    is_playing = True
    while is_playing and life > 0:

        # Check for events
        for event in pygame.event.get():
            # Stop loop if click on window close button
            if event.type == pygame.QUIT:
                is_playing = False

        # Make the player follow the mouse
        pos = pygame.mouse.get_pos()
        player_sprite.set_position(pos)

        for enemy_sprite in enemy_sprites:
            if player_sprite.is_colliding(enemy_sprite):
                life -= 0.2

        for powerup_sprite in powerups:
            if player_sprite.is_colliding(powerup_sprite):
                life += 1

        powerups = [p for p in powerups if not player_sprite.is_colliding(p)]

        life = life - 0.004
        frame_count = frame_count + 1

        scale = life / 5
        if scale < 0.3:
            scale = 0.3
        if scale > 1.5:
            scale = 1.5

        new_width = int(base_w * scale)
        new_height = int(base_h * scale)
        small_image = pygame.transform.smoothscale(base_player_image, (new_width, new_height))
        player_sprite.set_image(small_image)

        if frame_count % 400 == 0:
            enemy_sprites.append(Enemy(enemy_image, width, height))

        for enemy_sprite in enemy_sprites:
            enemy_sprite.move()
            enemy_sprite.bounce(width, height)

        if random.randint(1, 120) == 1:
            if random.randint(1, 3) == 1:
                powerups.append(RotatingPowerUp(rotating_powerup_image, width, height))
            else:
                powerups.append(PowerUp(powerup_image, width, height))

        # Erase the screen with a background color
        screen.fill((220, 235, 245))

        # Draw the characters
        for enemy_sprite in enemy_sprites:
            enemy_sprite.draw(screen)
        for powerup_sprite in powerups:
            powerup_sprite.draw(screen)

        player_sprite.draw(screen)

        # Write the life to the screen.
        text = "Life: " + str('%.1f' % life)
        life_banner = myfont.render(text, True, (20, 60, 100))
        screen.blit(life_banner, (20, 20))

        # Bring all the changes to the screen into view
        pygame.display.update()
        # Pause for a few milliseconds
        pygame.time.wait(20)

    # Once the game loop is done, pause, close the window and quit.
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
