'''
worlds_hardest_game.py
Eugene Chau
Last edited 17 June 2020
Version 1.0
The player controls a red block with the arrow keys and must navigate
through a sea of deadly enemy blocks to get to the green goal. Four challenging
levels make up the world's truly hardest game!
'''

import pygame
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
LIME_GREEN = (50, 205, 50)
MAGENTA = (255, 0, 255)

FPS = 60
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 3

class EnemyBlock(pygame.sprite.Sprite):
    """ Represents an enemy block (a black block) """
    def __init__(self, level, velocity_x, velocity_y):
        """
        Constructs an EnemyBlock with the specified x and y velocities. The
        level parameter represents the Level that the EnemyBlock is in.
        """
        super(EnemyBlock, self).__init__()

        self.image = pygame.Surface([10, 10])
        self.image.fill(BLACK)

        self.rect = self.image.get_rect()

        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

        # The Level that the EnemyBlock is in.
        self.level = level

    def update(self):
        """
        Updates the position of the EnemyBlock according to the block's velocity.
        Makes the block bounce off of any RectWall.
        """
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        walls_hit = pygame.sprite.spritecollide(self, self.level.wall_list, False)
        if len(walls_hit) == 1:
            wall = walls_hit[0]
            if (self.velocity_x > 0 and wall.rect.x <= self.rect.x + self.rect.width <= wall.rect.x + self.velocity_x
                    or self.velocity_x < 0 and wall.rect.x + wall.rect.width + self.velocity_x <= self.rect.x <= wall.rect.x + wall.rect.width):
                self.velocity_x *= -1
            if (self.velocity_y > 0 and wall.rect.y <= self.rect.y + self.rect.height <= wall.rect.y + self.velocity_y
                    or self.velocity_y < 0 and wall.rect.y + wall.rect.height + self.velocity_y <= self.rect.y <= wall.rect.y + wall.rect.height):
                self.velocity_y *= -1
        elif len(walls_hit) == 2: # the block hit a corner where two walls intersect
            self.velocity_x *= -1
            self.velocity_y *= -1

class BouncingEnemyBlock(EnemyBlock):
    """
    Represents an EnemyBlock that bounces off of other EnemyBlocks as well
    as RectWalls
    """
    def __init__(self, level, velocity_x, velocity_y):
        super(BouncingEnemyBlock, self).__init__(level, velocity_x, velocity_y)

        self.image.fill(MAGENTA)

    def update(self):
        super(BouncingEnemyBlock, self).update()

        enemy_blocks_hit = pygame.sprite.spritecollide(self, self.level.enemy_block_list, False)
        if len(enemy_blocks_hit) > 1: # Must be greater than 1 because the sprite always "collides" with itself
            self.velocity_x *= -1
            self.velocity_y *= -1

