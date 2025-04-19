import asyncio
import pygame
import random
from pygame.locals import (K_SPACE, K_LEFT, K_RIGHT, K_a, K_d, K_l, K_i, K_ESCAPE, QUIT)
import csv
import sys

class Info():
    def __init__(self, spillobjekt, x, y, type):
        self.spillobjekt = spillobjekt
        self.x = x
        self.y = y
        self.bredde = 10
        self.hoyde = 10
        self.type = type
        self.verdi = 0
        try: # Keep basic error handling
            self.font = pygame.font.Font("filer/PressStart2P.ttf", 20)
        except pygame.error:
             self.font = pygame.font.Font(None, 30) # Fallback


    def vis(self):
        score_tekst = self.font.render(self.type+": "+str(round(self.verdi)), True, (255, 255, 255))
        self.spillobjekt.vindu.blit(score_tekst, (self.x, self.y))

class Gjenstand():
    def __init__(self,  spillobjekt, x, y, bredde, hoyde, liste):
        self.spillobjekt = spillobjekt
        self.x = x
        self.y = y
        self.bredde = bredde
        self.hoyde = hoyde
        self.boks = pygame.Rect(self.x, self.y, self.bredde, self.hoyde)
        self.hastighet = 5
        self.liste = liste

    def beveg(self):
        if (self.spillobjekt.taster[K_RIGHT] or self.spillobjekt.taster[K_d]) and self.spillobjekt.spiller.x >= self.spillobjekt.vindubredde / 2:
            self.x -= self.hastighet
        if self.x < -self.bredde:
            if self in self.liste:
                 self.liste.remove(self)
        self.boks.x = self.x

