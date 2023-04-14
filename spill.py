# SUPER AIMARIO

# Importerer biblioteker
import pygame
import random
from pygame.locals import (K_SPACE, K_LEFT, K_RIGHT, K_a, K_d, K_l, K_i, K_ESCAPE)
import csv
import matplotlib.pyplot as plt

# Definer infotekstklassen
class Info(): 
    """ 
    Klasse for å lage info-objekt 
    
    Parametre:
    spillobjekt (Spill): tilhørende spillobjekt
    x (int): x-verdien til objektet
    y (int): y-verdien til objektet
    type (str): typen info
    """

    def __init__(self, spillobjekt, x, y, type):
        """ Konstruktør """
        self.spillobjekt = spillobjekt
        self.x = x
        self.y = y
        self.bredde = 10
        self.hoyde = 10
        self.type = type
        self.verdi = 0

    def vis(self):
        """ Metode for å tegne infoen """
        font = pygame.font.Font("filer\\PressStart2P.ttf", 20)
        score_tekst = font.render(self.type+": "+str(round(self.verdi)), True, (255, 255, 255))
        self.spillobjekt.vindu.blit(score_tekst, (self.x, self.y))

# Definer gjenstand-klassen
class Gjenstand():
    """ 
    Klasse for å lage ulike gjenstander i miljøet 
    
    Parametre:
    spillobjekt (Spill): tilhørende spillobjekt
    x (int): x-verdien til objektet
    y (int): y-verdien til objektet
    bredde (int): bredden til objektet
    hoyde (int): høyden til objektet
    liste (list): det tilhørende spillobjektets liste over gjenstandene
    """

    def __init__(self,  spillobjekt, x, y, bredde, hoyde, liste):
        """ Konstruktør """
        self.spillobjekt = spillobjekt
        self.x = x
        self.y = y
        self.bredde = bredde
        self.hoyde = hoyde
        self.boks = pygame.Rect(self.x, self.y, self.bredde, self.hoyde)
        self.hastighet = 5
        self.liste = liste   

    def beveg(self):
        """ Metode for å bevege gjenstanden """
        if (self.spillobjekt.taster[K_RIGHT] or self.spillobjekt.taster[K_d]) and self.spillobjekt.spiller.x >= self.spillobjekt.vindubredde / 2:
            self.x -= self.hastighet
        if self.x < -self.bredde:
            self.liste.remove(self)
        self.boks.x = self.x

# Definer Sky-klassen
class Sky(Gjenstand):
    """ 
    Klasse for å lage sky-objekt 
    
    Parametre:
    spillobjekt (Spill): tilhørende spillobjekt
    x (int): x-verdien til objektet
    """

    def __init__(self, spillobjekt, x):
        """ Konstruktør """
        super().__init__(spillobjekt, x, random.randint(0, spillobjekt.vinduhoyde / 3), 100, 50, spillobjekt.skyer)
        self.bilder = []
        for n in range(3):
            self.bilder.append(pygame.transform.scale(pygame.image.load("bilder\\sky"+str(n)+".png").convert_alpha(), (self.bredde, self.hoyde)))
        self.bilde = self.bilder[random.randint(0, len(self.bilder) - 1)]

    def vis(self):
        """ Metode for å tegne skyen """
        self.spillobjekt.vindu.blit(self.bilde, (self.x, self.y))

# Definer Busk-klassen
class Busk(Gjenstand):
    """ 
    Klasse for å lage busk-objekt 
    
    Parametre:
    spillobjekt (Spill): tilhørende spillobjekt
    plattformobjekt (Plattform): tilhørende plattformobjekt
    """

    def __init__(self, spillobjekt, plattformobjekt):
        """ Konstruktør """
        bredde = 80
        hoyde = 40
        self.plattformobjekt = plattformobjekt
        super().__init__(spillobjekt, random.randint(plattformobjekt.x, plattformobjekt.x + plattformobjekt.bredde - bredde), plattformobjekt.y - hoyde, bredde, hoyde, spillobjekt.busker)
        self.bilder = []
        for n in range(3):
            self.bilder.append(pygame.transform.scale(pygame.image.load("bilder\\busk"+str(n)+".png").convert_alpha(), (self.bredde, self.hoyde)))
        self.bilde = self.bilder[random.randint(0, len(self.bilder) - 1)]

    def vis(self):
        """ Metode for å tegne busken """
        self.spillobjekt.vindu.blit(self.bilde, (self.x, self.y))

