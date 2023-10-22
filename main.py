import pygame
import random
from pathfinding.core.grid import Grid
from pathfinding.finder.bi_a_star import BiAStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
import time

WIDTH, HEIGHT = 720, 720
GRID_SCALE = 4
CELL_SIZE_X, CELL_SIZE_Y = WIDTH // GRID_SCALE, HEIGHT // GRID_SCALE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
FPS = 60

pygame.init()
GRID = []
win = pygame.display.set_mode((WIDTH, HEIGHT))
game_map = [[1] * CELL_SIZE_X for _ in range(CELL_SIZE_Y + 1)]
grid = Grid(matrix=game_map)
font = pygame.font.SysFont('arial', 16)
damage_texts = []

def draw_damage_text(entity, damage_value):
    damage_text = {
        'text': font.render(f"{damage_value}", True, WHITE),
        'pos': (entity.x, entity.y - 30),
        'time': pygame.time.get_ticks()
    }
    damage_texts.append(damage_text)

# Todo: FInd a way of implementing on the mob chasing method
def pathfinder(entity, target):
    start = grid.node(entity.x // GRID_SCALE, entity.y // GRID_SCALE)
    end = grid.node(target.x // GRID_SCALE, target.y // GRID_SCALE)
    finder = BiAStarFinder(diagonal_movement=DiagonalMovement.always)
    start_time = time.time()
    path, runs = finder.find_path(start, end, grid)
    end_time = time.time()
    execution_time = end_time - start_time
    # print('operations:', runs, 'path length:', len(path), 'time:', execution_time)
    grid.cleanup()


class Player:
    def __init__(self, x, y):
        self.name = "Player"
        self.x = x
        self.y = y
        self.size = 10
        
        # Stats
        self.hp = 25
        self.max_hp = 25
        self.speed = 2
        self.attack = 5
        self.defense = 1
        
        # Progression
        self.level = 1
        self.xp = 0
        self.max_xp = 100
        
        # Economy
        self.gold = 0
        self.potions = 2
        
        # Technical
        self.hit_box = pygame.Rect(
            self.x, self.y, self.size + 40, self.size + 40)
        self.combat_delay = 1000
        self.next_strike_time = 0
        self.collided = False
        self.potion_used = False
        self.in_combat = False

    def draw(self):
        pygame.draw.circle(win, WHITE, (self.x, self.y), self.size)
        self.hit_box = pygame.Rect(
            self.x, self.y, self.size * 2, self.size * 2)
        self.draw_health_bar()

    def draw_health_bar(self):
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y - 10, self.size * 2, 5))  # max health
        pygame.draw.rect(win, (0, 255, 0), (self.x, self.y - 10, self.size * 2 * (self.hp / self.max_hp), 5))  # current health

    def handle_input(self, mobs):
        keys = pygame.key.get_pressed()
        for mob in mobs:
            if keys[pygame.K_LEFT] and self.x - self.speed >= 0 and not self.hit_box.move(-self.speed, 0).colliderect(mob.hit_box):
                self.x -= self.speed
            if keys[pygame.K_RIGHT] and self.x + self.speed + self.size <= WIDTH and not self.hit_box.move(self.speed, 0).colliderect(mob.hit_box):
                self.x += self.speed
            if keys[pygame.K_UP] and self.y - self.speed >= 0 and not self.hit_box.move(0, -self.speed).colliderect(mob.hit_box):
                self.y -= self.speed
            if keys[pygame.K_DOWN] and self.y + self.speed + self.size < HEIGHT and not self.hit_box.move(0, self.speed).colliderect(mob.hit_box):
                self.y += self.speed
            if keys[pygame.K_SPACE]:
                self.draw_character_chart()

    def combat(self, mob):
        current_time = pygame.time.get_ticks()

        if current_time > self.next_strike_time:
            player_damage = random.randint(1, self.attack) - mob.defense / 2
            mob.hp -= player_damage
            
            draw_damage_text(self, player_damage)

            if mob.hp < 0:
                self.win_combat(mob)
                return "WON"

            mob_damage = random.randint(1, mob.attack) - self.defense / 2
            self.hp -= mob_damage

            self.next_strike_time = current_time + self.combat_delay

            if self.hp <= 0:
                return "LOST"
            if mob.hp > 0:
                return "DRAW"

    def win_combat(self, mob):
        print(f"You have gained {mob.xp_loot} xp and" + 
              f"{mob.gold_loot} gold pieces.\n")
        self.xp += mob.xp_loot
        if self.xp >  self.max_xp:
            self.level_up()
        self.gold += mob.gold_loot
    
    def level_up(self):
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.attack += 1
        self.defense += 1
        self.xp = 0
        if self.level < 25:
            self.max_xp *= 1.85
        if self.level > 25 and self.level < 50:
            self.max_xp *= 2.5
            
    def draw_character_chart(self):
        chart_text1 = f"Name: {self.name}"
        chart_text2 = f"Level: {self.level}"
        chart_text3 = f"Attack: {self.attack}"
        chart_text4 = f"Defense: {self.defense}"
        
        chart1 = font.render(chart_text1, True, WHITE)
        chart2 = font.render(chart_text2, True, WHITE)
        chart3 = font.render(chart_text3, True, WHITE)
        chart4 = font.render(chart_text4, True, WHITE)
        
        win.blit(chart1, (WIDTH // 2, 0))
        win.blit(chart2, (WIDTH // 2, 20))
        win.blit(chart3, (WIDTH // 2, 40))
        win.blit(chart4, (WIDTH // 2, 60))   
    
    def use_potion(self):
        if self.potions:
            if self.hp + 10 > self.max_hp:
                self.hp = self.max_hp
            else:
                self.hp += 10

            self.potions -= 1


class Mob:
    ID = 0

    def __init__(self, x, y):
        self.id = Mob.ID
        Mob.ID += 1
        self.name = f"Mob {self.id}"
        self.x = x
        self.y = y

        self.hp = 10
        self.max_hp = 10
        self.attack = 2
        self.defense = 1

        self.xp_loot = random.randint(15, 25)
        self.gold_loot = random.randint(25, 50)

        self.speed = 1
        self.size = 10
        self.hit_box_size = self.size + 40
        self.detection_box_size = self.hit_box_size + 75

        
        # Technical
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.next_move_time = pygame.time.get_ticks() + random.randint(500, 2000)
        self.hit_box = pygame.Rect(
            self.x, self.y, self.hit_box_size, self.hit_box_size)
        self.detection_box = pygame.Rect(
            self.x, self.y, self.detection_box_size, self.detection_box_size)
        self.in_combat = False
        self.chasing = False
        self.chase_end_time = 0
        self.chase_duration = 5000
        self.move_timer = pygame.time.get_ticks() + 5000
        self.collided = False

    def draw(self):
        pygame.draw.circle(win, RED, (self.x, self.y), self.size)
        self.hit_box = pygame.Rect(
            self.x, self.y, self.hit_box_size, self.hit_box_size)
        self.detection_box = pygame.Rect(
            self.x, self.y, self.detection_box_size, self.detection_box_size)

    def move(self):
        if pygame.time.get_ticks() > self.move_timer:
            self.change_direction()
            self.move_timer = pygame.time.get_ticks() + 5000
        if self.direction == 'up':
            if self.y - self.speed - self.size >= 0 and pygame.time.get_ticks() < self.move_timer:
                self.y -= self.speed
            else:
                self.change_direction()

        elif self.direction == 'down':
            if self.y + self.speed + self.size <= HEIGHT and pygame.time.get_ticks() < self.move_timer:
                self.y += self.speed
            else:
                self.change_direction()

        elif self.direction == 'left' and pygame.time.get_ticks() > self.move_timer:
            if self.x - self.speed - self.size >= 0:
                self.x -= self.speed
            else:
                self.change_direction()

        elif self.direction == 'right':
            if self.x + self.speed + self.size <= WIDTH and pygame.time.get_ticks() < self.move_timer:
                self.x += self.speed
            else:
                self.change_direction()

    def change_direction(self):
        directions = ['up', 'down', 'left', 'right']
        directions.remove(self.direction)  # prevent u-turns
        self.direction = random.choice(directions)

    def update(self, player):
        self.halt_if_colliding(player)
        if self.chasing:
            if pygame.time.get_ticks() > self.chase_end_time:
                self.chasing = False
            else:
                self.chase(player)
        elif not self.in_combat:
            self.move()

    def halt_if_colliding(self, player):
        if player.hit_box.colliderect(self.hit_box):
            player.collided = True
            self.in_combat = True
        if self.detection_box.colliderect(player.hit_box):
            self.chasing = True
            self.chase_end_time = pygame.time.get_ticks() + self.chase_duration
        else:
            self.in_combat = False

    def chase(self, player):
        if player.x < self.x and not self.in_combat:
            self.x -= self.speed
        elif player.x > self.x and not self.in_combat:
            self.x += self.speed
        if player.y < self.y and not self.in_combat:
            self.y -= self.speed
        elif player.y > self.y and not self.in_combat:
            self.y += self.speed


def game_run():
    running = True
    global POINTS
    clock = pygame.time.Clock()
    win.fill(BLACK)
    player = Player(WIDTH // 2, HEIGHT // 2)
    mobs = []

    for _ in range(1):
        spawn_mob(mobs)

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                player.use_potion()
                player.potion_used = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_e:
                    player.potion_used = False
        win.fill(BLACK)
        player.handle_input(mobs)
        for text in damage_texts[:]:
            win.blit(text['text'], text['pos'])
            if pygame.time.get_ticks() - text['time'] > 500:
                damage_texts.remove(text)
        for mob in mobs:
            mob.update(player)
            if mob.in_combat:
                running = combat_loop(mob, mobs, player, running)

            mob.draw()

        player_hp = font.render(
            f"Player HP: {player.hp} / {player.max_hp}", True, WHITE)
        player_xp = font.render(
            f"Player XP: {player.xp} / {player.max_xp}", True, WHITE)
        player_gold = font.render(f"Player Gold: {player.gold}", True, WHITE)
        player_potion = font.render(f"Potions: {player.potions}", True, WHITE)
        win.blit(player_hp, (10, 10))
        win.blit(player_xp, (10, 30))
        win.blit(player_gold, (10, 50))
        win.blit(player_potion, (10, 70))
        player.draw()

        pygame.display.update()

    pygame.quit()


def combat_loop(mob, mobs, player, running):
    combat_status = player.combat(mob)
    if combat_status == "WON":
        mobs.remove(mob)
        spawn_mob(mobs)
    elif combat_status == "LOST":
        print("LOST!")
        running = False
    return running


def spawn_mob(mobs):
    pos_x = random.randint(0, 500)
    pos_y = random.randint(0, 500)
    mobs.append(Mob(pos_x, pos_y))


if __name__ == "__main__":
    game_run()
