#!/usr/bin/python

import secrets
from lib.game import *

CONTROL_LEFT  = [Button.L_STICK_LEFT, Button.HAT_LEFT, Button.KEY_LEFT]
CONTROL_RIGHT = [Button.L_STICK_RIGHT, Button.HAT_RIGHT, Button.KEY_RIGHT]
CONTROL_SHOOT = [Button.GREEN, Button.RED, Button.YELLOW, Button.BLUE, Button.KEY_L_SHIFT]

class Shooter:
    _DOWN_MOVE_FREQ = 50
    _ENEMY_OUTSIDE_WALL = 20

    def __init__(self, game: Game):
        self._game = game
        screen = game.screen     
        screen.clear()

        self.shoot_sound = game.sound.get(SoundSample.SHOOT)
        self.rocket_sound = game.sound.get(SoundSample.ROCKET)
        self.explosion_sound = game.sound.get(SoundSample.EXPLOSION)
        self.big_explosion_sound = game.sound.get(SoundSample.BIG_EXPLOSION)
        self.powerup_sound = game.sound.get(SoundSample.POWERUP)

        self._move_num = 1
        self._delay = 1 / 20
        self._score = 0
        self._random_direction = MoveDirection.UP

        self.create_player(game, screen)
        self.create_enemies(game, screen)
        screen.update()

    def step_delay(self):
        time.sleep(self._delay)

    def create_player(self, game: Game, screen: Screen):
        player = game.sprites.get(SpriteID.SHIP)
        self._player = player
        player.transform(1, skip_draw = True)
        player.set_position(
            int(screen.pixels.get_num_columns() / 2), 
            screen.pixels.get_num_rows() - player.get_height())

        self._player_shooting = False
        self._player_bullet = game.sprites.get(SpriteID.BULLET)

    def create_enemies(self, game: Game, screen: Screen):
        self._enemies: List[Sprite] = []
        self._enemy_groups: List[List[Sprite]] = []
        self._enemy_directions: List[MoveDirection] = []
        self._enemy_bullet = game.sprites.get(SpriteID.ENEMY_BULLET)
        self._enemy_bullet.set_brightness(2)
        self._enemy_shooting = False

        row = 0
        enemy_direction = MoveDirection.RIGHT

        for spriteObject in [
                #SpriteID.ENEMY_SQUARE,
                SpriteID.ENEMY_SHIP,
                SpriteID.ENEMY_FLIPER, 
                SpriteID.ENEMY_SPINNER
            ]:

            column = 0
            enemy_group: List[Sprite] = []

            while True:
                enemy = game.sprites.get(spriteObject)
                enemy.set_position(column, row)
                self._enemies.append(enemy)
                enemy_group.append(enemy)

                width = enemy.get_width()
                height = enemy.get_height()

                column += width + 1
                if column + width > screen.last_column:
                    break
            
            self._enemy_directions.append(enemy_direction)
            if enemy_direction == MoveDirection.RIGHT:
                enemy_direction = MoveDirection.LEFT
            else:
                enemy_direction = MoveDirection.RIGHT

            self._enemy_groups.append(enemy_group)
            row += height

    def move(self):
        game = self._game
        screen = game.screen
        player_bullet = self._player_bullet
        enemy_bullet = self._enemy_bullet

        self.move_bullets(screen, player_bullet, enemy_bullet)
        self.move_player(game.sound, self._player, player_bullet)
        self.move_enemy(enemy_bullet)
        screen.update()

        self._move_num += 1

    def move_player(self, sound: Sound, player: Sprite, player_bullet: Sprite):
        buttons = self._game.gamepad.get_all()
        for button in buttons:
            if button in CONTROL_LEFT:
                player.move(MoveDirection.LEFT)  
            elif button in CONTROL_RIGHT:
                player.move(MoveDirection.RIGHT)
            elif button in CONTROL_SHOOT and not self._player_shooting:
                if len(self._enemies) <= 5:
                    self.rocket_sound.play()
                    self._player_bullet = self._game.sprites.get(SpriteID.ROCKET)
                    player_bullet = self._player_bullet
                    player_bullet.set_brightness(2)
                else:
                    self.shoot_sound.play()

                column, row = player.get_middle_position()
                column = column - int(player_bullet.get_width() / 2)
                player_bullet.set_position(column, row - player_bullet.get_height())
                player.transform(0)
                self._player_shooting = True

    def move_bullets(self, screen: Screen, player_bullet: Sprite, enemy_bullet: Sprite):
        if self._player_shooting:
            if player_bullet.get_row() < 0:
                player_bullet.erase()
                self._player.transform(1)
                self._player_shooting = False
            if self._player_shooting:
                player_bullet.move(MoveDirection.UP, outside = 1, pulsate = True)
        
        if self._enemy_shooting:
            if enemy_bullet.get_row() > screen.last_row:
                enemy_bullet.erase()
                self._enemy_shooting = False
            if self._enemy_shooting:
                enemy_bullet.move(MoveDirection.DOWN, outside = 1, pulsate = True)

    def move_enemy(self, enemy_bullet: Sprite):
        outside_wall = self._ENEMY_OUTSIDE_WALL
        enemy_directions = self._enemy_directions
        enemies = self._enemies

        if len(enemies) <= 5:
            for enemy in enemies:
                if (self._move_num % 3) == 0:
                    self._random_direction = MoveDirection(secrets.randbelow(len(MoveDirection)))
                enemy.set_brightness(2)
                enemy.move(self._random_direction, pulsate = True)
        else:
            for i, enemy_group in enumerate(self._enemy_groups):
                if enemy_directions[i] == MoveDirection.RIGHT:
                    for enemy in reversed(enemy_group):
                        if not enemy.move(MoveDirection.RIGHT, outside_wall, pulsate = True):
                            enemy_directions[i] = MoveDirection.LEFT
                            break
                elif enemy_directions[i] == MoveDirection.LEFT:
                    for enemy in enemy_group:
                        if not enemy.move(MoveDirection.LEFT, outside_wall, pulsate = True):
                            enemy_directions[i] = MoveDirection.RIGHT
                            break
            if (self._move_num % self._DOWN_MOVE_FREQ) == 0:
                for enemy in self._enemies:
                    enemy.move(MoveDirection.DOWN, pulsate = True)

        if not self._enemy_shooting:
            visible_enemies: List[Sprite] = []
            for enemy in enemies:
                if enemy.on_screen():
                    visible_enemies.append(enemy)

            if len(visible_enemies) != 0:
                enemy = visible_enemies[secrets.randbelow(len(visible_enemies))]
                column, row = enemy.get_middle_position()
                enemy_bullet.set_position(column, row + enemy.get_height())
                self._enemy_shooting = True

    def detect(self) -> bool:
        game = self._game
        screen = game.screen
        sound = game.sound
        player = self._player
        enemies = self._enemies

        if len(enemies) == 0:
            self._game.show_win_lose(True, self._score)
            return True

        self.detect_enemy_kills(screen, sound, player, enemies, self._player_bullet)
        killed = self.detect_player_kill(screen, sound, player, enemies, self._enemy_bullet)
        return killed

    def detect_player_kill(self, screen: Screen, sound: Sound, player: Sprite, 
        enemies: List[Sprite], enemy_bullet: Sprite) -> bool:

        colisions = player.get_collisions(enemies)

        if (len(colisions) > 0) or player.is_colliding(enemy_bullet):
            self.big_explosion_sound.play()
            player.draw(Color.RED, brightness = -1)
            screen.update()
            time.sleep(1 / 100)

            player.erase()
            screen.update()
            time.sleep(1)

            self._game.show_win_lose(False, self._score)
            return True
        
        return False

    def detect_enemy_kills(self, screen: Screen, sound: Sound, player: Sprite,
        enemies: List[Sprite], player_bullet: Sprite):

        colisions = player_bullet.get_collisions(enemies)
        for enemy in colisions:
            if len(enemies) == 6:
                self.powerup_sound.play()
            else:
                self.explosion_sound.play()
                    
            enemy.draw(Color.RED, brightness = -1)
            screen.update()
            time.sleep(1 / 100)

            enemy.erase()
            enemies.remove(enemy)
            for enemy_group in self._enemy_groups:
                for check_enemy in enemy_group:
                    if enemy == check_enemy:
                        enemy_group.remove(check_enemy)

            player_bullet.erase()
            player.transform(1)
            screen.update()
            self._player_shooting = False
            self._score += 1

def start(game: Game):
    shooter = Shooter(game)

    while True:
        shooter.move()
        if shooter.detect():
            break
        shooter.step_delay()

if __name__ == '__main__':
    GameLauncher(
        GameFactory("data/horizontal.csv", "data/font.csv", "shooter.cfg", [], "data/sprites.csv"), 
        start)