# Definer Plattform-klasse
class Plattform(Gjenstand):
    """ 
    Klasse for å lage plattform-objekt 

    Parametre:
    spillobjekt (Spill): tilhørende spillobjekt
    x (int): x-verdien til objektet
    bredde (int): bredden til objektet
    """

    def __init__(self, spillobjekt, x, bredde):
        """ Konstruktør """
        hoyde = random.randint(60, 150)
        super().__init__(spillobjekt, x, spillobjekt.vinduhoyde - hoyde, bredde, hoyde, spillobjekt.plattformer)
        self.farge = (200, 200, 50)
        self.andrefarge = (150, 150, 40)
        self.kantfarge = (0, 0, 0)
    
    def vis(self):
        """ Metode for å tegne plattformen """
        pygame.draw.rect(self.spillobjekt.vindu, self.farge, (self.x, self.y, self.bredde, self.hoyde), 0)
        pygame.draw.rect(self.spillobjekt.vindu, self.andrefarge, (self.x, self.y, self.bredde, self.hoyde), 13)
        pygame.draw.rect(self.spillobjekt.vindu, self.kantfarge, (self.x, self.y, self.bredde, self.hoyde), 3)

    def opprettElementer(self):
        """ Metode for å opprette skurker og busker på plattformen """
        for i in range (random.randint(0, round(self.bredde / 300))):
            self.spillobjekt.skurker.append(Skurk(self.spillobjekt, self, self.spillobjekt.skurker))
        for i in range (random.randint(0, round(self.bredde / 100))):
            self.spillobjekt.busker.append(Busk(self.spillobjekt, self))