class Player(pygame.sprite.Sprite):
    """ Represents the Player (the red block) """
    def __init__(self, level, init_pos_x, init_pos_y, width, height):
        """
        Initializes the Player with the specified initial x and y positions, and
        the specified width and height. The level parameter indicates which Level
        the Player is in.
        """
        super(Player, self).__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = init_pos_x
        self.rect.y = init_pos_y

        self.init_pos = [init_pos_x, init_pos_y]

        self.velocity_x = 0
        self.velocity_y = 0

        # The level that the Player is currently in.
        self.level = level

        # Number of times the Player has died
        self.deaths = 0

        # Represents whether the Player has gotten hit by an enemy within
        # the last second
        self.hit_by_enemy = False

        # The number of ticks since the Player was hit by an enemy. Set to
        # FPS + 1 if self.hit_by_enemy == False
        self.ticks_since_hit = FPS + 1

        # Represents whether the Player has reached the goal of the Level
        self.reached_goal = False

    # Methods for controlling player movement
    def go_left(self):
        self.velocity_x -= PLAYER_SPEED

    def go_right(self):
        self.velocity_x += PLAYER_SPEED

    def go_up(self):
        self.velocity_y -= PLAYER_SPEED

    def go_down(self):
        self.velocity_y += PLAYER_SPEED

    def update(self):
        """ Updates the Player's position. """
        # If the Player has been hit by an enemy, they cannot move for 1 second.
        if self.hit_by_enemy and self.ticks_since_hit <= FPS * 2:
            self.ticks_since_hit += 1

            # Make the Player translucent
            self.image.set_alpha(75)

            if self.ticks_since_hit > FPS:
                # 1 second has passed since the Player has been hit by an enemy.
                self.hit_by_enemy = False

                # Remove the Player's transparency
                self.image.set_alpha(None)

                self.rect.x = self.init_pos[0]
                self.rect.y = self.init_pos[1]
        else:
            self.rect.x += self.velocity_x
            self.rect.y += self.velocity_y
            enemies_hit = pygame.sprite.spritecollide(self, self.level.enemy_block_list, False)
            if len(enemies_hit) > 0:
                self.hit_by_enemy = True
                self.ticks_since_hit = 0
                self.deaths += 1

            # Check if the Player hit a wall, and adjust the Player's position accordingly.
            walls_hit = pygame.sprite.spritecollide(self, self.level.wall_list, False)
            for wall in walls_hit:
                if wall == self.level.goal:
                    self.reached_goal = True
                    return # Immediately exits the method without running the rest of the code.

            if len(walls_hit) == 1:
                wall = walls_hit[0]
                if self.velocity_x > 0 and wall.rect.x <= self.rect.x + self.rect.width <= wall.rect.x + self.velocity_x:
                    self.rect.x = wall.rect.x - self.rect.width
                elif self.velocity_x < 0 and wall.rect.x + wall.rect.width + self.velocity_x <= self.rect.x <= wall.rect.x + wall.rect.width:
                    self.rect.x = wall.rect.x + wall.rect.width
                if self.velocity_y > 0 and wall.rect.y <= self.rect.y + self.rect.height <= wall.rect.y + self.velocity_y:
                    self.rect.y = wall.rect.y - self.rect.height
                elif self.velocity_y < 0 and wall.rect.y + wall.rect.height + self.velocity_y <= self.rect.y <= wall.rect.y + wall.rect.height:
                    self.rect.y = wall.rect.y + wall.rect.height
            elif len(walls_hit) == 2: # the Player hit a corner where two walls intersect
                self.rect.x -= self.velocity_x
                self.rect.y -= self.velocity_y

    def draw(self, surface):
        """ Draws the Player on the specified surface """
        pygame.draw.rect(surface, RED, self.rect)

class Level(object):
    """
    A superclass for all Levels. Every Level has a "player" attribute, which is
    a Player object, and a "goal" attribute, which is a Goal object. In addition,
    every Level has an "enemy_block_list" that stores EnemyBlock objects, a "wall_list"
    that stores RectWall objects, and an "all_sprites_list" that contains all of the
    sprites in the Level.
    """
    def __init__(self):
        """ Initializes the Level and all objects within """
        super(Level, self).__init__()

        self.enemy_block_list = pygame.sprite.Group()
        self.wall_list = pygame.sprite.Group()

        # all_sprites_list contains every object in the Level. Add
        # all objects to the list after instantiation.
        self.all_sprites_list = pygame.sprite.Group()

        # The following two fields must be initialized if subclassing Level

        # a Player object
        self.player = None

        # a Goal object. The goal MUST be the first object in self.wall_list
        self.goal = None

    def draw(self, surface):
        """
        Draws all objects in the Level on the specified surface.
        In addition, displays a "deaths" counter in the top-left corner.
        """
        self.all_sprites_list.draw(surface)

        # Displays deaths counter in the top-left corner.
        deaths_font = pygame.font.SysFont("Arial", 20, True)

        deaths_text = deaths_font.render("Deaths: " + str(self.player.deaths), False, BLUE)

        surface.blit(deaths_text, [10, 10])

    def update(self):
        """ Updates all objects in the Level """
        self.all_sprites_list.update()

