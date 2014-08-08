
import os, pygame, inputbox
from pygame.locals import *
import random, operator, math 

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

class Fist(pygame.sprite.Sprite):
    """moves a clenched fist on the screen, following the mouse"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('fist.bmp', -1)
        self.punching = 0
        self.distance = (0,0)
        self.key_movement = (0,0)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.boundary=0

    def update(self):
        "move the fist based on the mouse position"
        #print self.distance
        pos  = tuple(map(operator.add, self.rect.midtop, self.key_movement))
        if( self.area.left<=pos[0]<=self.area.right and self.area.top<=pos[1]<=self.area.bottom-10 ):
            self.rect.midtop = pos
            self.boundary=0
        else:
            self.boundary=1
            #print "boundary"
        if self.punching:
            self.rect.move_ip(1, 1)

    def punch(self,target):
        "returns true if the fist collides with the target"
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unpunch(self):
        "called to pull the fist back"
        self.punching = 0


class Chimp(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('chimp.bmp', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 100, 100
        self.display = 0
        self.move_x = 0
        self.move_y = 0

    def update(self):
        if self.display:
            self._spin()

    def _walk(self):
        self.move_x = random.randint(0,640)
        self.move_y = random.randint(0,480)
        newpos = self.rect.move(self.move_x-self.rect.left, self.move_y-self.rect.top)        
        self.rect = newpos


    def _spin(self):
        self.display = self.display + 6
        if self.display >= 360:
            self.display = 0
            self._walk()

    def punched(self):
        if not self.display:
            self.display = 1

def delay(n):
    clock = pygame.time.Clock()
    i=0
    while(i<n):
        i=i+1
        clock.tick(1)


def main():
#Initialize Everything
    screen_width = 640
    screen_height = 480
    pygame.init()
    screen = pygame.display.set_mode((screen_width,screen_height),FULLSCREEN)
    pygame.display.set_caption('M')
    pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250,130,130))

    misses = 0
    score = 0
    score_text="Score: "+str(score)

#Display The Background

#Prepare Game Objects
    clock = pygame.time.Clock()
    whiff_sound = load_sound('whiff.wav')
    whiff_sound.set_volume(1.0)
    punch_sound = load_sound('punch.wav')
    punch_sound.set_volume(1.0)
    punchr_sound = load_sound('bonus.wav')
    punchr_sound.set_volume(1.0)
    punchw_sound = load_sound('punch.wav')
    punchw_sound.set_volume(1.0)
    gameover = load_sound('gameover.wav')
    instructions = load_sound('instruction.wav')
    #instructions.play()
    start_sound = load_sound('start.wav')
    start_sound.play()
    screen.fill((250,130,130));
    main_text = "Highscore :"
    fo = open("highscore.txt", "r+")
    for line in fo:
        main_text = main_text + line;        
    fo.close()
    main_text = main_text.replace('\t',' ')
    font = pygame.font.SysFont("None", 50)
    text = font.render(main_text, 1, (10, 10, 10))
    textpos = text.get_rect(centerx=background.get_width()/2)
    screen.blit(text,textpos)
    pygame.display.flip()
    delay(3.5)
    flag=1
    while(flag):
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_1:
                instructions.play()
                delay(23.5)
                start_sound.play()
                delay(3.5)
            elif event.type == KEYDOWN and event.key == K_2:
                flag=0
                break
    animal = random.randint(1,4)
    animal_sound1 = load_sound('crow.wav')
    animal_sound3 = load_sound('cat_meow_x.wav')
    animal_sound4 = load_sound('dog_bark6.wav')
    animal_sound2 = load_sound('chicken.wav')

    ontarget_sound = load_sound('beep-07.wav')
    ontarget_sound.set_volume(0.04)
    boundary_sound = load_sound('boundary.wav')
    boundary_sound.set_volume(1.0)
    highscore_sound = load_sound('highscore.wav')
    highscore_sound.set_volume(1.0)
    lastchance_sound = load_sound('lastchance.wav')
    lastchance_sound.set_volume(1.0)
    volume = 0.1
    chimp = Chimp()
    fist = Fist()
    allsprites = pygame.sprite.RenderPlain((fist, chimp))
    fistsprite = pygame.sprite.RenderPlain(fist)
    chimpsprite = pygame.sprite.RenderPlain(chimp)
    animal_sound = {}
    animal_sound[1] = animal_sound1
    animal_sound[2] = animal_sound2
    animal_sound[3] = animal_sound3
    animal_sound[4] = animal_sound4
    animal_sound[animal].set_volume(volume)
    channel1 = animal_sound[animal].play(-1)

#Main Loop
    #channel1 = animal_sound.play(-1) #punch
    while misses<3:
        clock.tick(60)
        #print score
        fist.distance = tuple(map(operator.sub,chimp.rect.midtop,fist.rect.midtop))
        fist.key_movement = (0,0)
        key_states = pygame.key.get_pressed()
        if key_states[K_LEFT]:
            #print "left"
            fist.key_movement = tuple(map(operator.add,fist.key_movement,[-1,0]))
        if key_states[K_RIGHT]:
            #print "right"
            fist.key_movement = tuple(map(operator.add,fist.key_movement,[1,0]))
        if key_states[K_UP]:
            #print "up"
            fist.key_movement = tuple(map(operator.add,fist.key_movement,[0,-1]))
        if key_states[K_DOWN]:
            #print "down"
            fist.key_movement = tuple(map(operator.add,fist.key_movement,[0,1]))
    #Handle Input Events
        if(math.sqrt( math.pow(fist.distance[0],2)+math.pow(fist.distance[1],2))*4 / math.sqrt(math.pow(640,2)+math.pow(480,2)) < 1.0):
            volume = 0.8*(1.0-(math.sqrt( math.pow(fist.distance[0],2)+math.pow(fist.distance[1],2))*4 / math.sqrt(math.pow(640,2)+math.pow(480,2)) ))
            hitbox = fist.rect.inflate(-5, -5)
            #if(hitbox.colliderect(chimp.rect)):
             #   ontarget_sound.play()
            animal_sound[animal].set_volume(volume)
        else:
            #print "outside the circle"
            animal_sound[animal].set_volume(0.0)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif (event.type == KEYDOWN and (event.key == K_a or event.key == K_b or event.key == K_c or event.key == K_d)):
                if fist.punch(chimp):
                    score += 10
                    if(animal == ord(pygame.key.name(event.key))-96):
                        score += 5
                    else:
                        print "wrong choice"
                    score_text = "Score: "+str(score)
                    #channel1.pause()
                    if(animal == ord(pygame.key.name(event.key))-96):
                        channel3 = punchr_sound.play()
                    else:
                        channel3 = punchw_sound.play()
                    #channel1.unpause()
                    background.fill((255,130,130))
                    chimp.punched()
                    channel1.stop()
                    animal = random.randint(1,4)
                    animal_sound[animal].set_volume(0)
                    channel1 = animal_sound[animal].play(-1)
                else:
                    #channel1.pause()
                    misses += 1
                    whiff_sound.play() #miss
                    delay(0.5)
                    if(misses==2):
                        lastchance_sound.play()
                    #channel1.unpause() #punch
            elif event.type is KEYUP and (event.key == K_a or event.key == K_b or event.key == K_c or event.key == K_d):
                fist.unpunch()
        if(hitbox.colliderect(chimp.rect)):
            ontarget_sound.play()
        if(fist.boundary):
            boundary_sound.play()
        allsprites.update()
    #Draw Everything
        if pygame.font:
            font = pygame.font.SysFont("None", 20)
            text = font.render(score_text, 1, (10, 10, 10))
            textpos = text.get_rect(centerx=7*background.get_width()/8)
            screen.fill((250,130,130))
            screen.blit(text, textpos)
        #screen.blit(background, (0, 0))
        fistsprite.draw(screen)
        if chimp.display:
            chimpsprite.draw(screen)
        #allsprites.draw(screen)
        #pygame.sprite.RenderPlain(fist).draw(screen)
#        fist.draw(screen)
        pygame.display.flip()
    print "3 misses"
    gameover.play()
    delay(2)
#    pygame.mixer.music.load('data\\a_menu.wav')
#    pygame.mixer.music.queue('data\\b_menu.wav')
#    pygame.mixer.music.queue('data\crow_menu.wav')
#    pygame.mixer.music.play()

#    channel2.queue(b_menu)
#    channel2.queue(c_menu)
#    channel2.queue(d_menu)
    #c_menu.play()
    #d_menu.play()
    fo = open("highscore.txt", "r+")
    for line in fo:
        a = line.split('\t')
        a = a[1]
        a = int(a)
    fo.close()
    if(score>a):
        highscore_sound.play()
        delay(3)
        fo = open("highscore.txt",'w')
        answer = inputbox.ask(screen, "Your name")
        fo.write(answer+'\t'+str(score))
        fo.close()
    screen.fill((250,130,130));
    score_text = "Game Over"
    font = pygame.font.SysFont("None", 100)
    text = font.render(score_text, 1, (10, 10, 10))
    textpos = text.get_rect(centerx=background.get_width()/2)
    screen.blit(text,textpos)
    pygame.display.flip()

    pygame.quit()
#Game Over
if __name__ == '__main__': main()