# Definer spillerklassen
class Spiller():
    """ 
    Klasse for å lage spiller-objekt 

    Parametre:
    spillobjekt (Spill): tilhørende spillobjekt
    """
    
    def __init__(self,spillobjekt):
        """ Konstruktør """
        self.spillobjekt = spillobjekt
        self.x = 50
        self.y = spillobjekt.vinduhoyde / 2
        self.bredde = 45
        self.hoyde = 60
        self.boks = pygame.Rect(self.x, self.y, self.bredde, self.hoyde)
        self.hastighet_x = 5
        self.hastighet_y = 0
        self.bilder = []
        for n in range(11):
            self.bilder.append(pygame.transform.scale(pygame.image.load("bilder\\spiller"+str(n)+".png").convert_alpha(), (self.bredde, self.hoyde)))
        self.bilder_revers = []
        for bilde in self.bilder:
            self.bilder_revers.append(pygame.transform.flip(bilde,True,False))
        self.bildeliste = self.bilder
        self.bildenr = 0
        self.drept_lyd = pygame.mixer.Sound("lydfiler\\wilhelm_scream.mp3")
        self.animasjon_tid = pygame.time.get_ticks()
        self.drept = False
        self.liv = Info(spillobjekt, 350, 10, "Liv")
        self.liv.verdi = 3

    def beveg(self):
        """ Metode for å bevege spilleren """

        # Bevegelse til venstre
        if self.spillobjekt.taster[K_LEFT] or self.spillobjekt.taster[K_a]:
            self.x -= self.hastighet_x
            self.animasjon(False)

        # Bevegelse til høyre
        elif (self.spillobjekt.taster[K_RIGHT] or self.spillobjekt.taster[K_d]):
            if self.x < self.spillobjekt.vindubredde / 2:
                self.x += self.hastighet_x
            self.animasjon(True)
        if self.x < 0:
            self.x = 0

        # Vertikal bevegelse med tyngdekraft
        if self.spillobjekt.taster[K_SPACE] and self.hastighet_y == 0:
            self.hastighet_y = -12
        self.hastighet_y += 0.7
        self.hastighet_y = min([12, self.hastighet_y])
        self.y += self.hastighet_y
        if self.y > self.spillobjekt.vinduhoyde - self.hoyde:
            self.drept = True
        
        # Kollisjon med plattform
        for plattform in self.spillobjekt.plattformer:
            if self.boks.colliderect(plattform.boks):
                if self.y < plattform.y - self.hoyde + 25 and self.hastighet_y > 0:
                    self.y = plattform.y - self.hoyde
                    self.hastighet_y = 0
                else: 
                    self.x = plattform.x - self.bredde
                break
        
        # Kollisjon med skurk
        for skurk in self.spillobjekt.skurker: 
            if self.boks.colliderect(skurk.boks):
                if self.y < skurk.y - self.hoyde + 25 and self.hastighet_y > 0: 
                    skurk.drept_tid = pygame.time.get_ticks()
                elif skurk.drept_tid == 0:
                    self.drept = True
    
        self.boks.x = self.x
        self.boks.y = self.y
        
    def vis(self):
        """ Metode for å tegne spilleren """

        # Sjekker om spiller er drept
        if self.drept:
            self.drept_lyd.play()
            self.spillobjekt.vindu.blit(self.bildeliste[10], (self.x, self.y))
            pygame.display.update()
            pygame.time.wait(1000)
            self.respawn()
            self.drept = False
        else: 
        
        # Tegner normalt hvis ikke
            self.spillobjekt.vindu.blit(self.bildeliste[self.bildenr], (self.x, self.y))

    def animasjon(self,retning_hoyre):
        """ Metode for å animere spilleren """
        if pygame.time.get_ticks() - self.animasjon_tid > 50:
            self.animasjon_tid = pygame.time.get_ticks()
            self.bildenr += 1
            if self.bildenr == len(self.bilder) - 1:
                self.bildenr = 0
            if retning_hoyre:
                self.bildeliste = self.bilder
            else: 
                self.bildeliste = self.bilder_revers

    def respawn(self):
        """ Metode for å respawne """

        # Game Over
        if self.liv.verdi <= 1: 

            # Lagre score og tid
            with open("filer\\score.csv", "a", encoding="utf-8-sig", newline="") as fil: 
                csv.writer(fil).writerow([round(self.spillobjekt.tid.verdi),round(self.spillobjekt.score.verdi)])
       
            # Vis Game Over
            self.spillobjekt.vindu.fill((0, 0, 0))
            font = pygame.font.Font("filer\\PressStart2P.ttf", 100)
            game_tekst = font.render("GAME", True, (255, 255, 255))
            over_tekst = font.render("OVER", True, (255, 255, 255))
            game_boks = game_tekst.get_rect(center=(self.spillobjekt.vindubredde / 2, 250))
            over_boks = over_tekst.get_rect(center=(self.spillobjekt.vindubredde / 2, 350))
            self.spillobjekt.vindu.blit(game_tekst, game_boks)
            self.spillobjekt.vindu.blit(over_tekst, over_boks)
            pygame.display.update()
            pygame.time.wait(3000)

            # Restart spillet
            Spill().spillLokke()
        
        # Respawn hvis spiller har mer liv
        else: 
            self.spillobjekt.skurker = []
            self.spillobjekt.skyer = []
            self.spillobjekt.busker = []
            self.spillobjekt.plattformer = []
            for i in range (random.randint(5, 10)):
                self.spillobjekt.skyer.append(Sky(self.spillobjekt, random.randint(0, self.spillobjekt.vindubredde)))
            plattform = Plattform(self.spillobjekt, 0, self.spillobjekt.vindubredde)
            self.spillobjekt.plattformer.append(plattform)
            plattform.opprettElementer()
            self.y = self.spillobjekt.vinduhoyde / 2
            self.x = 50
            self.liv.verdi -= 1