class Level_01(Level):
    """ Represents Level 1 """
    def __init__(self):
        """ Initializes Level 1 and all objects within """
        super(Level_01, self).__init__()

        # Initialize enemy blocks
        for i in range(12):
            enemy_block = EnemyBlock(self, 0, 2)
            enemy_block.rect.x = 100 + 50 * i
            enemy_block.rect.y = 400
            self.enemy_block_list.add(enemy_block)

        # Initialize boundaries of the level
        left_boundary = RectWall(0, 0, 50, SCREEN_HEIGHT, CYAN)
        right_boundary = RectWall(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT, CYAN)
        top_boundary = RectWall(0, 0, SCREEN_WIDTH, 50, CYAN)
        bottom_boundary = RectWall(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, CYAN)

        # The goal that the Player must reach to pass the Level
        self.goal = Goal(right_boundary.rect.x - 50, top_boundary.rect.height, 50, SCREEN_HEIGHT - 100)

        self.wall_list.add(self.goal, left_boundary, right_boundary, top_boundary, bottom_boundary)

        self.player = Player(self, left_boundary.rect.width + 10, bottom_boundary.rect.y - 20, 10, 10)

        self.all_sprites_list.add(self.enemy_block_list, self.wall_list, self.player)

    def draw(self, surface):
        # Call the super class's draw() method
        super(Level_01, self).draw(surface)

        tips_font = pygame.font.SysFont("Arial", 32)
        tips_text = tips_font.render("Move your red block using the arrow keys.", False, RED)
        surface.blit(tips_text, [60, 60])
        tips_text = tips_font.render("Get to the green goal ==>", False, LIME_GREEN)
        surface.blit(tips_text, [self.goal.rect.x - tips_text.get_width() - 50, SCREEN_HEIGHT - tips_text.get_height() - 100])
        tips_text = tips_font.render("Don't touch the black blocks!", False, BLACK)
        surface.blit(tips_text, [60, 140])

class Level_02(Level):
    """ Represents Level 2 """
    def __init__(self):
        """ Initializes Level 2 and all objects within """
        super(Level_02, self).__init__()

        # Initialize enemy blocks

        # === Vertically-moving blocks ===
        for i in range(14):
            enemy_block = EnemyBlock(self, 0, 5)
            enemy_block.rect.x = 50 + 50 * i
            enemy_block.rect.y = 100
            self.enemy_block_list.add(enemy_block)

        # === Horizontally-moving blocks ===
        for i in range(10):
            enemy_block = EnemyBlock(self, 5, 0)
            enemy_block.rect.x = 150
            enemy_block.rect.y = 75 + 50 * i
            self.enemy_block_list.add(enemy_block)

        # Initialize boundaries of the level
        left_boundary = RectWall(0, 0, 50, SCREEN_HEIGHT, CYAN)
        right_boundary = RectWall(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT, CYAN)
        top_boundary = RectWall(0, 0, SCREEN_WIDTH, 50, CYAN)
        bottom_boundary = RectWall(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, CYAN)

        # The goal that the Player must reach to pass the Level
        self.goal = Goal(left_boundary.rect.width, bottom_boundary.rect.y - 50, 50, 50)

        self.wall_list.add(self.goal, left_boundary, right_boundary, top_boundary, bottom_boundary)

        self.player = Player(self, right_boundary.rect.x - 20, top_boundary.rect.height + 10, 10, 10)
        self.all_sprites_list.add(self.enemy_block_list, self.wall_list, self.player)

