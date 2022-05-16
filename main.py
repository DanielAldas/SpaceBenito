import pygame
import os
import time
import random

pygame.font.init()
pygame.init()

largo = 900
alto = 750
pantalla = pygame.display.set_mode((largo, alto))
pygame.display.set_caption("Space Benito")

#cargando assets
# Personajes
kendrick = pygame.image.load("assets/kendrick.png")
jackh = pygame.image.load("assets/jack.png")
rosalia = pygame.image.load("assets/rosalia.png")
badbunny =  pygame.image.load("assets/benito.png")

# Disparos
mrmorale = pygame.image.load("assets/morale.jpeg")
comeh = pygame.image.load("assets/harlow.jpeg")
motomami = pygame.image.load("assets/motomami.jpg")
verano = pygame.image.load("assets/verano.jpg")
sonido_disparo=pygame.mixer.Sound("assets/yeh.wav")

#Fondo de pantalla
fondo = pygame.transform.scale(pygame.image.load("assets/fondo.png"), (largo, alto))

class Album:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def mover(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return colide(self, obj)


class Personaje:

    COOLDOWN = 30

    def __init__(self, x, y, vida=100):
        self.x = x
        self.y = y
        self.vida = vida
        self.personaje_img = None
        self.album_img = None
        self.albums = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.personaje_img, (self.x, self.y))
        for album in self.albums:
            album.draw(window)

    def mover_album(self, vel, obj):
        self.cooldown()
        for album in self.albums:
            album.mover(vel)
            if album.off_screen(alto):
                self.albums.remove(album)
            elif album.collision(obj):
                obj.vida -= 10
                self.albums.remove(album)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            album = Album(self.x, self.y, self.album_img)
            self.albums.append(album)
            self.cool_down_counter = 1

    def get_width(self):
        return self.personaje_img.get_width()

    def get_height(self):
        return self.personaje_img.get_height()


class Jugador(Personaje):
    def __init__(self, x, y, vida=100):
        super().__init__(x, y, vida)
        self.personaje_img = badbunny
        self.album_img = verano
        self.mask = pygame.mask.from_surface(self.personaje_img)
        self.vida_max = vida

    def mover_album(self, vel, objs):
        self.cooldown()
        for album in self.albums:
            album.mover(vel)
            if album.off_screen(largo):
                self.albums.remove(album)
            else:
                for obj in objs:
                    if album.collision(obj):
                        objs.remove(obj)
                        if album in self.albums:
                            self.albums.remove(album)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.personaje_img.get_height() + 10, self.personaje_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.personaje_img.get_height() + 10, self.personaje_img.get_width() * (self.vida/self.vida_max), 10))


class Enemigo(Personaje):
    mapa_nombres = { 
        "rosalia" : (rosalia, motomami),
        "jack" : (jackh, comeh),
        "kendrick" : (kendrick, mrmorale)
        }

    def __init__(self, x, y, nombre, vida=100):
        super().__init__(x, y, vida)
        self.personaje_img, self.album_img = self.mapa_nombres[nombre]
        self.mask = pygame.mask.from_surface(self.personaje_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            album = Album(self.x + 15, self.y, self.album_img)
            self.albums.append(album)
            self.cool_down_counter = 1


def colide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    fps = 60
    level = 0
    crash = 5
    score = 0
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    
    pygame.mixer.music.load('assets/si_veo_a_tu_mama.wav')
    pygame.mixer.music.play(-1, 0.0)
    
    enemies = []
    wave_length = 5
    enemigo_vel = 1

    player_vel = 5
    album_vel = 5

    benito = Jugador(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        pantalla.blit(fondo, (0,0))
        # draw text
        score_label = main_font.render(f"Choques: {crash}", 1, (255,255,255))
        level_label = main_font.render(f"Nivel: {level}", 1, (255,255,255))

        pantalla.blit(score_label, (10, 10))
        pantalla.blit(level_label, (largo - level_label.get_width() - 10, 10))

        for enemigo in enemies:
            enemigo.draw(pantalla)

        benito.draw(pantalla)

        if lost:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('assets/si_veo_a_tu_mama.wav')
            pygame.mixer.music.play(-1, 0.0)
            lost_label = lost_font.render("Perdiste!!", 1, (255,255,255))
            pantalla.blit(lost_label, (largo/2 - lost_label.get_width()/2, 350))
            

        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()

        if crash <= 0 or benito.vida <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > fps * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemigo = Enemigo(random.randrange(50, largo-100), random.randrange(-1500, -100), random.choice(["kendrick", "rosalia", "jack"]))
                enemies.append(enemigo)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT] and benito.x - player_vel > 0: # left
            benito.x -= player_vel
        if keys[pygame.K_d] or keys[pygame.K_RIGHT] and benito.x + player_vel + benito.get_width() < largo: # right
            benito.x += player_vel
        if keys[pygame.K_w] or keys[pygame.K_UP]and benito.y - player_vel > 0: # up
            benito.y -= player_vel
        if keys[pygame.K_s] or keys[pygame.K_DOWN] and benito.y + player_vel + benito.get_height() + 15 < largo: # down
            benito.y += player_vel
        if keys[pygame.K_SPACE]:
            sonido_disparo.play()
            benito.shoot()
            

        for enemigo in enemies[:]:
            enemigo.move(enemigo_vel)
            enemigo.mover_album(album_vel, benito)

            if random.randrange(0, 2*60) == 1:
                enemigo.shoot()

            if colide(enemigo, benito):
                benito.vida -= 10
                score += 1
                enemies.remove(enemigo)
            elif enemigo.y + enemigo.get_height() > largo:
                crash -= 1
                enemies.remove(enemigo)
                

        benito.mover_album(-album_vel, enemies)

def main_menu():
    pygame.mixer.music.load('assets/trellas.mp3')
    pygame.mixer.music.play(-1, 0.0)
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        pantalla.blit(fondo, (0,0))
        title_label = title_font.render("Click para jugar", 1, (255,255,255))
        pantalla.blit(title_label, (largo/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.music.stop()
                main()
                
    pygame.quit()


main_menu()