# Definer Skurk-klassen
class Skurk():
    """ 
    Klasse for å lage skurk-objekt 

    Parametre:
    spillobjekt (Spill): tilhørende spillobjekt
    plattformobjekt (Plattform): tilhørende plattformobjekt
    liste (liste): det tilhørende spillobjektets liste over skurkene
    """

    def __init__(self, spillobjekt, plattformobjekt, liste):
        """ Konstruktør """
        self.spillobjekt = spillobjekt
        self.plattformobjekt = plattformobjekt
        self.bredde = 60
        self.hoyde = 60
        self.x = random.randint(plattformobjekt.x + round(plattformobjekt.bredde / 2), plattformobjekt.x + plattformobjekt.bredde)
        self.y = plattformobjekt.y - self.hoyde
        self.boks = pygame.Rect(self.x, self.y, self.bredde, self.hoyde)
        self.hastighet_abs = 1 + spillobjekt.score.verdi / 2000
        self.hastighet = self.hastighet_abs
        self.bilder = []
        for n in range(11):
            self.bilder.append(pygame.transform.scale(pygame.image.load("bilder\\skurk"+str(n)+".png").convert_alpha(), (self.bredde, self.hoyde)))
        self.bilder_revers = []
        for bilde in self.bilder:
            self.bilder_revers.append(pygame.transform.flip(bilde,True,False))
        self.bildeliste = self.bilder
        self.bildenr = 0
        self.drept_lyd = pygame.mixer.Sound("lydfiler\\minecraft_scream.mp3")
        self.animasjon_tid = pygame.time.get_ticks()
        self.drept_tid = 0
        self.liste = liste

    def beveg(self):
        """ Metode for å bevege skurken """

        # Bevegelse i forhold til spilleren
        if (self.spillobjekt.taster[K_RIGHT] or self.spillobjekt.taster[K_d]) and self.spillobjekt.spiller.x >= self.spillobjekt.vindubredde / 2:
            self.x -= (self.hastighet + self.spillobjekt.spiller.hastighet_x)
        else: 
            self.x -= self.hastighet

        # Animer skurken
        if pygame.time.get_ticks() - self.animasjon_tid > 50:
                self.animasjon_tid = pygame.time.get_ticks()
                self.bildenr += 1
                if self.hastighet < 0: 
                    self.bildeliste = self.bilder
                else: 
                    self.bildeliste = self.bilder_revers
                if self.bildenr == len(self.bildeliste) - 1:
                    self.bildenr = 0
        
        # Snur farten på enden av plattformen
        if self.x < self.plattformobjekt.x: 
            self.hastighet = -self.hastighet_abs
        elif self.x > self.plattformobjekt.x + self.plattformobjekt.bredde - self.bredde:
                    self.hastighet = self.hastighet_abs

        # Fjerner skurken når den er utilgjengelig
        if self.x < -self.spillobjekt.vindubredde:
            self.liste.remove(self)
        self.boks.x = self.x

    def vis(self):
        """ Metode for å tegne skurken """

        # Sjekker om skurken er drept
        if self.drept_tid > 0:
            self.drept_lyd.play()
            self.hastighet = 0
            self.spillobjekt.vindu.blit(self.bildeliste[10], (self.x, self.y))
            if pygame.time.get_ticks() - self.drept_tid > 200:
                self.spillobjekt.score.verdi += 100
                self.liste.remove(self)
        
        # Tegner normalt hvis ikke
        else: 
            self.spillobjekt.vindu.blit(self.bildeliste[self.bildenr], (self.x, self.y))