class Level_03(Level):
    """ Represents Level 3 """
    def __init__(self):
        """ Initializes Level 3 and all objects within """
        super(Level_03, self).__init__()

        # Initialize enemy blocks

        # === Vertically-moving blocks ===
        for i in range(7):
            enemy_block = EnemyBlock(self, 0, 3)
            enemy_block.rect.x = 50 + 45 * i
            enemy_block.rect.y = 75
            self.enemy_block_list.add(enemy_block)

        for i in range(11):
            enemy_block = EnemyBlock(self, 0, 3)
            enemy_block.rect.x = 250 + 45 * i
            enemy_block.rect.y = 525
            self.enemy_block_list.add(enemy_block)

        # === Horizontally-moving blocks ===
        for i in range(7):
            enemy_block = EnemyBlock(self, 3, 0)
            enemy_block.rect.x = 75
            enemy_block.rect.y = 90 + 75 * i
            self.enemy_block_list.add(enemy_block)

        for i in range(6):
            enemy_block = EnemyBlock(self, 3, 0)
            enemy_block.rect.x = 625
            enemy_block.rect.y = 125 + 75 * i
            self.enemy_block_list.add(enemy_block)

        # Initialize boundaries of the level
        left_boundary = RectWall(0, 0, 50, SCREEN_HEIGHT, CYAN)
        right_boundary = RectWall(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT, CYAN)
        top_boundary = RectWall(0, 0, SCREEN_WIDTH, 50, CYAN)
        bottom_boundary = RectWall(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, CYAN)

        vertical_wall = RectWall(SCREEN_WIDTH / 2 - 20, top_boundary.rect.height, 40, SCREEN_HEIGHT / 2 - top_boundary.rect.height, CYAN)
        horizontal_wall = RectWall(SCREEN_WIDTH / 2 - 200, vertical_wall.rect.y + 50, 400, 400, CYAN)

        self.goal = Goal(vertical_wall.rect.x + vertical_wall.rect.width, top_boundary.rect.height, 60, horizontal_wall.rect.y - top_boundary.rect.height)

        self.wall_list.add(self.goal, vertical_wall, horizontal_wall, left_boundary, right_boundary, top_boundary, bottom_boundary)

        self.player = Player(self, vertical_wall.rect.x - 20, vertical_wall.rect.y + 10, 10, 10)
        self.all_sprites_list.add(self.enemy_block_list, self.wall_list, self.player)

class Level_04(Level):
    """ Represents Level 4 """
    def __init__(self):
        """ Initializes Level 4 and all objects within """
        super(Level_04, self).__init__()

        # Initialize enemy blocks

        for i in range(16):
            enemy_block = BouncingEnemyBlock(self, 0, 5)
            enemy_block.rect.x = 60 + 45 * i
            enemy_block.rect.y = 200
            self.enemy_block_list.add(enemy_block)

        for i in range(10):
            enemy_block = BouncingEnemyBlock(self, 5, 0)
            enemy_block.rect.x = 150
            enemy_block.rect.y = 90 + 50 * i
            self.enemy_block_list.add(enemy_block)

        # Initialize boundaries of the level
        left_boundary = RectWall(0, 0, 50, SCREEN_HEIGHT, CYAN)
        right_boundary = RectWall(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT, CYAN)
        top_boundary = RectWall(0, 0, SCREEN_WIDTH, 50, CYAN)
        bottom_boundary = RectWall(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, CYAN)

        horizontal_wall = RectWall(left_boundary.rect.width, top_boundary.rect.height + 30, 100, 25, CYAN)

        self.goal = Goal(SCREEN_WIDTH / 2 - 10, SCREEN_HEIGHT / 2 - 10, 20, 20)

        self.wall_list.add(self.goal, horizontal_wall, left_boundary, right_boundary, top_boundary, bottom_boundary)

        self.player = Player(self, left_boundary.rect.width + 10, top_boundary.rect.height + 10, 10, 10)
        self.all_sprites_list.add(self.enemy_block_list, self.wall_list, self.player)

