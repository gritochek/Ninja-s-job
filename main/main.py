import enum
import arcade
import math
import random



class FaceDirection(enum.Enum):
    FD = 0
    BK = 1
    RT = 2
    LT = 3


class Bullet(arcade.Sprite):

    def __init__(self, x, y, angle, speed=500):
        texture = arcade.load_texture("resources/bullet.png")
        super().__init__(texture)

        self.center_x = x
        self.center_y = y
        self.angle = angle
        self.speed = speed

        self.change_x = math.cos(math.radians(self.angle)) * self.speed
        self.change_y = math.sin(math.radians(self.angle)) * self.speed

    def update(self, delta_time: float = 1 / 60):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        if (self.center_x < -50 or self.center_x > SCREEN_WIDTH + 50 or
                self.center_y < -50 or self.center_y > SCREEN_HEIGHT + 50):
            self.remove_from_sprite_lists()


class Hero(arcade.Sprite):
    def __init__(self):
        base_path = "sprites"
        texture = arcade.load_texture("resources/fd.png")

        super().__init__(texture, scale=1.0)

        self.speed = 300
        self.health = 10
        self.max_health = 10
        self.shoot_cooldown = 0.3
        self.shoot_timer = 0
        self.bullet_damage = 25
        self.mouse_x = SCREEN_WIDTH // 2
        self.mouse_y = SCREEN_HEIGHT // 2

        # Загружаем остальные текстуры
        self.walk_textures = []
        self.walk_textures.append(texture)  # FD
        self.walk_textures.append(arcade.load_texture("resources/bk.png"))
        self.walk_textures.append(arcade.load_texture("resources/lt.png"))
        self.walk_textures.append(arcade.load_texture("resources/rt.png"))

        self.is_walking = False
        self.face_direction = FaceDirection.FD

    def update_animation(self, delta_time: float = 1 / 60):
        if self.face_direction == FaceDirection.FD:
            self.texture = self.walk_textures[1]
        elif self.face_direction == FaceDirection.BK:
            self.texture = self.walk_textures[0]
        elif self.face_direction == FaceDirection.RT:
            self.texture = self.walk_textures[2]
        elif self.face_direction == FaceDirection.LT:
            self.texture = self.walk_textures[3]

    def update(self, delta_time, keys_pressed):
        dx, dy = 0, 0

        if arcade.key.LEFT in keys_pressed or arcade.key.A in keys_pressed:
            dx -= self.speed * delta_time
            self.face_direction = FaceDirection.LT
        if arcade.key.RIGHT in keys_pressed or arcade.key.D in keys_pressed:
            dx += self.speed * delta_time
            self.face_direction = FaceDirection.RT
        if arcade.key.UP in keys_pressed or arcade.key.W in keys_pressed:
            dy += self.speed * delta_time
            self.face_direction = FaceDirection.FD
        if arcade.key.DOWN in keys_pressed or arcade.key.S in keys_pressed:
            dy -= self.speed * delta_time
            self.face_direction = FaceDirection.BK

        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        self.center_x += dx
        self.center_y += dy

        self.center_x = max(self.width / 2, min(SCREEN_WIDTH - self.width / 2, self.center_x))
        self.center_y = max(self.height / 2, min(SCREEN_HEIGHT - self.height / 2, self.center_y))

        self.is_walking = dx != 0 or dy != 0
        self.update_animation(delta_time)

        if self.shoot_timer > 0:
            self.shoot_timer -= delta_time

    def shoot(self, bullet_list):
        if self.shoot_timer <= 0:
            dx = self.mouse_x - self.center_x
            dy = self.mouse_y - self.center_y
            angle = math.degrees(math.atan2(dy, dx))

            bullet = Bullet(self.center_x, self.center_y, angle)
            bullet_list.append(bullet)
            self.shoot_timer = self.shoot_cooldown
            return True
        return False

    def update_mouse_position(self, x, y):
        self.mouse_x = x
        self.mouse_y = y