class Sky(Gjenstand):
    def __init__(self, spillobjekt, x):
        super().__init__(spillobjekt, x, random.randint(0, spillobjekt.vinduhoyde // 3), 100, 50, spillobjekt.skyer)
        self.bilder = []
        for n in range(3):
            self.bilder.append(pygame.transform.scale(pygame.image.load("bilder/sky"+str(n)+".png").convert_alpha(), (self.bredde, self.hoyde)))
        self.bilde = self.bilder[random.randint(0, len(self.bilder) - 1)]

    def vis(self):
        self.spillobjekt.vindu.blit(self.bilde, (self.x, self.y))

class Busk(Gjenstand):
    def __init__(self, spillobjekt, plattformobjekt):
        bredde = 80
        hoyde = 40
        self.plattformobjekt = plattformobjekt
        start_x = random.randint(int(plattformobjekt.x), max(int(plattformobjekt.x), int(plattformobjekt.x + plattformobjekt.bredde - bredde)))
        super().__init__(spillobjekt, start_x, plattformobjekt.y - hoyde, bredde, hoyde, spillobjekt.busker)
        self.bilder = []
        for n in range(3):
            self.bilder.append(pygame.transform.scale(pygame.image.load("bilder/busk"+str(n)+".png").convert_alpha(), (self.bredde, self.hoyde)))
        self.bilde = self.bilder[random.randint(0, len(self.bilder) - 1)]

    def vis(self):
        self.spillobjekt.vindu.blit(self.bilde, (self.x, self.y))

class Plattform(Gjenstand):
    def __init__(self, spillobjekt, x, bredde):
        hoyde = random.randint(60, 150)
        super().__init__(spillobjekt, x, spillobjekt.vinduhoyde - hoyde, bredde, hoyde, spillobjekt.plattformer)
        self.farge = (200, 200, 50)
        self.andrefarge = (150, 150, 40)
        self.kantfarge = (0, 0, 0)

    def vis(self):
        pygame.draw.rect(self.spillobjekt.vindu, self.farge, (self.x, self.y, self.bredde, self.hoyde), 0)
        pygame.draw.rect(self.spillobjekt.vindu, self.andrefarge, (self.x, self.y, self.bredde, self.hoyde), 13)
        pygame.draw.rect(self.spillobjekt.vindu, self.kantfarge, (self.x, self.y, self.bredde, self.hoyde), 3)

    def opprettElementer(self):
        for i in range (random.randint(0, round(self.bredde / 300))):
            self.spillobjekt.skurker.append(Skurk(self.spillobjekt, self, self.spillobjekt.skurker))
        for i in range (random.randint(0, round(self.bredde / 100))):
            self.spillobjekt.busker.append(Busk(self.spillobjekt, self))

class Spiller():
    def __init__(self,spillobjekt):
        self.spillobjekt = spillobjekt
        self.x = 50.0
        self.y = float(spillobjekt.vinduhoyde / 2)
        self.bredde = 45
        self.hoyde = 60
        self.boks = pygame.Rect(int(self.x), int(self.y), self.bredde, self.hoyde)
        self.hastighet_x = 5.0
        self.hastighet_y = 0.0
        self.bilder = []
        for n in range(11):
            try: # Keep basic error handling
                self.bilder.append(pygame.transform.scale(pygame.image.load("bilder/spiller"+str(n)+".png").convert_alpha(), (self.bredde, self.hoyde)))
            except pygame.error: pass # Ignore missing images
        self.bilder_revers = []
        for bilde in self.bilder:
            self.bilder_revers.append(pygame.transform.flip(bilde,True,False))
        self.bildeliste = self.bilder
        self.bildenr = 0
        self.drept_lyd = pygame.mixer.Sound("lydfiler/wilhelm_scream.ogg")
        self.animasjon_tid = pygame.time.get_ticks()
        self.animasjon_intervall = 50
        self.drept = False
        self.liv = Info(spillobjekt, 350, 10, "Liv")
        self.liv.verdi = 3

    def beveg(self):
        if self.spillobjekt.taster[K_LEFT] or self.spillobjekt.taster[K_a]:
            self.x -= self.hastighet_x
            self.animasjon(False)
        elif (self.spillobjekt.taster[K_RIGHT] or self.spillobjekt.taster[K_d]):
            if self.x < self.spillobjekt.vindubredde / 2:
                self.x += self.hastighet_x
            self.animasjon(True)
        if self.x < 0:
            self.x = 0

        on_ground_simple = self.hastighet_y == 0
        if self.spillobjekt.taster[K_SPACE] and on_ground_simple:
            self.hastighet_y = -12.0
        self.hastighet_y += 0.7
        self.hastighet_y = min(12.0, self.hastighet_y)
        self.y += self.hastighet_y

        self.boks.x = int(self.x)
        self.boks.y = int(self.y)

        if self.y > self.spillobjekt.vinduhoyde:
            self.drept = True

        for plattform in self.spillobjekt.plattformer:
            if self.boks.colliderect(plattform.boks):
                if self.hastighet_y > 0 and self.boks.bottom <= plattform.boks.top + 25:
                    self.y = float(plattform.y - self.hoyde)
                    self.hastighet_y = 0.0
                    self.boks.y = int(self.y)
                elif self.hastighet_y <=0 :
                     if self.boks.right > plattform.boks.left and self.boks.left < plattform.boks.left:
                          self.x = float(plattform.boks.left - self.bredde)
                     elif self.boks.left < plattform.boks.right and self.boks.right > plattform.boks.right:
                          self.x = float(plattform.boks.right)
                break

        # Kollisjon med skurk
        for skurk in self.spillobjekt.skurker: 
            if self.boks.colliderect(skurk.boks):
                if self.y < skurk.y - self.hoyde + 25 and self.hastighet_y > 0: 
                    skurk.drept_tid = pygame.time.get_ticks()
                elif skurk.drept_tid == 0:
                    self.drept = True

        self.boks.x = int(self.x)
        self.boks.y = int(self.y)


    def vis(self):
        # Drawing logic ONLY, no respawn trigger
        if self.bildeliste and len(self.bildeliste) > self.bildenr:
            # Use dead sprite visual if flag is set, otherwise normal anim
            sprite_index = 10 if self.drept and len(self.bilder) > 10 else self.bildenr
            # Ensure index is valid before drawing
            if sprite_index < len(self.bildeliste):
                 self.spillobjekt.vindu.blit(self.bildeliste[sprite_index], (self.x, self.y))


    def animasjon(self,retning_hoyre):
        if pygame.time.get_ticks() - self.animasjon_tid > self.animasjon_intervall:
            self.animasjon_tid = pygame.time.get_ticks()
            self.bildenr += 1
            if self.bildenr >= 10:
                self.bildenr = 0
            if retning_hoyre:
                self.bildeliste = self.bilder
            else:
                self.bildeliste = self.bilder_revers

    def respawn(self):
        # Modified respawn logic
        if self.liv.verdi <= 1:
            # Signal game over to the main game object
            self.spillobjekt.trigger_game_over()
        else:
            # Reset level and player state for respawn
            self.spillobjekt.reset_level_elements() # Separate method in Spill
            self.drept_lyd.play()
            self.y = float(self.spillobjekt.vinduhoyde / 2)
            self.x = 50.0
            self.hastighet_y = 0.0
            self.liv.verdi -= 1
            self.drept = False # Reset flag after handling

class Skurk():
    def __init__(self, spillobjekt, plattformobjekt, liste):
        self.spillobjekt = spillobjekt
        self.plattformobjekt = plattformobjekt
        self.bredde = 60
        self.hoyde = 60
        start_x = random.uniform(plattformobjekt.x + plattformobjekt.bredde / 2, max(plattformobjekt.x + plattformobjekt.bredde / 2, plattformobjekt.x + plattformobjekt.bredde - self.bredde))
        self.x = float(start_x)
        self.y = float(plattformobjekt.y - self.hoyde)
        self.boks = pygame.Rect(int(self.x), int(self.y), self.bredde, self.hoyde)
        self.hastighet_abs = 1.0 + spillobjekt.score.verdi / 2000.0
        self.hastighet = self.hastighet_abs
        self.bilder = []
        try: # Keep basic error handling
            for n in range(11):
                self.bilder.append(pygame.transform.scale(pygame.image.load("bilder/skurk"+str(n)+".png").convert_alpha(), (self.bredde, self.hoyde)))
        except pygame.error: pass
        self.bilder_revers = []
        for bilde in self.bilder:
            self.bilder_revers.append(pygame.transform.flip(bilde,True,False))
        self.bildeliste = self.bilder_revers
        self.bildenr = 0
        self.drept_lyd = pygame.mixer.Sound("lydfiler/minecraft_scream.ogg")
        self.animasjon_tid = pygame.time.get_ticks()
        self.animasjon_intervall = 100
        self.drept_tid = 0
        self.liste = liste

    def beveg(self):
        if self.drept_tid > 0:
            self.hastighet = 0
            return

        scroll_speed = 0
        if (self.spillobjekt.taster[K_RIGHT] or self.spillobjekt.taster[K_d]) and self.spillobjekt.spiller.x >= self.spillobjekt.vindubredde / 2:
            scroll_speed = self.spillobjekt.spiller.hastighet_x

        self.x -= (self.hastighet + scroll_speed)
        self.animasjon()

        if self.x <= self.plattformobjekt.x:
            self.x = float(self.plattformobjekt.x)
            self.hastighet = -self.hastighet_abs
        elif self.x >= self.plattformobjekt.x + self.plattformobjekt.bredde - self.bredde:
            self.x = float(self.plattformobjekt.x + self.plattformobjekt.bredde - self.bredde)
            self.hastighet = self.hastighet_abs

        if self.x < -self.spillobjekt.vindubredde:
             if self in self.liste:
                 self.liste.remove(self)

        self.boks.x = int(self.x)
        self.boks.y = int(self.y)

    def animasjon(self):
         if pygame.time.get_ticks() - self.animasjon_tid > self.animasjon_intervall:
              self.animasjon_tid = pygame.time.get_ticks()
              self.bildenr += 1
              if self.bildenr >= 10:
                   self.bildenr = 0
              if self.hastighet > 0:
                   self.bildeliste = self.bilder_revers
              else:
                   self.bildeliste = self.bilder

    def vis(self):
        # Original vis logic including removal
        if self.drept_tid > 0:
            self.drept_lyd.play()
            if len(self.bilder) > 10:
                 self.spillobjekt.vindu.blit(self.bilder[10], (self.x, self.y))
            if pygame.time.get_ticks() - self.drept_tid > 200:
                self.spillobjekt.score.verdi += 100
                if self in self.liste:
                     self.liste.remove(self)
        else:
             if self.bildeliste and len(self.bildeliste) > self.bildenr:
                  self.spillobjekt.vindu.blit(self.bildeliste[self.bildenr], (self.x, self.y))

class Spill():
    def __init__(self, history = True):
        pygame.init()
        pygame.display.set_caption("SUPER AIMARIO")
        pygame.mixer.init()
        pygame.mixer.music.load("lydfiler/wii.ogg")

        self.history = history
        self.spill = False
        self.info = False
        self.game_over = False # New flag for game over state
        self.vindubredde = 800
        self.vinduhoyde = 600
        self.vindu = pygame.display.set_mode((self.vindubredde, self.vinduhoyde))
        self.klokke = pygame.time.Clock()
        self.starttid = pygame.time.get_ticks()
        self.score = Info(self, 50, 10, "Score")
        self.tid = Info(self, 600, 10, "Tid")
        self.spiller = Spiller(self)
        self.skurker = []
        self.skyer = []
        self.busker = []
        self.plattformer = []
        self.reset_level_elements(True) # Initial population
        self.taster = pygame.key.get_pressed()

    def reset_level_elements(self, initial=False):
         self.skurker.clear()
         self.skyer.clear()
         self.busker.clear()
         self.plattformer.clear()
         for i in range (random.randint(5, 10)):
              self.skyer.append(Sky(self,random.randint(0, self.vindubredde)))
         plattform = Plattform(self, 0, self.vindubredde)
         self.plattformer.append(plattform)
         plattform.opprettElementer()
         # Reset score/time only on full game reset, not just respawn level reset
         if not initial and self.game_over: # Check if called from game over reset
              self.score.verdi = 0
              self.tid.verdi = 0
              self.starttid = pygame.time.get_ticks()

    def reset_game(self):
         # Reset all game state for a new game
         self.spill = True
         self.info = False
         self.game_over = False
         self.score.verdi = 0
         self.tid.verdi = 0
         self.starttid = pygame.time.get_ticks()
         self.spiller = Spiller(self) # Create new player with full lives
         self.reset_level_elements(False) # Reset elements

    def trigger_game_over(self):
         self.game_over = True
         self.spill = False # Stop active gameplay
         # Attempt score saving
         try:
              with open("filer/score.csv", "a", encoding="utf-8", newline="") as fil:
                   csv.writer(fil).writerow([round(self.tid.verdi),round(self.score.verdi)])
         except Exception as e: print(f"Game Over score save error: {e}")


    def visStartvindu(self):
        tid_verdier = []
        score_verdier = [0]
        try:
            with open("filer/score.csv", encoding="utf-8") as fil:
                filinnhold = csv.reader(fil, delimiter=",")
                next(filinnhold)
                for rad in filinnhold:
                     if len(rad) >= 2:
                          try:
                               tid_verdier.append(rad[0])
                               score_verdier.append(int(rad[1]))
                          except ValueError: continue
                score = score_verdier[-1] if score_verdier else 0
                high_score = max(score_verdier) if score_verdier else 0
        except (FileNotFoundError, StopIteration): score, high_score = 0, 0
        except Exception: score, high_score = 0, 0 # Catch other errors

        # State check moved to spillLokke

        tittel_font = pygame.font.Font("filer/PressStart2P.ttf", 70)
        stor_font = pygame.font.Font("filer/PressStart2P.ttf", 20)
        liten_font = pygame.font.Font("filer/PressStart2P.ttf", 15)
        super_tekst = tittel_font.render("SUPER", True, (255, 255, 100))
        aimario_tekst = tittel_font.render("AIMARIO", True, (255, 255, 100))
        start_tekst = stor_font.render("Trykk SPACE for å starte", True, (255, 255, 255)) # aa for å
        high_score_tekst = liten_font.render("High score: "+str(high_score), True, (255, 255, 255))
        score_tekst = liten_font.render("Siste score: "+str(score), True, (255, 255, 255))
        info_tekst = liten_font.render("Info (Trykk I)", True, (255, 255, 255))

        super_boks = super_tekst.get_rect(center=(self.vindubredde / 2, 100))
        aimario_boks = aimario_tekst.get_rect(center=(self.vindubredde / 2, 200))
        start_boks = start_tekst.get_rect(center=(self.vindubredde / 2, self.vinduhoyde / 2))
        high_score_boks = high_score_tekst.get_rect(center=(self.vindubredde / 2, 400))
        score_boks = score_tekst.get_rect(center=(self.vindubredde / 2, 450))
        info_boks = info_tekst.get_rect(center=(self.vindubredde / 2, 500))

        self.vindu.fill((100, 150, 200))
        self.vindu.blit(super_tekst, super_boks)
        self.vindu.blit(aimario_tekst, aimario_boks)
        self.vindu.blit(start_tekst, start_boks)
        self.vindu.blit(high_score_tekst, high_score_boks)
        self.vindu.blit(score_tekst, score_boks)
        self.vindu.blit(info_tekst, info_boks)

    def visInfo(self):
        # State check moved to spillLokke

        font = pygame.font.Font("filer/PressStart2P.ttf", 15)
        beveg_tekst = font.render("AD/piltaster og SPACE for å bevege", True, (255, 255, 255))
        dod_tekst = font.render("Ikke treff skurkene eller fall ned", True, (255, 255, 255))
        poeng_tekst = font.render("Land oppå skurkene for 100 poeng", True, (255, 255, 255))
        lukk_tekst = font.render("Trykk ESC for å lukke infovinduet", True, (255, 255, 255))

        beveg_boks = beveg_tekst.get_rect(center=(self.vindubredde / 2, 100))
        dod_boks = dod_tekst.get_rect(center=(self.vindubredde / 2, 200))
        poeng_boks = poeng_tekst.get_rect(center=(self.vindubredde / 2, 300))
        lukk_boks = lukk_tekst.get_rect(center=(self.vindubredde / 2, 500))

        self.vindu.fill((100, 150, 200))
        self.vindu.blit(beveg_tekst, beveg_boks)
        self.vindu.blit(dod_tekst, dod_boks)
        self.vindu.blit(poeng_tekst, poeng_boks)
        self.vindu.blit(lukk_tekst, lukk_boks)

    def visGameOver(self):
         # Draws the game over screen
         self.vindu.fill((0, 0, 0))
         font_large = pygame.font.Font("filer/PressStart2P.ttf", 100)
         font_small = pygame.font.Font("filer/PressStart2P.ttf", 20)
         game_tekst = font_large.render("GAME", True, (255, 255, 255))
         over_tekst = font_large.render("OVER", True, (255, 255, 255))
         restart_tekst = font_small.render("Trykk SPACE for å prove igjen", True, (255, 255, 255)) # aa for å

         game_boks = game_tekst.get_rect(center=(self.vindubredde / 2, 250))
         over_boks = over_tekst.get_rect(center=(self.vindubredde / 2, 350))
         restart_boks = restart_tekst.get_rect(center=(self.vindubredde / 2, 500))

         self.vindu.blit(game_tekst, game_boks)
         self.vindu.blit(over_tekst, over_boks)
         self.vindu.blit(restart_tekst, restart_boks)


    def opprettElementer(self):
        if (self.taster[K_RIGHT] or self.taster[K_d]) and self.spiller.x >= self.vindubredde / 2:
            if random.randint(1, 20) == 1:
                self.skyer.append(Sky(self, self.vindubredde))
            if self.plattformer:
                 if self.vindubredde - (self.plattformer[-1].x + self.plattformer[-1].bredde) > 130:
                     plattform = Plattform(self, self.vindubredde, random.randint(100, 1000))
                     self.plattformer.append(plattform)
                     plattform.opprettElementer()
            # Keep original score logic
            self.score.verdi += 1/10

    def kjorRunde(self):
        self.tid.verdi = round((pygame.time.get_ticks() - self.starttid) / 1000)
        self.spiller.beveg()
        # Keep original iteration
        for skurk in self.skurker: skurk.beveg()
        for sky in self.skyer: sky.beveg()
        for busk in self.busker: busk.beveg()
        for plattform in self.plattformer: plattform.beveg()
        self.opprettElementer()

        # Drawing happens in spillLokke now based on state

    async def spillLokke(self):
        while True:
            for hendelse in pygame.event.get():
                if hendelse.type == QUIT:
                    pygame.quit()
                    exit() # Keep original exit

            self.taster = pygame.key.get_pressed()

            # --- Handle Input and State Changes First ---
            if self.game_over:
                if self.taster[K_SPACE]:
                    self.reset_game() # Reset the game state
                elif self.taster[K_ESCAPE]:
                    self.spill = False
                    self.info = False
                    self.game_over = False
            elif not self.spill and not self.info: # Start Screen
                if self.taster[K_SPACE]:
                    self.spill = True
                    pygame.mixer.music.play(-1) 
                    self.info = False
                    self.game_over = False # Ensure game over is false
                    self.starttid = pygame.time.get_ticks()
                elif self.taster[K_i]:
                    self.info = True
            elif self.info: # Info Screen
                if self.taster[K_ESCAPE]:
                    self.info = False
            elif self.spill: # Gameplay Screen
                if self.taster[K_ESCAPE]: # Option to return to menu
                     self.spill = False
                     self.info = False
                     self.game_over = False


            # --- Update Game Logic if Active ---
            if self.spill:
                self.kjorRunde() # Update positions, handle movement etc.
                if self.spiller.drept: # Check for death AFTER update
                    self.spiller.respawn() # Call modified respawn (sets game_over or resets state)

            # --- Draw Current State ---
            if self.game_over:
                self.visGameOver()
            elif self.spill:
                # Drawing previously done in kjorRunde, needs to be here
                self.vindu.fill((100, 150, 200))
                self.score.vis()
                self.spiller.liv.vis()
                self.tid.vis()
                for sky in self.skyer: sky.vis()
                for busk in self.busker: busk.vis()
                for plattform in self.plattformer: plattform.vis()
                for skurk in self.skurker: skurk.vis()
                self.spiller.vis() # Draws player (including potentially dead sprite briefly)
            elif self.info:
                self.visInfo()
            else: # Start screen
                self.visStartvindu()

            pygame.display.flip()
            self.klokke.tick(60)
            await asyncio.sleep(0)


async def run_game():
    spill_instance = Spill()
    try:
        await spill_instance.spillLokke()
    except Exception as e:
        print(f"Error during game loop: {e}")
        try: # Attempt cleanup even on error
             pygame.quit()
        except: pass # Ignore errors during cleanup


if __name__ == "__main__":
    import asyncio # Ensure imported here
    asyncio.run(run_game())