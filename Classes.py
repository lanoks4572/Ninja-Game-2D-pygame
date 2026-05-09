from pygame import *

class Player(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 100
        self.height = 140
        
        #Настройка хит бокса
        self.hitbox_margin_x = 30
        self.hitbox_margin_y = 10 

#Анимации

        path = "Ninja_Monk/"
        animation_config = {
            "idle": ("Idle.png", 7),
            "walk": ("Run.png", 8),
            "jump": ("Jump.png", 9),
            "dead": ("Dead.png", 5)
        }
        
        self.animations_right = {}
        for name, (file, count) in animation_config.items():
            self.animations_right[name] = self.load_animation_sheet(path + file, count)
            
        attack_part1 = self.load_animation_sheet(path + "Attack_1.png", 5)
        attack_part2 = self.load_animation_sheet(path + "Attack_2.png", 5)
        self.animations_right["attack"] = attack_part1 + attack_part2
        
        self.animations_left = {}
        for name, frames in self.animations_right.items():
            self.animations_left[name] = [transform.flip(img, True, False) for img in frames]

        self.state = "idle"
        self.direction = "right"
        self.frame_index = 0
        self.image = self.animations_right[self.state][self.frame_index]
        
        self.rect = self.image.get_rect(topleft=(x, y))

        self.hitbox = Rect(x + self.hitbox_margin_x, y + self.hitbox_margin_y, 
                           self.width - self.hitbox_margin_x * 2, self.height - self.hitbox_margin_y * 2)
        
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 7
        self.gravity = 0.8
        self.jump_power = -16
        self.on_ground = False
        self.update_time = time.get_ticks()
        self.animation_speed = 100

    def load_animation_sheet(self, filename, frames_count):
        try:
            sheet = image.load(filename).convert_alpha()
            frame_w = sheet.get_width() / frames_count
            frame_h = sheet.get_height()
            return [transform.scale(sheet.subsurface(Rect(i * frame_w, 0, frame_w, frame_h)), (self.width, self.height)) for i in range(frames_count)]
        except:
            surf = Surface((self.width, self.height)); surf.fill((255, 0, 0)); return [surf]

#Функционал

    def update(self, platforms):
        if self.state != "dead":
            self.handle_input()
        

        self.vel_y += self.gravity
        self.hitbox.y += self.vel_y
        for p in platforms:
            if self.hitbox.colliderect(p.rect):
                if self.vel_y > 0:
                    self.hitbox.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.hitbox.top = p.rect.bottom
                    self.vel_y = 0


        if self.state != "attack":
            self.hitbox.x += self.vel_x
            for p in platforms:
                if self.hitbox.colliderect(p.rect):
                    if self.vel_x > 0: self.hitbox.right = p.rect.left
                    elif self.vel_x < 0: self.hitbox.left = p.rect.right


        self.rect.x = self.hitbox.x - self.hitbox_margin_x
        self.rect.y = self.hitbox.y - self.hitbox_margin_y

        if not self.on_ground and self.state not in ["attack", "dead"]:
            self.state = "jump"
        self.animate()

    def handle_input(self):
        if self.state in ["dead", "attack"]: 
            self.vel_x = 0
            return 
        keys = key.get_pressed()
        if keys[K_a]:
            self.vel_x = -self.speed; self.direction = "left"
            if self.on_ground: self.state = "walk"
        elif keys[K_d]:
            self.vel_x = self.speed; self.direction = "right"
            if self.on_ground: self.state = "walk"
        else:
            self.vel_x = 0
            if self.on_ground: self.state = "idle"
        if keys[K_f]:
            self.state = "attack"; self.frame_index = 0

    def jump(self):
        if self.on_ground: self.vel_y = self.jump_power; self.on_ground = False

    def animate(self):
        now = time.get_ticks()
        if now - self.update_time > self.animation_speed:
            self.update_time = now
            anim_list = self.animations_right[self.state] if self.direction == "right" else self.animations_left[self.state]
            self.frame_index += 1
            if self.state == "dead":
                if self.frame_index >= len(anim_list) - 1:
                    self.frame_index = len(anim_list) - 1
                    display.update(); time.delay(1000); quit(); exit()
            elif self.state == "attack" and self.frame_index >= len(anim_list):
                self.state = "idle"; self.frame_index = 0
            else:
                self.frame_index %= len(anim_list)
            self.image = anim_list[self.frame_index]

    def get_attack_rect(self):
        side_width = 50
        if self.direction == "right":
            return Rect(self.hitbox.right, self.hitbox.y, side_width, self.hitbox.height)
        else:
            return Rect(self.hitbox.left - side_width, self.hitbox.y, side_width, self.hitbox.height)


class Enemy(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 100
        self.height = 140

        #Настройка хит бокса
        self.hitbox_margin_x = 25 
        self.hitbox_margin_y = 10

        path = "Ninja_Enemy/"
        self.animation_config = {
            "idle": ("Enemy_Idle.png", 7), "walk": ("Enemy_Run.png", 8),
            "jump": ("Enemy_Jump.png", 9), "dead": ("Enemy_Dead.png", 5)
        }
        self.animations_right = {}
        for name, (file, count) in self.animation_config.items():
            self.animations_right[name] = self.load_animation_sheet(path + file, count)
        
        a1 = self.load_animation_sheet(path + "Enemy_Attack_1.png", 4)
        a2 = self.load_animation_sheet(path + "Enemy_Attack_2.png", 5)
        self.animations_right["attack"] = a1 + a2
        
        self.animations_left = {}
        for name, frames in self.animations_right.items():
            self.animations_left[name] = [transform.flip(img, True, False) for img in frames]

        self.state = "idle"
        self.direction = "left"
        self.frame_index = 0
        self.image = self.animations_left[self.state][self.frame_index]
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = Rect(x + self.hitbox_margin_x, y + self.hitbox_margin_y, 
                           self.width - self.hitbox_margin_x * 2, self.height - self.hitbox_margin_y * 2)
        
        self.speed = 2
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_power = -14
        self.update_time = time.get_ticks()
        self.dir_change_time = time.get_ticks() 
        self.animation_speed = 100
        self.wait_timer = 0

    def load_animation_sheet(self, filename, frames_count):
        try:
            sheet = image.load(filename).convert_alpha()
            w = sheet.get_width() / frames_count
            h = sheet.get_height()
            return [transform.scale(sheet.subsurface(Rect(i*w, 0, w, h)), (self.width, self.height)) for i in range(int(frames_count))]
        except:
            s = Surface((self.width, self.height)); s.fill((255, 0, 0)); return [s]

    def update(self, platforms, player):
        if self.state == "dead":
            self.animate(); return

        now = time.get_ticks()

        view_ray_dist = 500
        if self.direction == "right":
            view_ray = Rect(self.hitbox.right, self.hitbox.y, view_ray_dist, self.hitbox.height)
        else:
            view_ray = Rect(self.hitbox.left - view_ray_dist, self.hitbox.y, view_ray_dist, self.hitbox.height)

        up_ray = Rect(self.hitbox.x, self.hitbox.top - 300, self.hitbox.width, 300)

        if up_ray.colliderect(player.hitbox) and self.state != "wait":
            self.state = "wait"; self.wait_timer = now
        elif view_ray.colliderect(player.hitbox) and self.state not in ["wait", "attack"]:
            self.state = "chase"

        if self.state == "wait":
            if now - self.wait_timer > 2000:
                self.direction = "right" if player.hitbox.x > self.hitbox.x else "left"
                self.state = "chase"
        
        elif self.state == "chase":
            dx = self.speed * 1.5 if self.direction == "right" else -self.speed * 1.5
            self.hitbox.x += dx
            # Прыжок перед стеной (проверяем хитбоксом)
            self.hitbox.x += (1 if self.direction == "right" else -1)
            for p in platforms:
                if self.hitbox.colliderect(p.rect) and self.vel_y == 0:
                    self.vel_y = self.jump_power
            self.hitbox.x -= (1 if self.direction == "right" else -1)

        elif self.state == "idle":
            if now - self.dir_change_time > 5000:
                self.direction = "right" if self.direction == "left" else "left"
                self.dir_change_time = now

        # Гравитация
        self.vel_y += self.gravity
        self.hitbox.y += self.vel_y
        for p in platforms:
            if self.hitbox.colliderect(p.rect):
                if self.vel_y > 0: self.hitbox.bottom = p.rect.top; self.vel_y = 0

        self.rect.x = self.hitbox.x - self.hitbox_margin_x
        self.rect.y = self.hitbox.y - self.hitbox_margin_y
        self.animate()

    def animate(self):
        now = time.get_ticks()
        if now - self.update_time > self.animation_speed:
            self.update_time = now
            curr = "walk" if self.state == "chase" else ("idle" if self.state == "wait" else self.state)
            anim_list = self.animations_right[curr] if self.direction == "right" else self.animations_left[curr]
            self.frame_index += 1
            if self.state == "dead" and self.frame_index >= len(anim_list):
                self.frame_index = len(anim_list) - 1
            elif self.state == "attack" and self.frame_index >= len(anim_list):
                self.state = "idle"; self.frame_index = 0
            else:
                self.frame_index %= len(anim_list)
            self.image = anim_list[self.frame_index]