class GameOverScreen(Level):
    """ Represents the game over screen (a blank Level) """
    def __init__(self):
        super(GameOverScreen, self).__init__()

        left_boundary = RectWall(0, 0, 50, SCREEN_HEIGHT, CYAN)
        right_boundary = RectWall(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT, CYAN)
        top_boundary = RectWall(0, 0, SCREEN_WIDTH, 50, CYAN)
        bottom_boundary = RectWall(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, CYAN)

        self.wall_list.add(left_boundary, right_boundary, top_boundary, bottom_boundary)
        self.all_sprites_list.add(self.wall_list)

    def draw(self, surface):
        """
        Draws the boundaries of the GameOverScreen.
        Does not display a deaths counter or the level counter.
        """
        self.all_sprites_list.draw(surface)

class RectWall(pygame.sprite.Sprite):
    """ Represents a rectangular wall in a Level """
    def __init__(self, left, top, width, height, colour):
        """
        Constructs a rectangular wall.
        Parameters:
        - left: the x coordinate of the top left corner of the wall
        - top: the y coordinate of the top left corner of the wall
        - width: the width of the wall
        - height: the height of the wall
        - colour: the colour of the wall
        """
        super(RectWall, self).__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(colour)

        self.rect = self.image.get_rect()
        self.rect.x = left
        self.rect.y = top

    def update(self):
        """
        Updates the RectWall (override this if you want the
        wall to move)
        """
        pass

class Goal(RectWall):
    """
    Represents the green rectangular area that the player must reach in
    order to pass the level
    """
    def __init__(self, left, top, width, height):
        """
        Constructs a Goal.
        Parameters:
        - left: the x coordinate of the top left corner of the Goal
        - top: the y coordinate of the top left corner of the Goal
        - width: the width of the Goal
        - height: the height of the Goal
        """
        super(Goal, self).__init__(left, top, width, height, LIME_GREEN)