class Villainmelee(arcade.Sprite):
    def __init__(self, level=1):
        base_path = "sprites"
        texture = arcade.load_texture("resources/fdmv.png")

        super().__init__(texture, scale=1.0)

        self.level = level
        self.speed = 100 + level * 10
        self.health = 1 + level // 2
        self.max_health = self.health
        self.change_x = 0
        self.change_y = 0
        self.damage = 10 + level * 2

        self.walk_textures = []
        self.walk_textures.append(texture)
        self.walk_textures.append(arcade.load_texture("resources/bkmv.png"))
        self.walk_textures.append(arcade.load_texture("resources/ltmv.png"))
        self.walk_textures.append(arcade.load_texture("resources/rtmv.png"))

        self.is_walking = False
        self.face_direction = FaceDirection.FD

    def update_animation(self, delta_time: float = 1 / 60):
        if self.face_direction == FaceDirection.FD:
            self.texture = self.walk_textures[1]
        elif self.face_direction == FaceDirection.BK:
            self.texture = self.walk_textures[0]
        elif self.face_direction == FaceDirection.RT:
            self.texture = self.walk_textures[2]
        elif self.face_direction == FaceDirection.LT:
            self.texture = self.walk_textures[3]

    def update(self, delta_time, player_x, player_y):
        dx = player_x - self.center_x
        dy = player_y - self.center_y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 30:
            if dist > 0:
                self.change_x = (dx / dist) * self.speed * delta_time
                self.change_y = (dy / dist) * self.speed * delta_time
            else:
                self.change_x = 0
                self.change_y = 0
        else:
            self.change_x = 0
            self.change_y = 0

        self.center_x += self.change_x
        self.center_y += self.change_y

        if abs(self.change_x) > abs(self.change_y):
            if self.change_x > 0:
                self.face_direction = FaceDirection.RT
            elif self.change_x < 0:
                self.face_direction = FaceDirection.LT
        else:
            if self.change_y > 0:
                self.face_direction = FaceDirection.FD
            elif self.change_y < 0:
                self.face_direction = FaceDirection.BK

        self.center_x = max(self.width / 2, min(SCREEN_WIDTH - self.width / 2, self.center_x))
        self.center_y = max(self.height / 2, min(SCREEN_HEIGHT - self.height / 2, self.center_y))

        self.is_walking = self.change_x != 0 or self.change_y != 0

        self.update_animation(delta_time)


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Ninja's Job"


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.player_list = None
        self.enemy_list = None
        self.wall_list = None
        self.bullet_list = None
        self.player = None
        self.keys_pressed = set()
        self.last_enemy_spawn_time = 0
        self.elapsed_time = 0
        self.score = 0
        self.game_state = "PLAYING"  # PLAYING, LEVEL_COMPLETE, GAME_OVER

        self.current_level = 1
        self.max_levels = 5
        self.enemies_on_current_level = 0
        self.enemies_defeated = 0

        self.level_config = {
            1: {"enemies": 3, "spawn_delay": 5.0, "name": "Уровень 1: Начало пути"},
            2: {"enemies": 5, "spawn_delay": 4.0, "name": "Уровень 2: Усиление врагов"},
            3: {"enemies": 8, "spawn_delay": 3.0, "name": "Уровень 3: Натиск"},
            4: {"enemies": 12, "spawn_delay": 2.5, "name": "Уровень 4: Осада"},
            5: {"enemies": 15, "spawn_delay": 2.0, "name": "Уровень 5: Финальная битва"}
        }

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        tile_map = arcade.load_tilemap("resources/map.tmx", scaling=1.0)
        self.wall_list = tile_map.sprite_lists["walls"]

        self.player = Hero()
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player_list.append(self.player)


        self.start_level(self.current_level)

        self.keys_pressed = set()

    def start_level(self, level):
        self.current_level = level
        self.enemies_on_current_level = self.level_config[level]["enemies"]
        self.enemies_defeated = 0
        self.enemy_spawn_delay = self.level_config[level]["spawn_delay"]
        self.last_enemy_spawn_time = 0
        self.elapsed_time = 0

        self.enemy_list.clear()
        self.bullet_list.clear()

        enemies_to_spawn = min(3, self.enemies_on_current_level)
        for _ in range(enemies_to_spawn):
            self.spawn_enemy()

        self.game_state = "PLAYING"

    def spawn_enemy(self):
        enemy = Villainmelee(level=self.current_level)

        side = random.randint(0, 3)
        if side == 0:
            enemy.center_x = random.randint(50, SCREEN_WIDTH - 50)
            enemy.center_y = SCREEN_HEIGHT + 20
        elif side == 1:
            enemy.center_x = SCREEN_WIDTH + 20
            enemy.center_y = random.randint(50, SCREEN_HEIGHT - 50)
        elif side == 2:
            enemy.center_x = random.randint(50, SCREEN_WIDTH - 50)
            enemy.center_y = -20
        else:
            enemy.center_x = -20
            enemy.center_y = random.randint(50, SCREEN_HEIGHT - 50)

        self.enemy_list.append(enemy)

    def check_collisions(self):
        for enemy in self.enemy_list:
            if arcade.check_for_collision(self.player, enemy):
                self.player.health -= enemy.damage * 0.1

                enemy.health -= 5

                if enemy.health <= 0:
                    enemy.remove_from_sprite_lists()
                    self.enemies_defeated += 1
                    self.score += 10 * self.current_level

        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            for enemy in hit_list:
                enemy.health -= self.player.bullet_damage
                if enemy.health <= 0:
                    enemy.remove_from_sprite_lists()
                    self.enemies_defeated += 1
                    self.score += 10 * self.current_level
                bullet.remove_from_sprite_lists()
                break

        if self.enemies_defeated >= self.enemies_on_current_level:
            if self.current_level < self.max_levels:
                self.game_state = "LEVEL_COMPLETE"
            else:
                self.game_state = "GAME_OVER"

        if self.player.health <= 0:
            self.game_state = "GAME_OVER"

    def on_draw(self):
        self.clear()

        self.wall_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()

        arcade.draw_text(f"Уровень: {self.current_level}/{self.max_levels}",
                         10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16)
        arcade.draw_text(f"Очки: {self.score}",
                         10, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)
        arcade.draw_text(f"Здоровье: {int(self.player.health)}/{self.player.max_health}",
                         10, SCREEN_HEIGHT - 90, arcade.color.WHITE, 16)
        arcade.draw_text(f"Врагов: {self.enemies_defeated}/{self.enemies_on_current_level}",
                         10, SCREEN_HEIGHT - 120, arcade.color.WHITE, 16)
        arcade.draw_text("Управление: WASD - движение, ЛКМ - стрельба",
                         10, 20, arcade.color.LIGHT_GRAY, 14)

        if self.game_state == "LEVEL_COMPLETE":
            arcade.draw_text("УРОВЕНЬ ПРОЙДЕН!",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                             arcade.color.WHITE, 30, anchor_x="center")
            arcade.draw_text(f"Очки: {self.score}",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.YELLOW, 24, anchor_x="center")
            arcade.draw_text("Нажмите ПРОБЕЛ для следующего уровня",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                             arcade.color.WHITE, 18, anchor_x="center")

        elif self.game_state == "GAME_OVER":
            if self.current_level >= self.max_levels:
                arcade.draw_rectangle_filled(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                    400, 200,
                    arcade.color.DARK_GREEN
                )
                arcade.draw_text("ПОБЕДА!",
                                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                                 arcade.color.GOLD, 40, anchor_x="center")
                arcade.draw_text(f"Финальный счет: {self.score}",
                                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                 arcade.color.WHITE, 24, anchor_x="center")
                arcade.draw_text("Нажмите R для перезапуска",
                                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                                 arcade.color.WHITE, 18, anchor_x="center")
            else:
                arcade.draw_text("ИГРА ОКОНЧЕНА",
                                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                                 arcade.color.WHITE, 30, anchor_x="center")
                arcade.draw_text(f"Достигнут уровень: {self.current_level}",
                                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                 arcade.color.YELLOW, 24, anchor_x="center")
                arcade.draw_text("Нажмите R для перезапуска",
                                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                                 arcade.color.WHITE, 18, anchor_x="center")

    def on_update(self, delta_time):
        if self.game_state != "PLAYING":
            return

        self.elapsed_time += delta_time

        self.player.update(delta_time, self.keys_pressed)

        for enemy in self.enemy_list:
            enemy.update(delta_time, self.player.center_x, self.player.center_y)

        self.bullet_list.update(delta_time)

        current_enemies = len(self.enemy_list)
        if (current_enemies < self.enemies_on_current_level and
                self.elapsed_time - self.last_enemy_spawn_time > self.enemy_spawn_delay):
            self.spawn_enemy()
            self.last_enemy_spawn_time = self.elapsed_time

        self.check_collisions()

    def on_mouse_motion(self, x, y, dx, dy):
        """Отслеживание движения мыши"""
        if self.player:
            self.player.update_mouse_position(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.game_state == "PLAYING":
            if self.player:
                self.player.update_mouse_position(x, y)
                self.player.shoot(self.bullet_list)

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

        if key == arcade.key.SPACE:
            if self.game_state == "LEVEL_COMPLETE" and self.current_level < self.max_levels:
                self.current_level += 1
                self.start_level(self.current_level)

        elif key == arcade.key.R:
            self.setup()
            self.score = 0
            self.current_level = 1
            self.game_state = "PLAYING"

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()