# Definer Spill-klassen
class Spill():
    """ 
    Klasse for å lage spill-objekt 
    """

    def __init__(self):
        """ Konstruktør """

        # Starter opp Pygame
        pygame.init()
        pygame.display.set_caption("SUPER AIMARIO")
        pygame.mixer.init()
        pygame.mixer.music.load("lydfiler\\wii.mp3")

        # Lagrer variabler og oppretter elementer
        self.spill = False
        self.info = False
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
        for i in range (random.randint(5, 10)):
            self.skyer.append(Sky(self,random.randint(0, self.vindubredde)))
        plattform = Plattform(self, 0, self.vindubredde)
        self.plattformer.append(plattform)
        plattform.opprettElementer()


    def visStartvindu(self):
        """ Metode for å vise startvindu """   

        # Hent data fra csv-fil
        tid_verdier = []
        score_verdier = []
        with open("filer\\score.csv", encoding="utf-8-sig") as fil: 
            filinnhold = csv.reader(fil, delimiter=",")
            overskrifter = next(filinnhold)
            for rad in filinnhold: 
                tid_verdier.append(rad[0])
                score_verdier.append(int(rad[1]))
        score = score_verdier[-1]
        high_score = max(score_verdier)

        # Starter spill hvis SPACE
        if self.taster[K_SPACE]:
            pygame.mixer.music.play(-1)
            self.spill = True
        
        # Viser logg fra de siste spill hvis L
        elif self.taster[K_l]: 
            plt.figure("Logg over de 10 siste spillene")
            bars = plt.bar(tid_verdier[-10:], score_verdier[-10:])
            plt.bar_label(bars)
            plt.xlabel(overskrifter[0]+" i sekunder")
            plt.ylabel(overskrifter[1])
            plt.show()
    
        # Viser info vis I
        elif self.taster[K_i]:
            self.info = True

        # Opprett tekst
        tittel_font = pygame.font.Font("filer\\PressStart2P.ttf", 70)
        stor_font = pygame.font.Font("filer\\PressStart2P.ttf", 20)
        liten_font = pygame.font.Font("filer\\PressStart2P.ttf", 15)
        super_tekst = tittel_font.render("SUPER", True, (255, 255, 100))
        aimario_tekst = tittel_font.render("AIMARIO", True, (255, 255, 100))
        start_tekst = stor_font.render("Trykk SPACE for å starte", True, (255, 255, 255))
        high_score_tekst = liten_font.render("High score: "+str(high_score), True, (255, 255, 255))
        score_tekst = liten_font.render("Score: "+str(score), True, (255, 255, 255))
        logg_tekst = liten_font.render("Logg (Trykk L)", True, (255, 255, 255))
        info_tekst = liten_font.render("Info (Trykk I))", True, (255, 255, 255))

        # Opprett tekstboks 
        super_boks = super_tekst.get_rect(center=(self.vindubredde / 2, 100))
        aimario_boks = aimario_tekst.get_rect(center=(self.vindubredde / 2, 200))
        start_boks = start_tekst.get_rect(center=(self.vindubredde / 2, self.vinduhoyde / 2))
        high_score_boks = high_score_tekst.get_rect(center=(self.vindubredde / 2, 400))
        score_boks = score_tekst.get_rect(center=(self.vindubredde / 2, 450))
        logg_boks = logg_tekst.get_rect(center=(self.vindubredde / 2, 500))
        info_boks = info_tekst.get_rect(center=(self.vindubredde / 2, 550))

        # Tegn tekstboks på vinduet
        self.vindu.fill((100, 150, 200))
        self.vindu.blit(super_tekst, super_boks)
        self.vindu.blit(aimario_tekst, aimario_boks)
        self.vindu.blit(start_tekst, start_boks)
        self.vindu.blit(high_score_tekst, high_score_boks)
        self.vindu.blit(score_tekst, score_boks)
        self.vindu.blit(logg_tekst, logg_boks)
        self.vindu.blit(info_tekst, info_boks)

    def visInfo(self):
            
            # Lukker infovinduet hvis ESC
            if self.taster[K_ESCAPE]:
                self.info = False 
            
            # Opprett tekst
            font = pygame.font.Font("filer\\PressStart2P.ttf", 15)
            beveg_tekst = font.render("AD/piltaster og SPACE for å bevege", True, (255, 255, 255))
            dod_tekst = font.render("Ikke treff skurkene eller fall ned", True, (255, 255, 255))
            poeng_tekst = font.render("Land oppå skurkene for 100 poeng", True, (255, 255, 255))
            lyd_tekst = font.render("Husk å ha på lyd mens du spiller", True, (255, 255, 255))
            lukk_tekst = font.render("Trykk ESC for å lukke infovinduet", True, (255, 255, 255))

            # Opprett tekstboks 
            beveg_boks = beveg_tekst.get_rect(center=(self.vindubredde / 2, 100))
            dod_boks = dod_tekst.get_rect(center=(self.vindubredde / 2, 200))
            poeng_boks = poeng_tekst.get_rect(center=(self.vindubredde / 2, 300))
            lyd_boks = lyd_tekst.get_rect(center=(self.vindubredde / 2, 400))
            lukk_boks = lukk_tekst.get_rect(center=(self.vindubredde / 2, 500))

            # Tegn tekstboks på vinduet
            self.vindu.fill((100, 150, 200))
            self.vindu.blit(beveg_tekst, beveg_boks)
            self.vindu.blit(dod_tekst, dod_boks)
            self.vindu.blit(poeng_tekst, poeng_boks)
            self.vindu.blit(lyd_tekst, lyd_boks)
            self.vindu.blit(lukk_tekst, lukk_boks)

    def opprettElementer(self):
        """ Metode for å opprette nye elementer når spilleren beveger seg """
        if (self.taster[K_RIGHT] or self.taster[K_d]) and self.spiller.x >= self.vindubredde / 2:
                if random.randint(1, 20) == 1:
                    self.skyer.append(Sky(self, self.vindubredde))
                if self.vindubredde - (self.plattformer[-1].x + self.plattformer[-1].bredde) > 130:
                    plattform = Plattform(self, self.vindubredde, random.randint(100, 1000))
                    self.plattformer.append(plattform)
                    plattform.opprettElementer()
                self.score.verdi += 1/10

    def kjorRunde(self):
        """ Metode for å kjøre runden """

        # Oppdater spiller og miljø
        self.tid.verdi = round((pygame.time.get_ticks() - self.starttid) / 1000)
        self.spiller.beveg()
        for skurk in self.skurker:
            skurk.beveg()
        for sky in self.skyer:
            sky.beveg()
        for busk in self.busker:
            busk.beveg()
        for plattform in self.plattformer: 
            plattform.beveg()
        self.opprettElementer()

        # Tegn spiller og miljø
        self.vindu.fill((100, 150, 200))
        self.score.vis()
        self.spiller.liv.vis()
        self.tid.vis()
        for sky in self.skyer:
            sky.vis()
        for busk in self.busker:
            busk.vis()
        for plattform in self.plattformer: 
            plattform.vis()
        for skurk in self.skurker: 
            skurk.vis()
        self.spiller.vis()
    
    def spillLokke(self):
        """ Metode for å kjøre spillet """

        # Start hovedløkke
        while True:

            # Avslutter hvis vinduet lukkes
            for hendelse in pygame.event.get():
                if hendelse.type == pygame.QUIT:
                        pygame.quit()
                        exit()
            
            # Sjekker om spilleren har startet spillet
            self.taster = pygame.key.get_pressed()
            if self.spill:
                self.kjorRunde()
            elif self.info: 
                    self.visInfo()
            else:
                    self.visStartvindu()

            # Oppdater vindu og begrens hastighet
            pygame.display.flip()
            self.klokke.tick(60) 

# Kjør spillet
Spill().spillLokke()