def main():
    pygame.init()

    # Set screen properties
    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("World's Hardest Game Spin-off")

    done = False

    clock = pygame.time.Clock()

    # List of all of the levels in the game
    levels_list = [Level_01(), Level_02(), Level_03(), Level_04()]

    # The index of levels_list that points to the current level.
    current_level_index = 0

    current_level = levels_list[0]

    # The font that is used to show the congratulatory message at the end of the level
    congratulations_font = pygame.font.SysFont("Arial", 48, True)

    # Represents whether the congratulations message is being shown or not.
    congratulations_text_showing = False

    # Number of ticks that the congratulations message has been shown for.
    congratulations_text_ticks = 0

    # Messages that show up on the end-game screen when the player beats all of the levels.
    game_over_messages = ["Congratulations!", "You beat all the levels!", "Thanks for playing!"]

    # Represents whether the arrow keys are pressed down or not.
    # From left to right, the boolean values correspond to the
    # state of the UP, DOWN, LEFT, and RIGHT keys.
    # The idea of storing the states of keys in a list was borrowed from a post
    # on Game Development Stack Exchange by kevintodisco, published on 2012 November 11.
    # https://gamedev.stackexchange.com/a/43556
    key_pressed = [False, False, False, False]

    # -------- Main Program Loop -----------
    while not done:
        # --- Event Handler Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if current_level_index < len(levels_list):
                if event.type == pygame.KEYDOWN: # Player movement is controlled with arrow keys
                    if event.key == pygame.K_UP:
                        key_pressed[0] = True
                    if event.key == pygame.K_DOWN:
                        key_pressed[1] = True
                    if event.key == pygame.K_LEFT:
                        key_pressed[2] = True
                    if event.key == pygame.K_RIGHT:
                        key_pressed[3] = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        key_pressed[0] = False
                    if event.key == pygame.K_DOWN:
                        key_pressed[1] = False
                    if event.key == pygame.K_LEFT:
                        key_pressed[2] = False
                    if event.key == pygame.K_RIGHT:
                        key_pressed[3] = False

        screen.fill(WHITE)

        current_level.draw(screen)

        if current_level_index >= len(levels_list): # The player beat all of the levels
            if congratulations_text_ticks == 0:
                # Add a message to game_over_messages telling the player how many times they died
                game_over_messages.append("Total number of deaths: " + str(current_level.player.deaths))

                # Initialize game over screen
                current_level = GameOverScreen()

            congratulations_text_ticks += 1

            if congratulations_text_ticks > 12 * FPS:
                done = True # Breaks out of the loop

            if 8 * FPS < congratulations_text_ticks <= 12 * FPS:
                congratulations_text = congratulations_font.render("World's Hardest Game Spin-off", False, GREEN)
                screen.blit(congratulations_text, [SCREEN_WIDTH / 2 - congratulations_text.get_width() / 2,
					SCREEN_HEIGHT / 2 - congratulations_text.get_height()])
                if 9.5 * FPS < congratulations_text_ticks <= 12 * FPS:
                    congratulations_text = congratulations_font.render("made by Eugene Chau", False, GREEN)
                    screen.blit(congratulations_text, [SCREEN_WIDTH / 2 - congratulations_text.get_width() / 2,
						SCREEN_HEIGHT / 2])
                pygame.display.flip()
                clock.tick(FPS)
                continue

            for i in range(4):
                if 2 * i * FPS < congratulations_text_ticks <= 2 * (i + 1) * FPS:
                    congratulations_text = congratulations_font.render(game_over_messages[i], False, GREEN)
                    screen.blit(congratulations_text, [SCREEN_WIDTH / 2 - congratulations_text.get_width() / 2,
						SCREEN_HEIGHT / 2 - congratulations_text.get_height() / 2])
                    pygame.display.flip()
                    clock.tick(FPS)

            continue

        # From this line onward, current_level_index < len(levels_list).

        # The player's x and y velocities must be reset to 0 every time, or else
        # the player would go faster and faster as the arrow keys continue
        # to be pressed.
        current_level.player.velocity_x = 0
        current_level.player.velocity_y = 0

        if key_pressed[0]:
            current_level.player.go_up()
        if key_pressed[1]:
            current_level.player.go_down()
        if key_pressed[2]:
            current_level.player.go_left()
        if key_pressed[3]:
            current_level.player.go_right()

        # Text on the top-right corner telling the player which level they
        # are on.
        level_font = pygame.font.SysFont("Arial", 20, True)
        level_text = level_font.render("Level " + str(current_level_index + 1), False, BLUE)
        screen.blit(level_text, [SCREEN_WIDTH - level_text.get_width() - 10, 10])

        # Checks if the player has reached the goal.
        if current_level.player.reached_goal:
            # Displays a message to the player saying they beat the level.
            congratulations_text = congratulations_font.render("Level " + str(current_level_index + 1) + " complete!", False, GREEN)
            screen.blit(congratulations_text, [SCREEN_WIDTH / 2 - congratulations_text.get_width() / 2,
				SCREEN_HEIGHT / 2 - congratulations_text.get_height() / 2])
            congratulations_text_showing = True
            congratulations_text_ticks += 1

            if congratulations_text_ticks > 2 * FPS: # Only show the congratulatory message for 1 second.
                congratulations_text_showing = False

            # Checks if the congratulatory message has stopped showing up
            if not congratulations_text_showing:
                congratulations_text_ticks = 0

                # At this point, it is safe to increment the current_level_index.
                current_level_index += 1

                if current_level_index < len(levels_list): # The player has not beaten all of the levels
                    # Changes the Level
                    # The number of deaths that the Player has carries over to the next Level.
                    current_deaths = current_level.player.deaths
                    current_level = levels_list[current_level_index]
                    current_level.player.deaths = current_deaths
        else: # Only update the Level if the Player hasn't reached the goal.
            current_level.update()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
