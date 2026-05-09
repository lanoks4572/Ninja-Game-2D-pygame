from pygame import *
from Classes import *

import random

win_width = 1920
win_height = 700
FPS = 60

window = display.set_mode((win_width, win_height), flags= NOFRAME)
display.set_caption("Ninja Fight")
icon = image.load("icon.png")
display.set_icon(icon)

sloi_1 = image.load("sloi/1-sloi.png").convert()
sloi_2 = image.load("sloi/2-sloi.png").convert_alpha()
sloi_3 = image.load("sloi/3-sloi.png").convert_alpha()

clock = time.Clock()

class Block(sprite.Sprite):
    def __init__(self, block_image, block_x, block_y, size_x, size_y):
        super().__init__()        
        if isinstance(block_image, str):
            original_image = image.load(block_image).convert_alpha()
        else:
            original_image = block_image
        self.image = transform.scale(original_image, (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.x = block_x
        self.rect.y = block_y
    def reset(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

platforms = sprite.Group()
def generate_floor():
    platforms.empty()

    base_y = 630
    x = 0
    bump_length = 0
    block_size = 70
    wall_height = 15
    map_width = win_width * 10 + 70
    # Левая стена
    for j in range(1, wall_height):
        platforms.add(Block("null_block.png", 0, base_y - (j * block_size), block_size, block_size))

    # Пол
    while x < map_width:
        if bump_length > 0:
            platforms.add(
                Block("block.png", x, base_y - block_size, block_size, block_size),
                Block("null_block.png", x, base_y, block_size, block_size)
            )
            bump_length -= 1
        else:
            if random.randint(1, 4) == 1:
                bump_length = random.randint(2, 4)
                continue
            platforms.add(
                Block("block.png", x, base_y, block_size, block_size)
            )
        x += block_size

    # Правая стена
    last_x = x - block_size 
    for j in range(1, wall_height):
        platforms.add(Block("null_block.png", last_x, base_y - (j * block_size), block_size, block_size))


def draw_bg(image, speed, camera_x):

    width = image.get_width()

    dx = (camera_x * speed) % width
    
    window.blit(image, (dx - width, 0))
    window.blit(image, (dx, 0))
    window.blit(image, (dx + width, 0))

generate_floor()

enemies = sprite.Group()
total_enemies_limit = 10  # Макс врагов
enemies_spawned_count = 0
max_on_screen = 3 # Лимит врагов в реальном времени
def spawn_new_enemy():
    global enemies_spawned_count
    if enemies_spawned_count < total_enemies_limit:

        rx = random.randint(800, 18500)
        ry = 500
        new_mob = Enemy(rx, ry)
        enemies.add(new_mob)
        enemies_spawned_count += 1
        print(f"Заспавнен враг №{enemies_spawned_count} на X: {rx}")

for i in range(max_on_screen):
    spawn_new_enemy()

ninja = Player(9600, 400)
camera_x = 0


game = True
while game:

    alive_mobs = [m for m in enemies if m.state != "dead"]
    if len(alive_mobs) < max_on_screen and enemies_spawned_count < total_enemies_limit:
        spawn_new_enemy()



    for e in event.get():
        if e.type == QUIT: 
            game = False
        if e.type == KEYDOWN:
            if ninja.state != "dead":
                if e.key == K_SPACE: 
                    ninja.jump()
                if e.key == K_f: 
                    ninja.state = "attack"
                    ninja.frame_index = 0


    ninja.update(platforms)
    
    # Бой и cмерть
    for mob in enemies:
        mob.update(platforms, ninja)
        
        if mob.state == "dead": 
            continue


        sword_hitbox = ninja.get_attack_rect()
        
        if ninja.state == "attack" and sword_hitbox.colliderect(mob.hitbox):
            if ninja.frame_index >= 2: 
                mob.state = "dead"
                print(f"Враг зарублен! Кадр удара: {ninja.frame_index}")
                continue

        # 2.
        if ninja.hitbox.colliderect(mob.hitbox):
            if ninja.state != "dead":
                ninja.state = "dead"
                ninja.frame_index = 0
                ninja.vel_x = 0
                
                mob.state = "attack"
                mob.frame_index = 0
                print("Ниндзя погиб от столкновения!")

    #Камера
    target_x = -(ninja.hitbox.centerx - win_width // 2)
    camera_x += (target_x - camera_x) * 0.05
    int_cam = int(camera_x)

    draw_bg(sloi_1, 0.2, int_cam)
    draw_bg(sloi_2, 0.5, int_cam)
    draw_bg(sloi_3, 0.8, int_cam)


    for p in platforms:
        if -150 < p.rect.x + int_cam < win_width + 150:
            window.blit(p.image, (p.rect.x + int_cam, p.rect.y))

    for mob in enemies:
        window.blit(mob.image, (mob.rect.x + int_cam, mob.rect.y))

    window.blit(ninja.image, (ninja.rect.x + int_cam, ninja.rect.y))

    otladka = True
    if otladka == True:
    # Хитбокс игрока (Зеленый)
        draw.rect(window, (0, 255, 0), (ninja.hitbox.x + int_cam, ninja.hitbox.y, ninja.hitbox.width, ninja.hitbox.height), 2)

        # Удар мечом (Синий)
        if ninja.state == "attack" and 3 <= ninja.frame_index <= 7:
            sword_ray = ninja.get_attack_rect()
            draw.rect(window, (0, 0, 255), (sword_ray.x + int_cam, sword_ray.y, sword_ray.width, sword_ray.height), 2)

        for mob in enemies:
            if mob.state != "dead":
                # Хитбокс врага (Красный)
                draw.rect(window, (255, 0, 0), (mob.hitbox.x + int_cam, mob.hitbox.y, mob.hitbox.width, mob.hitbox.height), 2)

                # Луч зрения (Желтый)
                view_dist = 500
                if mob.direction == "right":
                    v_ray = Rect(mob.hitbox.right, mob.hitbox.y, view_dist, mob.hitbox.height)
                else:
                    v_ray = Rect(mob.hitbox.left - view_dist, mob.hitbox.y, view_dist, mob.hitbox.height)
                draw.rect(window, (255, 255, 0), (v_ray.x + int_cam, v_ray.y, v_ray.width, v_ray.height), 1)

    display.update()
    clock.tick(FPS)